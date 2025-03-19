import pytest
from app import app, db, Doctor, Patient, Appointment
from werkzeug.security import generate_password_hash

@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:" 
    with app.test_client() as client:
        with app.app_context():
            db.create_all()  
        yield client
        with app.app_context():
            db.session.remove()
            db.drop_all() 

def test_welcome(client):
    """Test the welcome route."""
    response = client.get("/")
    assert response.status_code == 200
    assert b"Welcome to Appointment Booking with Doctor" in response.data

def test_doctor_signup(client):
    """Doctor signup route."""
    doctor_data = {
        "name": "Dr. Smith",
        "email": "drsmith@example.com",
        "specialization": "Cardiology",
        "time_slots": "9 AM - 5 PM",
        "password": "securepass"
    }
    response = client.post("/doctor/signup", json=doctor_data)
    assert response.status_code == 201
    assert b"Doctor registered successfully" in response.data

def test_doctor_signin(client):
    """Doctor sign-in route."""
    hashed_password = generate_password_hash("securepass")
    with app.app_context():
        new_doctor = Doctor(name="Dr. Smith", email="drsmith@example.com", specialization="Cardiology",
                            available_time="9 AM - 5 PM", password=hashed_password)
        db.session.add(new_doctor)
        db.session.commit()

    response = client.post("/doctor/signin", json={"email": "drsmith@example.com", "password": "securepass"})
    assert response.status_code == 200
    assert b"Welcome Dr. Smith" in response.data

def test_patient_signup(client):
    """Patient signup route."""
    patient_data = {
        "name": "John Doe",
        "email": "johndoe@example.com",
        "password": "mypassword"
    }
    response = client.post("/patient/signup", json=patient_data)
    assert response.status_code == 201
    assert b"Patient registered successfully" in response.data

def test_patient_signin(client):
    """Patient sign-in route."""
    hashed_password = generate_password_hash("mypassword")
    with app.app_context():
        new_patient = Patient(name="John Doe", email="johndoe@example.com", password=hashed_password)
        db.session.add(new_patient)
        db.session.commit()

    response = client.post("/patient/signin", json={"email": "johndoe@example.com", "password": "mypassword"})
    assert response.status_code == 200
    assert b"Welcome John Doe" in response.data

def test_book_appointment(client):
    """Booking an appointment."""
    with app.app_context():
        doctor = Doctor(name="Dr. Adams", email="dradams@example.com", specialization="Dermatology",
                        available_time="10 AM - 4 PM", password=generate_password_hash("testpass"))
        db.session.add(doctor)
        db.session.commit()

    appointment_data = {
        "patient_name": "John Doe",
        "doctor_id": 1,
        "time_slot": "11 AM"
    }
    response = client.post("/appointments/book", json=appointment_data)
    assert response.status_code == 201
    assert b"Appointment booked successfully" in response.data

def test_get_appointments(client):
    """Retrieving a patient's appointments."""
    with app.app_context():
        doctor = Doctor(name="Dr. Adams", email="dradams@example.com", specialization="Dermatology",
                        available_time="10 AM - 4 PM", password=generate_password_hash("testpass"))
        db.session.add(doctor)
        db.session.commit()
        appointment = Appointment(patient_name="John Doe", doctor_id=1, appointment_time="11 AM")
        db.session.add(appointment)
        db.session.commit()

    response = client.get("/appointments/John Doe")
    assert response.status_code == 200
    assert b"John Doe" in response.data
    assert b"11 AM" in response.data

def test_cancel_appointment(client):
    """Cancel an appointment."""
    with app.app_context():
        doctor = Doctor(name="Dr. Adams", email="dradams@example.com", specialization="Dermatology",
                        available_time="10 AM - 4 PM", password=generate_password_hash("testpass"))
        db.session.add(doctor)
       
