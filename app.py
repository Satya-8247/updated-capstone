from flask import Flask, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS  # Import CORS

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
class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)  # New password field

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    patient_name = db.Column(db.String(100), nullable=False)
    appointment_time = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(50), default="Booked")

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
    hashed_password = generate_password_hash(password)

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

    patient = Patient.query.filter_by(email=email).first()

    if not patient or not check_password_hash(patient.password, password):
        return jsonify({"error": "Invalid email or password"}), 401

    return jsonify({"message": f"Welcome {patient.name}", "patient_name": patient.name}), 200



@app.route('/appointments/book', methods=['POST'])
def book_appointment():
    data = request.get_json()
    patient_name = data.get("patient_name")
    doctor_id = data.get("doctor_id")
    time_slot = data.get("time_slot")

    new_appointment = Appointment(patient_name=patient_name, doctor_id=doctor_id, appointment_time=time_slot, status="Scheduled")
    db.session.add(new_appointment)
    db.session.commit()

    return jsonify({"message": "Appointment booked successfully"}), 201


@app.route('/appointments/cancel/<int:appointment_id>', methods=['DELETE'])
def cancel_appointment(appointment_id):
    appointment = Appointment.query.get(appointment_id)
    if not appointment:
        return jsonify({"error": "Appointment not found"}), 404

    db.session.delete(appointment)
    db.session.commit()

    return jsonify({"message": "Appointment canceled successfully"}), 200



@app.route('/appointments/<string:patient_name>', methods=['GET'])
def get_patient_appointments(patient_name):
    # Correct the query to fetch from Appointment model
    appointments = Appointment.query.filter_by(patient_name=patient_name).all() 

    # Build the list of appointments with doctor details
    appointment_list = [{
        "id": appt.id,
        "doctor": appt.doctor.name if appt.doctor else "Unknown Doctor",  # Doctor's name
        "time_slot": appt.appointment_time,  # Appointment time
        "status": appt.status  # Appointment status
    } for appt in appointments]

    return jsonify({"appointments": appointment_list}), 200



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
    doctor_list = [{"id": doc.id, "name": doc.name,"time_slots":doc.available_time} for doc in doctors]

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
        "appointment_time": appt.appointment_time,
        "status": appt.status
    } for appt in appointments]

    return jsonify({"doctor": doctor.name, "patients": patient_list}), 200



if __name__ == '__main__':
    app.run(debug=True)
