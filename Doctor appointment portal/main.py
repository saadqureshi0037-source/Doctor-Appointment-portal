# main.py

import streamlit as st
from database import init_db
from auth import register_user, login_user
from doctor_ui import doctor_dashboard
from patient_ui import patient_dashboard
from admin_ui import admin_dashboard
from sample_data import insert_samples
import os
# Load custom CSS
with open("styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
st.markdown("""
<div class='main-header'>
    <h1>🩺 Doctor Appointment Portal</h1>
    <p>Your personalized online health scheduling system</p>
</div>
""", unsafe_allow_html=True)
 
st.set_page_config(page_title="Doctor Appointment Portal", layout="wide")
st.title("🩺 Doctor Appointment Portal")

# --- Initialize database and sample data ---
init_db()
insert_samples()

if "user" not in st.session_state:
    st.session_state.user = None

# --- Sidebar Navigation ---
with st.sidebar:
    st.header("Navigation")
    menu = st.selectbox("Menu", ["Home", "Login", "Signup", "Logout"])

# --- HOME ---
if menu == "Home":
    st.header("Welcome 👋")
    st.write("A lightweight **Doctor Appointment Portal** demo built with Streamlit + SQLite.")
    st.info("Sample accounts:\n- **Doctor:** alice@example.com / password123\n- **Patient:** john@example.com / password123")

# --- SIGNUP ---
elif menu == "Signup":
    st.header("📝 Create Account")
    role = st.radio("Role", ("patient", "doctor"))
    name = st.text_input("Full Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    contact = st.text_input("Contact / Location")

    specialization = None
    experience = None
    photo = None
    if role == "doctor":
        specialization = st.text_input("Specialization")
        experience = st.number_input("Experience (years)", min_value=0, max_value=80, value=1)
        photo = st.file_uploader("Profile photo (optional)", type=["png", "jpg", "jpeg"])

    if st.button("Create Account"):
        photo_path = None
        if photo:
            os.makedirs("data/photos", exist_ok=True)
            save_path = os.path.join("data/photos", f"{os.urandom(4).hex()}_{photo.name}")
            with open(save_path, "wb") as f:
                f.write(photo.getbuffer())
            photo_path = save_path

        success, msg = register_user(
            name, email, password, role,
            specialization,
            int(experience) if experience else None,
            contact,
            photo_path
        )

        if success:
            st.success("✅ Account created successfully — please login.")
        else:
            st.error(msg)

# --- LOGIN ---
elif menu == "Login":
    st.header("🔐 Login")
    email = st.text_input("Email", key="login_email")
    password = st.text_input("Password", type="password", key="login_password")

    if st.button("Login"):
        user = login_user(email, password)
        if user:
            st.session_state.user = user
            st.success(f"Welcome, {user['name']} ({user['role']})")
            st.rerun()  # ✅ Updated method
        else:
            st.error("Invalid email or password.")

# --- LOGOUT ---
elif menu == "Logout":
    if st.button("Logout"):
        st.session_state.user = None
        st.success("You have been logged out.")
        st.rerun()

# --- DASHBOARDS (After Login) ---
if st.session_state.user:
    user = st.session_state.user
    role = user["role"]

    st.sidebar.markdown(f"**Logged in as:** {user['name']} ({role})")
    if st.sidebar.button("Logout (Quick)"):
        st.session_state.user = None
        st.rerun()

    if role == "doctor":
        doctor_dashboard(user)
    elif role == "patient":
        patient_dashboard(user)
    elif role == "admin":
        admin_dashboard(user)
else:
    st.info("Please login or signup to access dashboards.")
