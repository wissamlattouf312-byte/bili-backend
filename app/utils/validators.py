"""
BILI Master System - Input Validators
"""
import re
from typing import Optional


def validate_phone_number(phone: str) -> bool:
    """Validate phone number format"""
    if not phone:
        return False
    # Remove spaces and special characters
    cleaned = re.sub(r'[^\d+]', '', phone)
    # Check if it's a valid phone number (at least 8 digits)
    return len(cleaned) >= 8 and len(cleaned) <= 15


def validate_email(email: str) -> bool:
    """Validate email format"""
    if not email:
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_coordinates(latitude: float, longitude: float) -> bool:
    """Validate GPS coordinates"""
    return -90 <= latitude <= 90 and -180 <= longitude <= 180


def sanitize_string(input_str: str, max_length: int = 255) -> Optional[str]:
    """Sanitize user input string"""
    if not input_str:
        return None
    # Remove dangerous characters
    sanitized = re.sub(r'[<>"\']', '', input_str)
    return sanitized[:max_length] if len(sanitized) > max_length else sanitized
