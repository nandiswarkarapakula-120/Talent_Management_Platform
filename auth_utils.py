"""
TalentSphere Elevate - Authentication Utilities
Handles password hashing, signup, login, and password recovery (no email required).
"""

import hashlib
import hmac
import os
import re
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db import run_query, now

SALT = "talentsphere_elevate_static_salt_v1"


def hash_password(password: str) -> str:
    return hmac.new(SALT.encode(), password.encode(), hashlib.sha256).hexdigest()


def verify_password(password: str, hashed: str) -> bool:
    return hmac.compare_digest(hash_password(password), hashed)


def valid_email(email: str) -> bool:
    return bool(re.match(r"^[\w\.\+-]+@[\w-]+\.[a-zA-Z]{2,}$", email))


def valid_mobile(mobile: str) -> bool:
    return bool(re.match(r"^[6-9]\d{9}$", mobile.strip()))


def username_exists(username: str) -> bool:
    return run_query("SELECT id FROM users WHERE username=?", (username,), fetchone=True) is not None


def email_exists(email: str) -> bool:
    return run_query("SELECT id FROM users WHERE email=?", (email,), fetchone=True) is not None


def signup_user(fullname, email, username, password, confirm_password, mobile, category):
    errors = []
    if not fullname or len(fullname.strip()) < 3:
        errors.append("Full name must be at least 3 characters.")
    if not valid_email(email):
        errors.append("Please enter a valid email address.")
    elif email_exists(email):
        errors.append("This email is already registered.")
    if not username or len(username.strip()) < 4:
        errors.append("Username must be at least 4 characters.")
    elif username_exists(username):
        errors.append("Username already taken. Please choose another.")
    if not password or len(password) < 6:
        errors.append("Password must be at least 6 characters.")
    if password != confirm_password:
        errors.append("Passwords do not match.")
    if not valid_mobile(mobile):
        errors.append("Please enter a valid 10-digit mobile number.")
    if category not in ("High School Student", "College Student", "Working Professional"):
        errors.append("Please select a valid category.")

    if errors:
        return False, errors, None

    user_id = run_query(
        """INSERT INTO users (fullname, email, username, password, mobile, category, created_at)
           VALUES (?,?,?,?,?,?,?)""",
        (fullname.strip(), email.strip().lower(), username.strip(), hash_password(password),
         mobile.strip(), category, now())
    )
    run_query(
        "INSERT INTO notifications (user_id, title, message, created_at) VALUES (?,?,?,?)",
        (user_id, "Welcome to TalentSphere Elevate! 🎉",
         f"Hi {fullname.split()[0]}, your {category} journey starts now. Explore your personalized dashboard!",
         now())
    )
    return True, [], user_id


def login_user(username_or_email, password):
    user = run_query("SELECT * FROM users WHERE username=? OR email=?",
                      (username_or_email.strip(), username_or_email.strip().lower()), fetchone=True)
    if not user:
        return False, "No account found with that username/email.", None
    if not user["is_active"]:
        return False, "Your account has been deactivated. Please contact admin.", None
    if not verify_password(password, user["password"]):
        return False, "Incorrect password. Please try again.", None
    return True, "Login successful!", user


def login_admin(username, password):
    admin = run_query("SELECT * FROM admins WHERE username=?", (username.strip(),), fetchone=True)
    if not admin:
        return False, "Invalid admin username.", None
    if not verify_password(password, admin["password"]):
        return False, "Incorrect password.", None
    return True, "Welcome back, Admin!", admin


def reset_password(username, mobile, new_password, confirm_password):
    user = run_query("SELECT * FROM users WHERE username=?", (username.strip(),), fetchone=True)
    if not user:
        return False, "No account found with that username."
    if user["mobile"] != mobile.strip():
        return False, "Mobile number does not match our records."
    if not new_password or len(new_password) < 6:
        return False, "New password must be at least 6 characters."
    if new_password != confirm_password:
        return False, "Passwords do not match."
    run_query("UPDATE users SET password=? WHERE id=?", (hash_password(new_password), user["id"]))
    return True, "Password reset successful! You can now log in."
