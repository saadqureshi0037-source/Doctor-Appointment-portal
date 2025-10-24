# sample_data.py
from auth import register_user
from database import get_all_doctors, get_all_users

def insert_samples():
    # Create a couple of doctors and a patient for testing. If they already exist, register_user will return False.
    # Using simple credentials for demonstration.
    register_user("Dr Alice", "alice@example.com", "password123", "doctor", specialization="Cardiology", experience=8, contact="City Hospital")
    register_user("Dr Bob", "bob@example.com", "password123", "doctor", specialization="Dermatology", experience=5, contact="Central Clinic")
    register_user("John Doe", "john@example.com", "password123", "patient", contact="N/A")

if __name__ == "__main__":
    insert_samples()
    print("Inserted sample users (if not already present).")
