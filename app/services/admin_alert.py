"""
BILI Master System - Admin Login Alert Service
Sends instant SMS to 03 520 580 upon admin login
"""
from datetime import datetime
from app.services.sms import send_sms_alert
from app.core.config import settings


async def send_admin_login_alert(
    admin_phone: str,
    login_time: datetime,
    ip_address: str = "X",
    username: str = "unknown"
) -> bool:
    """
    Send instant SMS notification to admin phone (03 520 580) upon login attempt.
    [cite: 2026-02-02]
    """
    message = (
        f"🔐 BILI Admin Login Alert\n"
        f"Time: {login_time.strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
        f"Username: {username}\n"
        f"IP: {ip_address}\n"
        f"Action: Admin panel accessed"
    )
    
    return await send_sms_alert(admin_phone, message)


async def send_admin_alert(message: str) -> bool:
    """
    Send general administrative alert to 03 520 580 [cite: 2026-02-02]
    """
    from app.core.config import settings
    return await send_sms_alert(settings.ADMIN_PHONE_NUMBER, message)
