# patient_ui.py
import streamlit as st
import pandas as pd
from datetime import date
from streamlit.components.v1 import html
from database import (
    get_all_doctors,
    book_appointment,
    get_appointments_by_patient,
    update_appointment_status,
)

def animate_card():
    html("""
    <script>
    const cards = document.querySelectorAll('.stDataFrame, .stExpander');
    cards.forEach((el, i) => {
        el.style.opacity = 0;
        setTimeout(() => {
            el.style.transition = 'all 0.6s ease';
            el.style.opacity = 1;
            el.style.transform = 'translateY(0)';
        }, 100 * i);
    });
    </script>
    """, height=0)
def patient_dashboard(user):
    st.title("👩‍⚕️ Patient Dashboard")
    st.sidebar.header(f"Welcome, {user['name']}")
    st.markdown("---")

    tabs = st.tabs(["📅 Book Appointment", "🗂 My Appointments"])

    # --- Tab 1: Book Appointment ---
    with tabs[0]:
        st.subheader("Find a Doctor")

        doctors = get_all_doctors()
        if not doctors:
            st.info("No doctors registered yet.")
        else:
            df = pd.DataFrame(
                [tuple(d) for d in doctors],
                columns=[
                    "id",
                    "name",
                    "email",
                    "password",
                    "role",
                    "specialization",
                    "experience",
                    "contact",
                    "photo_path",
                ],
            )

            search = st.text_input("🔍 Search doctor by name or specialization")
            display_df = df
            if search:
                mask = (
                    df["name"].str.contains(search, case=False, na=False)
                    | df["specialization"].str.contains(search, case=False, na=False)
                )
                display_df = df[mask]

            if display_df.empty:
                st.warning("No matching doctors found.")
            else:
                st.dataframe(
                    display_df[["name", "specialization", "experience", "contact"]],
                    use_container_width=True,
                )

                st.markdown("### 🗓️ Book Appointment")
                doctor_name = st.selectbox("Select Doctor", display_df["name"].tolist())
                selected_row = display_df[display_df["name"] == doctor_name].iloc[0]

                appt_date = st.date_input("Select Date", value=date.today())
                appt_time = st.time_input("Select Time")
                duration = st.selectbox(
                    "Duration (minutes)", [15, 30, 45, 60], index=1
                )
                notes = st.text_area("Notes for Doctor")

                if st.button("💬 Book Appointment"):
                    success = book_appointment(
                        selected_row["id"],
                        user["id"],
                        appt_date.isoformat(),
                        appt_time.strftime("%H:%M"),
                        duration,
                        "pending",
                        notes,
                    )
                    if success:
                        st.success("✅ Appointment booked successfully! Awaiting confirmation.")
                    else:
                        st.error("❌ Failed to book appointment — slot conflict or unavailable.")

    # --- Tab 2: My Appointments ---
    with tabs[1]:
        st.subheader("My Appointments")

        rows = get_appointments_by_patient(user["id"])
        if not rows:
            st.info("No appointments found.")
        else:
            df = pd.DataFrame(
                [tuple(r) for r in rows],
                columns=[
                    "id",
                    "doctor_id",
                    "patient_id",
                    "date",
                    "time",
                    "duration",
                    "status",
                    "notes",
                ],
            )

            df["status_icon"] = df["status"].apply(
                lambda s: "🟢 Confirmed"
                if s == "confirmed"
                else "🟡 Pending"
                if s == "pending"
                else "🔴 Cancelled"
            )

            st.dataframe(
                df[["date", "time", "duration", "status_icon", "notes"]],
                use_container_width=True,
            )

            for r in rows:
                aid = r["id"]
                with st.expander(f"Appointment {aid} — {r['date']} {r['time']}"):
                    st.write(f"👨‍⚕️ **Doctor ID:** {r['doctor_id']}")
                    st.write(f"📝 **Notes:** {r['notes'] or '—'}")

                    if r["status"] != "cancelled":
                        if st.button(f"❌ Cancel Appointment {aid}", key=f"cancel_{aid}"):
                            update_appointment_status(aid, "cancelled")
                            st.rerun()
animate_card()