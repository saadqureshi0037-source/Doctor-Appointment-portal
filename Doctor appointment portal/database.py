import sqlite3
import os
from typing import Optional, List, Tuple
import uuid

DB_PATH = "data/appointments.db"

# --- Dict factory (makes rows behave like real dicts) ---
def dict_factory(cursor, row):
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}

# --- Connection helper ---
def get_conn():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = dict_factory  # ✅ now returns dicts
    return conn

# Global connection
_conn = get_conn()

# --- Initialize DB ---
def init_db():
    cur = _conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            specialization TEXT,
            experience INTEGER,
            contact TEXT,
            photo_path TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id TEXT PRIMARY KEY,
            doctor_id TEXT NOT NULL,
            patient_id TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            duration INTEGER NOT NULL,
            status TEXT NOT NULL,
            notes TEXT,
            FOREIGN KEY(doctor_id) REFERENCES users(id),
            FOREIGN KEY(patient_id) REFERENCES users(id)
        )
    """)
    _conn.commit()

# --- User CRUD ---
def add_user(user_id: str, name: str, email: str, password_hash: str, role: str,
             specialization: Optional[str] = None, experience: Optional[int] = None,
             contact: Optional[str] = None, photo_path: Optional[str] = None) -> None:
    cur = _conn.cursor()
    cur.execute("""
        INSERT INTO users (id, name, email, password, role, specialization, experience, contact, photo_path)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (user_id, name, email, password_hash, role, specialization, experience, contact, photo_path))
    _conn.commit()

def get_user_by_email(email: str):
    cur = _conn.cursor()
    cur.execute("SELECT * FROM users WHERE email = ?", (email,))
    return cur.fetchone()

def get_user_by_id(uid: str):
    cur = _conn.cursor()
    cur.execute("SELECT * FROM users WHERE id = ?", (uid,))
    return cur.fetchone()

def get_all_users():
    cur = _conn.cursor()
    cur.execute("SELECT * FROM users ORDER BY role, name")
    return cur.fetchall()

def list_doctors(filter_text: Optional[str] = None):
    cur = _conn.cursor()
    if filter_text:
        like = f"%{filter_text}%"
        cur.execute("""
            SELECT * FROM users
            WHERE role = 'doctor'
            AND (name LIKE ? OR specialization LIKE ? OR contact LIKE ?)
        """, (like, like, like))
    else:
        cur.execute("SELECT * FROM users WHERE role = 'doctor'")
    return cur.fetchall()

def get_all_doctors():
    return list_doctors(None)

# --- Appointment CRUD ---
def create_appointment(app_id: str, doctor_id: str, patient_id: str, date: str, time: str,
                       duration: int, status: str = 'pending', notes: str = '') -> None:
    cur = _conn.cursor()
    cur.execute("""
        INSERT INTO appointments (id, doctor_id, patient_id, date, time, duration, status, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (app_id, doctor_id, patient_id, date, time, duration, status, notes))
    _conn.commit()

def update_appointment_status(app_id: str, status: str) -> None:
    cur = _conn.cursor()
    cur.execute("UPDATE appointments SET status = ? WHERE id = ?", (status, app_id))
    _conn.commit()

def delete_appointment(app_id: str) -> None:
    cur = _conn.cursor()
    cur.execute("DELETE FROM appointments WHERE id = ?", (app_id,))
    _conn.commit()

def get_appointments_by_doctor(doctor_id: str, start_date: Optional[str] = None, end_date: Optional[str] = None):
    cur = _conn.cursor()
    if start_date and end_date:
        cur.execute("""
            SELECT * FROM appointments
            WHERE doctor_id = ? AND date BETWEEN ? AND ?
            ORDER BY date, time
        """, (doctor_id, start_date, end_date))
    else:
        cur.execute("SELECT * FROM appointments WHERE doctor_id = ? ORDER BY date, time", (doctor_id,))
    return cur.fetchall()

def get_appointments_by_patient(patient_id: str, start_date: Optional[str] = None, end_date: Optional[str] = None):
    cur = _conn.cursor()
    if start_date and end_date:
        cur.execute("""
            SELECT * FROM appointments
            WHERE patient_id = ? AND date BETWEEN ? AND ?
            ORDER BY date, time
        """, (patient_id, start_date, end_date))
    else:
        cur.execute("SELECT * FROM appointments WHERE patient_id = ? ORDER BY date, time", (patient_id,))
    return cur.fetchall()

def get_appointments_on(doctor_id: str, date_str: str):
    cur = _conn.cursor()
    cur.execute("SELECT * FROM appointments WHERE doctor_id = ? AND date = ? ORDER BY time", (doctor_id, date_str))
    return cur.fetchall()

def get_all_appointments():
    cur = _conn.cursor()
    cur.execute("SELECT * FROM appointments ORDER BY date, time")
    return cur.fetchall()

# --- Export helper ---
def export_appointments_df(appointments_rows):
    import pandas as pd
    if not appointments_rows:
        return pd.DataFrame()
    cols = list(appointments_rows[0].keys())
    df = pd.DataFrame(appointments_rows, columns=cols)
    return df

# --- Booking wrapper ---
def book_appointment(doctor_id: str, patient_id: str, date_str: str, time_str: str, duration: int,
                     status: str = 'pending', notes: str = '') -> bool:
    from utils import can_book
    existing = get_appointments_on(doctor_id, date_str)
    if not can_book(existing, time_str, duration):
        return False
    app_id = str(uuid.uuid4())
    create_appointment(app_id, doctor_id, patient_id, date_str, time_str, duration, status, notes)
    return True
