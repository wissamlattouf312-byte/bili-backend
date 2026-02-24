"""
BILI Master System - SMS Service
Placeholder 'X' for SMS API credentials - fill in .env file
"""
try:
    import httpx
    HAS_HTTPX = True
except ImportError:
    httpx = None
    HAS_HTTPX = False

from app.core.config import settings
from typing import Optional


async def send_sms(
    phone_number: str,
    message: str
) -> bool:
    """
    Send SMS message.
    Uses placeholder 'X' for API credentials - configure in .env
    """
    if settings.SMS_API_KEY == "X" or settings.SMS_API_URL == "X":
        # In development, just log the message
        print(f"[SMS] Would send to {phone_number}: {message}")
        return True
    
    if not HAS_HTTPX:
        print(f"[SMS] httpx not available. Would send to {phone_number}: {message}")
        return True
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                settings.SMS_API_URL,
                json={
                    "api_key": settings.SMS_API_KEY,
                    "to": phone_number,
                    "message": message
                },
                timeout=10.0
            )
            response.raise_for_status()
            return True
    except Exception as e:
        print(f"Failed to send SMS: {e}")
        return False


async def send_sms_alert(
    phone_number: str,
    alert_message: str
) -> bool:
    """Send SMS alert"""
    return await send_sms(phone_number, alert_message)
