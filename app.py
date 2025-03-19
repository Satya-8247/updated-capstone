from flask import Flask, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS  # Import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)
# SQLAlchemy configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:admin123@localhost/doctor_apointment'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Doctor Model with Password
class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    specialization = db.Column(db.String(50), nullable=False)
    available_time = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    appointments = db.relationship('Appointment', backref='doctor', lazy=True) 

# Patient Model with Password
# Patient Model with Password
class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

# Appointment Model with Date
class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_name = db.Column(db.String(100), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)  # Foreign Key reference to Doctor
    time_slot = db.Column(db.String(50), nullable=False)
    date = db.Column(db.Date, nullable=False)


@app.route('/')
def welcome():
    return jsonify({"message": "Welcome to Appointment Booking with Doctor"})

# Sign Up Doctor Route (with password hashing)
@app.route('/doctor/signup', methods=['POST'])
def signup_doctor():
    doctor_data = request.get_json()
    name = doctor_data.get('name')
    email = doctor_data.get('email')
    specialization = doctor_data.get('specialization')
    time_slots = doctor_data.get('time_slots')
    password = doctor_data.get('password')

    if not name or not email or not specialization or not time_slots or not password:
        return jsonify({"error": "Missing required fields"}), 400

    # Hash the password
    hashed_password = generate_password_hash(password)

    try:
        # Insert the doctor data into the database
        new_doctor = Doctor(name=name, email=email, specialization=specialization, available_time=str(time_slots), password=hashed_password)
        db.session.add(new_doctor)
        db.session.commit()

        return jsonify({"message": "Doctor registered successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# Sign In Doctor Route (with password validation)
@app.route('/doctor/signin', methods=['POST'])
def signin_doctor():
    doctor_data = request.get_json()
    email = doctor_data.get('email')
    password = doctor_data.get('password')

    doctor = Doctor.query.filter_by(email=email).first()

    if not doctor or not check_password_hash(doctor.password, password):
        return jsonify({"error": "Invalid email or password"}), 401

    return jsonify({"message": f"Welcome {doctor.name}", "doctor_id": doctor.id}), 200

# Sign Up Patient Route (with password hashing)
@app.route('/patient/signup', methods=['POST'])
def signup_patient():
    patient_data = request.get_json()
    name = patient_data.get('name')
    email = patient_data.get('email')
    password = patient_data.get('password')

    if not name or not email or not password:
        return jsonify({"error": "Missing required fields"}), 400

    # Hash the password
    hashed_password = generate_password_hash(str(password))

    try:
        # Insert the patient data into the database
        new_patient = Patient(name=name, email=email, password=hashed_password)
        db.session.add(new_patient)
        db.session.commit()

        return jsonify({"message": "Patient registered successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500



# Sign In Patient Route (with password validation)
@app.route('/patient/signin', methods=['POST'])
def signin_patient():
    patient_data = request.get_json()
    email = patient_data.get("email")
    password = patient_data.get("password")
    password = str(password)
    patient = Patient.query.filter_by(email=email).first()

    if not patient or not check_password_hash(patient.password, password):
        return jsonify({"error": "Invalid email or password"}), 401

    return jsonify({"message": f"Welcome {patient.name}", "patient_name": patient.name}), 200


@app.route('/appointments/book', methods=['POST'])
def book_appointment():
    data = request.json
    patient_name = data.get('patient_name')
    doctor_id = data.get('doctor_id')
    time_slot = data.get('time_slot')
    date_str = data.get('date')

    if not patient_name or not doctor_id or not time_slot or not date_str:
        return jsonify({"error": "Missing required fields"}), 400

    # Convert string date to date object
    try:
        appointment_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"error": "Invalid date format"}), 400

    new_appointment = Appointment(
        patient_name=patient_name,
        doctor_id=doctor_id,
        time_slot=time_slot,
        date=appointment_date
    )

    db.session.add(new_appointment)
    db.session.commit()

    return jsonify({"message": "Appointment booked successfully"})



@app.route('/appointments/cancel/<int:appointment_id>', methods=['DELETE'])
def cancel_appointment(appointment_id):
    appointment = Appointment.query.get(appointment_id)
    if not appointment:
        return jsonify({"error": "Appointment not found"}), 404

    db.session.delete(appointment)
    db.session.commit()

    return jsonify({"message": "Appointment canceled successfully"}), 200


from datetime import datetime

@app.route('/appointments/<patient_name>', methods=['GET'])
def get_appointments(patient_name):
    patient = Patient.query.filter_by(name=patient_name).first()

    if not patient:
        return jsonify({'message': 'Patient not found'}), 404

    appointments = Appointment.query.join(Doctor).filter(Appointment.patient_name == patient_name).all()
    appointment_data = []
    for appointment in appointments:
      
        # Format the date field as a string
        formatted_date = appointment.date.strftime("%Y-%m-%d")  # Change format as needed

        appointment_data.append({
            'id': appointment.id,
            'doctor': appointment.doctor.name,
            'specialization': appointment.doctor.specialization,
            'time_slot': appointment.time_slot,
            'date': formatted_date  # Use the formatted date here
        })

    return jsonify({'appointments': appointment_data})




@app.route('/appointments/modify/<int:appointment_id>', methods=['PUT'])
def modify_appointment(appointment_id):
    data = request.get_json()
    new_time_slot = data.get("new_time_slot")

    appointment = Appointment.query.get(appointment_id)
    if not appointment:
        return jsonify({"error": "Appointment not found"}), 404

    appointment.appointment_time = new_time_slot
    db.session.commit()

    return jsonify({"message": "Appointment updated successfully"}), 200



@app.route('/doctors/available', methods=['GET'])
def get_available_doctors():
    doctors = Doctor.query.all()
    doctor_list = [{"id": doc.id, "name": doc.name,"time_slots":doc.available_time,"specialization":doc.specialization} for doc in doctors]

    return jsonify({"doctors": doctor_list}), 200


@app.route('/doctor/<int:doctor_id>', methods=['GET'])
def get_doctor(doctor_id):
    doctor = Doctor.query.get(doctor_id)
    if not doctor:
        return jsonify({'error': 'Doctor not found'}), 404
    return jsonify({
        'id': doctor.id,
        'name': doctor.name,
        'specialization': doctor.specialization,
        'available_time': doctor.available_time
    })


@app.route('/doctor/<int:doctor_id>/patients', methods=['GET'])
def get_doctor_patients(doctor_id):
    doctor = Doctor.query.get(doctor_id)
    if not doctor:
        return jsonify({"error": "Doctor not found"}), 404

    appointments = Appointment.query.filter_by(doctor_id=doctor_id).all()

    patient_list = [{
        "appointment_id": appt.id,
        "patient_name": appt.patient_name, 
        "appointment_time": appt.time_slot, 
        "appointment_date":appt.date.strftime("%Y-%m-%d") , # Change format as needed
        "status": "Booked"
    } for appt in appointments]

    return jsonify({"doctor": doctor.name, "patients": patient_list}), 200

@app.route('/patient/forgot_password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    email = data.get("email")
    new_password = data.get("new_password")

    patient = Patient.query.filter_by(email=email).first()
    if not patient:
        return jsonify({"error": "Patient not found"}), 404

    # Hash and update the new password
    hashed_password = generate_password_hash(new_password)
    patient.password = hashed_password
    db.session.commit()

    return jsonify({"message": "Password updated successfully"}), 200

from datetime import datetime
@app.route('/doctor/<doctor_id>/available_slots', methods=['GET'])
def get_available_slots(doctor_id):
    # Get all the time slots from the doctor
    doctor = Doctor.query.get(doctor_id)
    all_time_slots = doctor.available_time  # Assuming available slots are stored as a comma-separated string
    
    # Check if there is a comma in the string, if so, split it, else treat as one time slot
    if ',' in all_time_slots: 
        all_time_slots = all_time_slots.split(',')  # Split into individual slots
    else:
        all_time_slots = [all_time_slots]  # If no comma, it's a single time slot
    
    print(all_time_slots)
    
    # Return all time slots without filtering
    return jsonify({"available_slots": all_time_slots})


@app.route('/appointments/<int:appointment_id>/update', methods=['PUT'])
def update_appointment(appointment_id):
    data = request.get_json()
    new_time_slot = data.get('time_slot')

    appointment = Appointment.query.get(appointment_id)
    if appointment:
        appointment.time_slot = new_time_slot
        db.session.commit()
        return jsonify({"message": "Appointment updated successfully."}), 200
    return jsonify({"message": "Appointment not found."}), 404

@app.route('/appointment/<int:appointment_id>', methods=['GET'])
def get_appointment(appointment_id):
    try:
        # Fetch the appointment from the database using the appointmentId
        appointment = Appointment.query.filter_by(id=appointment_id).first()

        if not appointment:
            return jsonify({"message": "Appointment not found"}), 404
        print(appointment.doctor_id)
        # Respond with the appointment details, including doctor_id
        return jsonify({
    
            "doctor_id": appointment.doctor_id,

        })
    except Exception as e:
        return jsonify({"message": "Server error", "error": str(e)}), 500



if __name__ == '__main__':
    app.run(debug=True)
