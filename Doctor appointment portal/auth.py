# auth.py
import hashlib
import uuid
from typing import Optional
from database import add_user, get_user_by_email, get_user_by_id

# Demo static salt — replace with env secret in production
SALT = "__static_salt_demo_2025__"


def hash_password(password: str) -> str:
    h = hashlib.sha256()
    h.update((password + SALT).encode("utf-8"))
    return h.hexdigest()


def register_user(
    name: str,
    email: str,
    password: str,
    role: str,
    specialization: str | None = None,
    experience: int | None = None,
    contact: str | None = None,
    photo_path: str | None = None,
) -> tuple[bool, str]:
    """
    Register a new user.

    Returns:
        (success: bool, message_or_id: str)
    """
    if not name or not email or not password or not role:
        return False, "Missing required fields"
    if get_user_by_email(email):
        return False, "Email already registered"
    uid = str(uuid.uuid4())
    hashed = hash_password(password)
    add_user(uid, name, email, hashed, role.lower(), specialization, experience, contact, photo_path)
    return True, uid


def login_user(email: str, password: str) -> Optional[object]:
    """
    Attempt login. Returns the sqlite3.Row-like user object on success, or None.
    """
    user = get_user_by_email(email)
    if not user:
        return None
    stored_hash = user["password"]
    if stored_hash == hash_password(password):
        return user
    return None


def get_user(uid: str):
    return get_user_by_id(uid)
