"""
BILI Master System - Authentication Middleware
"""
from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import jwt
from app.core.config import settings
from app.core.database import SessionLocal
from app.models.user import User, UserRole


security = HTTPBearer()


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = None,
    request: Optional[Request] = None,
) -> Optional[User]:
    """
    Get current authenticated user from JWT token.
    Returns None for guest access (allows browsing without auth).
    """
    if not credentials:
        return None

    try:
        token = credentials.credentials
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_id = payload.get("user_id")

        if not user_id:
            return None

        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            return user
        finally:
            db.close()
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
    except Exception:
        return None


async def require_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> User:
    """
    Require admin authentication.
    Raises 401 if not authenticated or not admin.
    """
    user = await get_current_user(credentials, None)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

    if user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    return user
