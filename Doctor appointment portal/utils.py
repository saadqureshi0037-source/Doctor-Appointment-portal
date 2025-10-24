# utils.py
from datetime import time
from typing import List


def minutes_to_time_str(minutes: int) -> str:
    h = minutes // 60
    m = minutes % 60
    return f"{h:02d}:{m:02d}"


def generate_slots(start_str: str, end_str: str, duration_min: int) -> List[str]:
    """
    start_str, end_str: 'HH:MM'
    returns list of slot start times as 'HH:MM'
    """
    sh, sm = map(int, start_str.split(":"))
    eh, em = map(int, end_str.split(":"))
    start = sh * 60 + sm
    end = eh * 60 + em
    slots = []
    cur = start
    while cur + duration_min <= end:
        slots.append(minutes_to_time_str(cur))
        cur += duration_min
    return slots


def overlaps(existing_start_min: int, existing_duration: int, new_start_min: int, new_duration: int) -> bool:
    existing_end = existing_start_min + existing_duration
    new_end = new_start_min + new_duration
    return not (new_end <= existing_start_min or new_start_min >= existing_end)


def can_book(doctor_appointments, new_time_str: str, new_duration: int) -> bool:
    """
    doctor_appointments: iterable of rows where columns include 'time','duration','status'.
    new_time_str: 'HH:MM'
    """
    nh, nm = map(int, new_time_str.split(":"))
    new_start = nh * 60 + nm
    for row in doctor_appointments:
        # row could be a sqlite3.Row -> mapping access or tuple -> index access; we assume mapping first
        try:
            ex_time = row["time"]
            ex_dur = int(row["duration"])
            ex_status = row["status"]
        except Exception:
            # fallback for tuple-like row: columns are (id, doctor_id, patient_id, date, time, duration, status, notes)
            ex_time = row[4]
            ex_dur = int(row[5])
            ex_status = row[6]
        ex_h, ex_m = map(int, ex_time.split(":"))
        ex_start = ex_h * 60 + ex_m
        if ex_status != 'cancelled' and overlaps(ex_start, ex_dur, new_start, new_duration):
            return False
    return True
