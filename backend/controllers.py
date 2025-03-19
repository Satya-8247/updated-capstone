from flask import jsonify, request
from models import db, Doctor, Patient, Appointment
from werkzeug.security import generate_password_hash, check_password_hash

class AuthController:
    @staticmethod
    def signup_doctor():
        data = request.get_json()
        required_fields = ['name', 'email', 'specialization', 'time_slots', 'password']
        if not all(data.get(field) for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        hashed_password = generate_password_hash(data['password'])
        try:
            new_doctor = Doctor(
                name=data['name'],
                email=data['email'],
                specialization=data['specialization'],
                available_time=str(data['time_slots']),
                password=hashed_password
            )
            db.session.add(new_doctor)
            db.session.commit()
            return jsonify({"message": "Doctor registered successfully"}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

    @staticmethod
    def signin_doctor():
        data = request.get_json()
        doctor = Doctor.query.filter_by(email=data.get('email')).first()
        if not doctor or not check_password_hash(doctor.password, data.get('password')):
            return jsonify({"error": "Invalid email or password"}), 401
        return jsonify({"message": f"Welcome {doctor.name}", "doctor_id": doctor.id}), 200

    @staticmethod
    def signup_patient():
        data = request.get_json()
        required_fields = ['name', 'email', 'password']
        if not all(data.get(field) for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        hashed_password = generate_password_hash(data['password'])
        try:
            new_patient = Patient(
                name=data['name'],
                email=data['email'],
                password=hashed_password
            )
            db.session.add(new_patient)
            db.session.commit()
            return jsonify({"message": "Patient registered successfully"}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

    @staticmethod
    def signin_patient():
        data = request.get_json()
        patient = Patient.query.filter_by(email=data.get('email')).first()
        if not patient or not check_password_hash(patient.password, data.get('password')):
            return jsonify({"error": "Invalid email or password"}), 401
        return jsonify({"message": f"Welcome {patient.name}", "patient_name": patient.name}), 200
    
    @staticmethod
    def patient_password():
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

class AppointmentController:
    @staticmethod
    def book_appointment():
        data = request.get_json()
        required_fields = ["patient_name", "doctor_id", "time_slot"]
        if not all(data.get(field) for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        try:
            new_appointment = Appointment(
                patient_name=data["patient_name"],
                doctor_id=data["doctor_id"],
                appointment_time=data["time_slot"],
                status="Scheduled"
            )
            db.session.add(new_appointment)
            db.session.commit()
            return jsonify({"message": "Appointment booked successfully"}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

    @staticmethod
    def cancel_appointment(appointment_id):
        appointment = Appointment.query.get(appointment_id)
        if not appointment:
            return jsonify({"error": "Appointment not found"}), 404
        try:
            db.session.delete(appointment)
            db.session.commit()
            return jsonify({"message": "Appointment canceled successfully"}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

    @staticmethod
    def get_patient_appointments(patient_name):
        try:
            appointments = Appointment.query.filter_by(patient_name=patient_name).all()
            appointment_list = [{
                "id": appt.id,
                "patient_name": appt.patient_name,
                "doctor": appt.doctor.name if appt.doctor else "Unknown Doctor",
                "time_slot": appt.appointment_time,
                "status": appt.status
            } for appt in appointments]
            return jsonify({"appointments": appointment_list}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @staticmethod
    def modify_appointment(appointment_id):
        data = request.get_json()
        new_time_slot = data.get("new_time_slot")
        if not new_time_slot:
            return jsonify({"error": "New time slot is required"}), 400

        appointment = Appointment.query.get(appointment_id)
        if not appointment:
            return jsonify({"error": "Appointment not found"}), 404

        try:
            appointment.appointment_time = new_time_slot
            db.session.commit()
            return jsonify({"message": "Appointment updated successfully"}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

class DoctorController:
    @staticmethod
    def get_available_doctors():
        try:
            doctors = Doctor.query.all()
            doctor_list = [{
                "id": doc.id,
                "name": doc.name,
                "time_slots": doc.available_time,
                "specialization": doc.specialization
            } for doc in doctors]
            return jsonify({"doctors": doctor_list}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @staticmethod
    def get_doctor(doctor_id):
        doctor = Doctor.query.get(doctor_id)
        if not doctor:
            return jsonify({'error': 'Doctor not found'}), 404
        try:
            return jsonify({
                'id': doctor.id,
                'name': doctor.name,
                'specialization': doctor.specialization,
                'available_time': doctor.available_time
            }), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @staticmethod
    def get_doctor_patients(doctor_id):
        doctor = Doctor.query.get(doctor_id)
        if not doctor:
            return jsonify({"error": "Doctor not found"}), 404

        try:
            appointments = Appointment.query.filter_by(doctor_id=doctor_id).all()
            patient_list = [{
                "appointment_id": appt.id,
                "patient_name": appt.patient_name,
                "appointment_time": appt.appointment_time,
                "status": appt.status
            } for appt in appointments]
            return jsonify({"doctor": doctor.name, "patients": patient_list}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500