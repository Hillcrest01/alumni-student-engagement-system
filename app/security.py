import secrets
from datetime import datetime, timedelta
from werkzeug.security import check_password_hash

def generate_temp_password(length=16):
    """Generate secure temporary password"""
    return secrets.token_urlsafe(length)

def password_complexity_check(password):
    """Enforce password policies"""
    if len(password) < 10:
        return False
    if not any(c.isupper() for c in password):
        return False
    if not any(c.isdigit() for c in password):
        return False
    return True