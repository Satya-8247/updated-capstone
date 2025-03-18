document.addEventListener("DOMContentLoaded", function () {
    loadDoctors();
    loadUserAppointments();

    document.getElementById("appointmentForm").addEventListener("submit", function (event) {
        event.preventDefault();
        bookAppointment();
    });
});

// API Base URL (Replace with actual backend URL)
const API_BASE_URL = "http://127.0.0.1:8000";

// Fetch and Display Doctors
function loadDoctors() {
    fetch(${API_BASE_URL}/doctors)
        .then(response => response.json())
        .then(doctors => {
            const doctorList = document.querySelector(".doctor-list");
            const doctorSelect = document.getElementById("doctor");

            doctorList.innerHTML = "";
            doctorSelect.innerHTML = "<option value=''>Select a Doctor</option>";

            doctors.forEach(doctor => {
                // Create Doctor Card
                const doctorCard = document.createElement("div");
                doctorCard.classList.add("doctor-card");
                doctorCard.innerHTML = `
                    <img src="assets/doctor_placeholder.png" alt="Doctor">
                    <h3>${doctor.name}</h3>
                    <p>Specialty: ${doctor.specialty}</p>
                    <p>Rating: ⭐ ${doctor.average_rating}</p>
                `;
                doctorList.appendChild(doctorCard);

                // Add Doctor to Dropdown
                const option = document.createElement("option");
                option.value = doctor.id;
                option.textContent = doctor.name;
                doctorSelect.appendChild(option);
            });
        })
        .catch(error => console.error("Error fetching doctors:", error));
}

// Book an Appointment
function bookAppointment() {
    const doctorId = document.getElementById("doctor").value;
    const date = document.getElementById("date").value;
    const time = document.getElementById("time").value;

    if (!doctorId || !date || !time) {
        alert("Please fill in all fields.");
        return;
    }

    const appointmentData = {
        user_id: 1, // Hardcoded for now (Replace with actual logged-in user ID)
        doctor_id: parseInt(doctorId),
        appointment_time: ${date}T${time}:00Z
    };

    fetch(${API_BASE_URL}/appointments, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(appointmentData)
    })
        .then(response => response.json())
        .then(data => {
            alert("Appointment booked successfully!");
            loadUserAppointments();
        })
        .catch(error => console.error("Error booking appointment:", error));
}

// Fetch and Display User Appointments
function loadUserAppointments() {
    fetch(${API_BASE_URL}/appointments/user/1) // Hardcoded user ID
        .then(response => response.json())
        .then(appointments => {
            const appointmentList = document.querySelector(".appointment-list");
            appointmentList.innerHTML = "";

            if (appointments.length === 0) {
                appointmentList.innerHTML = "<p>No appointments booked yet.</p>";
                return;
            }

            appointments.forEach(appointment => {
                const appointmentCard = document.createElement("div");
                appointmentCard.classList.add("appointment-card");
                appointmentCard.innerHTML = `
                    <h3>${appointment.doctor_name}</h3>
                    <p>Date: ${appointment.appointment_time.split("T")[0]}</p>
                    <p>Time: ${appointment.appointment_time.split("T")[1].slice(0, 5)}</p>
                    <button onclick="cancelAppointment(${appointment.id})">Cancel</button>
                `;
                appointmentList.appendChild(appointmentCard);
            });
        })
        .catch(error => console.error("Error fetching appointments:", error));
}

// Cancel an Appointment
function cancelAppointment(appointmentId) {
    if (!confirm("Are you sure you want to cancel this appointment?")) return;

    fetch(${API_BASE_URL}/appointments/${appointmentId}, {
        method: "DELETE"
    })
        .then(response => response.json())
        .then(data => {
            alert("Appointment canceled successfully.");
            loadUserAppointments();
        })
        .catch(error => console.error("Error canceling appointment:", error));
}