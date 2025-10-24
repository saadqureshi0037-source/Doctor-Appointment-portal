# admin_ui.py
import streamlit as st
import pandas as pd
from database import get_all_users, get_all_appointments

def admin_dashboard(user):
    st.title("🧑‍💼 Admin Dashboard")
    st.sidebar.header(f"Admin: {user['name']}")

    tabs = st.tabs(["👥 Users", "📅 Appointments"])

    with tabs[0]:
        st.subheader("All Registered Users")
        users = get_all_users()
        if not users:
            st.info("No users found.")
        else:
            df = pd.DataFrame([tuple(u) for u in users],
                              columns=["id", "name", "email", "password", "role", "specialization", "experience", "contact", "photo_path"])
            st.dataframe(df[["id", "name", "email", "role", "specialization", "experience", "contact"]])

    with tabs[1]:
        st.subheader("All Appointments")
        appts = get_all_appointments()
        if not appts:
            st.info("No appointments yet.")
        else:
            df = pd.DataFrame([tuple(a) for a in appts],
                              columns=["id", "doctor_id", "patient_id", "date", "time", "duration", "status", "notes"])
            df["status_icon"] = df["status"].apply(lambda s: "🟢 Confirmed" if s=="confirmed" else "🟡 Pending" if s=="pending" else "🔴 Cancelled")
            st.dataframe(df[["date", "time", "duration", "doctor_id", "patient_id", "status_icon", "notes"]])
