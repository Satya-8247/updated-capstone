from flask import Flask, jsonify
from flask_cors import CORS
from models import db
from controllers import AuthController, AppointmentController, DoctorController

app = Flask(__name__)
CORS(app)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:admin123@localhost/doctor_apointment'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Welcome route
@app.route('/')
def welcome():
    return jsonify({"message": "Welcome to Appointment Booking with Doctor"})

# Auth routes
@app.route('/doctor/signup', methods=['POST'])
def doctor_signup():
    return AuthController.signup_doctor()

@app.route('/doctor/signin', methods=['POST'])
def doctor_signin():
    return AuthController.signin_doctor()

@app.route('/patient/signup', methods=['POST'])
def patient_signup():
    return AuthController.signup_patient()

@app.route('/patient/signin', methods=['POST'])
def patient_signin():
    return AuthController.signin_patient()

@app.route('/patient/forgot_password', methods=['POST'])
def patient_password():
    return AuthController.patient_password()

# Appointment routes
@app.route('/appointments/book', methods=['POST'])
def book_appointment():
    return AppointmentController.book_appointment()

@app.route('/appointments/cancel/<int:appointment_id>', methods=['DELETE'])
def cancel_appointment(appointment_id):
    return AppointmentController.cancel_appointment(appointment_id)

@app.route('/appointments/<string:patient_name>', methods=['GET'])
def get_patient_appointments(patient_name):
    return AppointmentController.get_patient_appointments(patient_name)

@app.route('/appointments/modify/<int:appointment_id>', methods=['PUT'])
def modify_appointment(appointment_id):
    return AppointmentController.modify_appointment(appointment_id)

# Doctor routes
@app.route('/doctors/available', methods=['GET'])
def get_available_doctors():
    return DoctorController.get_available_doctors()

@app.route('/doctor/<int:doctor_id>', methods=['GET'])
def get_doctor(doctor_id):
    return DoctorController.get_doctor(doctor_id)

@app.route('/doctor/<int:doctor_id>/patients', methods=['GET'])
def get_doctor_patients(doctor_id):
    return DoctorController.get_doctor_patients(doctor_id)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)