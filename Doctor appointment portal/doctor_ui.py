# doctor_ui.py
import streamlit as st
import pandas as pd
from datetime import date
from database import get_appointments_on, update_appointment_status, get_appointments_by_doctor
from utils import generate_slots  # for future availability feature
from streamlit.components.v1 import html
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
st.markdown("""
<div style="display:flex; gap:1rem;">
    <div style="flex:1; background:#e8f7ee; border-radius:12px; padding:1rem; text-align:center; box-shadow:0 2px 6px rgba(0,0,0,0.1);">
        <h3>🟢 Confirmed</h3>
        <p>Upcoming appointments</p>
    </div>
    <div style="flex:1; background:#fff7e6; border-radius:12px; padding:1rem; text-align:center; box-shadow:0 2px 6px rgba(0,0,0,0.1);">
        <h3>🟡 Pending</h3>
        <p>Awaiting confirmation</p>
    </div>
    <div style="flex:1; background:#fdeaea; border-radius:12px; padding:1rem; text-align:center; box-shadow:0 2px 6px rgba(0,0,0,0.1);">
        <h3>🔴 Cancelled</h3>
        <p>Past or declined</p>
    </div>
</div>
""", unsafe_allow_html=True)

def doctor_dashboard(user):
    st.header(f"Dr. {user['name']} — Dashboard")
    st.subheader("Your Profile")

    col1, col2 = st.columns([1, 3])
    with col1:
        if user.get("photo_path"):
            st.image(user["photo_path"], width=120)
        else:
            st.image("https://cdn-icons-png.flaticon.com/512/387/387561.png", width=100)

    with col2:
        st.write(f"**Specialization:** {user.get('specialization') or '—'}")
        st.write(f"**Experience:** {user.get('experience') or '—'} years")
        st.write(f"**Contact:** {user.get('contact') or '—'}")

    st.markdown("---")

    # --- Availability Section ---
    with st.expander("🕒 Manage Availability & Generate Slots"):
        with st.form("availability_form"):
            st.write("Define your daily availability window and consultation duration.")
            start = st.time_input("Start Time", key="doc_start")
            end = st.time_input("End Time", key="doc_end")
            duration = st.selectbox(
                "Consultation Duration (minutes)",
                [15, 20, 30, 45, 60],
                index=2
            )
            submitted = st.form_submit_button("💾 Save (demo only)")
            if submitted:
                st.success("Availability saved for session — in production, store this in the database.")

    st.markdown("---")
    st.subheader("📅 Appointments")

    d = st.date_input("Choose date", value=date.today())
    rows = get_appointments_on(user["id"], d.isoformat())

    if not rows:
        st.info("No appointments on this date.")
    else:
        df = pd.DataFrame(
            [tuple(r) for r in rows],
            columns=["id", "doctor_id", "patient_id", "date", "time", "duration", "status", "notes"]
        )

        def status_label(s: str) -> str:
            if s == "confirmed":
                return "🟢 Confirmed"
            elif s == "pending":
                return "🟡 Pending"
            else:
                return "🔴 Cancelled"

        df["status_display"] = df["status"].apply(status_label)
        st.dataframe(df[["date", "time", "duration", "status_display", "notes"]])

        for r in rows:
            aid = r["id"]
            astatus = r["status"]
            atime = r["time"]

            with st.expander(f"Appointment {aid} — {atime} — {astatus.title()}"):
                st.write(f"👤 **Patient ID:** {r['patient_id']}")
                st.write(f"📝 **Notes:** {r['notes'] or '—'}")

                if astatus != "confirmed":
                    if st.button(f"✅ Confirm {aid}", key=f"confirm_{aid}"):
                        update_appointment_status(aid, "confirmed")
                        st.rerun()

                if astatus != "cancelled":
                    if st.button(f"❌ Cancel {aid}", key=f"cancel_{aid}"):
                        update_appointment_status(aid, "cancelled")
                        st.rerun()

    st.markdown("---")
    st.subheader("📤 Export Appointments")

    all_rows = get_appointments_by_doctor(user["id"])
    if all_rows:
        df_all = pd.DataFrame(
            [tuple(r) for r in all_rows],
            columns=["id", "doctor_id", "patient_id", "date", "time", "duration", "status", "notes"]
        )
        csv = df_all.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Download CSV",
            data=csv,
            file_name=f"appointments_doctor_{user['id']}.csv",
            mime="text/csv"
        )
    else:
        st.info("No appointments to export.")
animate_card()
