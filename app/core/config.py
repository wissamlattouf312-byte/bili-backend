"""
BILI Master System - Configuration Management
All external API credentials use placeholder 'X' and must be set in .env file
"""
from pydantic_settings import BaseSettings
from typing import List
import os
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    # App Configuration
    APP_ENV: str = os.getenv("APP_ENV", "development")
    APP_DEBUG: bool = os.getenv("APP_DEBUG", "true").lower() == "true"
    BETA_MODE: bool = os.getenv("BETA_MODE", "true").lower() == "true"
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/bili_db")
    
    # Google Maps API (Placeholder: X)
    GOOGLE_MAPS_API_KEY: str = os.getenv("GOOGLE_MAPS_API_KEY", "X")
    
    # Bybit Wallet Integration (Placeholders: X)
    BYBIT_API_KEY: str = os.getenv("BYBIT_API_KEY", "X")
    BYBIT_API_SECRET: str = os.getenv("BYBIT_API_SECRET", "X")
    BYBIT_WALLET_ADDRESS: str = os.getenv("BYBIT_WALLET_ADDRESS", "X")
    BYBIT_TESTNET: bool = os.getenv("BYBIT_TESTNET", "false").lower() == "true"
    
    # WhatsApp Gateway (Placeholders: X)
    WHATSAPP_API_KEY: str = os.getenv("WHATSAPP_API_KEY", "X")
    WHATSAPP_API_URL: str = os.getenv("WHATSAPP_API_URL", "X")
    
    # SMS Service for Admin Alerts
    SMS_API_KEY: str = os.getenv("SMS_API_KEY", "X")
    SMS_API_URL: str = os.getenv("SMS_API_URL", "X")
    ADMIN_PHONE_NUMBER: str = os.getenv("ADMIN_PHONE_NUMBER", "03520580")
    
    # Firebase (Optional - Placeholders: X)
    FIREBASE_PROJECT_ID: str = os.getenv("FIREBASE_PROJECT_ID", "X")
    FIREBASE_PRIVATE_KEY: str = os.getenv("FIREBASE_PRIVATE_KEY", "X")
    FIREBASE_CLIENT_EMAIL: str = os.getenv("FIREBASE_CLIENT_EMAIL", "X")
    
    # JWT
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "X")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    
    # File Storage
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "uploads")
    MAX_VIDEO_SIZE_MB: int = int(os.getenv("MAX_VIDEO_SIZE_MB", "100"))
    MAX_VIDEO_DURATION_SECONDS: int = int(os.getenv("MAX_VIDEO_DURATION_SECONDS", "60"))
    MAX_VIDEO_RESOLUTION: str = os.getenv("MAX_VIDEO_RESOLUTION", "1080p")
    
    # Credit System
    INITIAL_CLAIM_CREDITS: int = int(os.getenv("INITIAL_CLAIM_CREDITS", "20"))
    REFERRAL_REWARD_CREDITS: int = int(os.getenv("REFERRAL_REWARD_CREDITS", "5"))
    AD_POST_COST_CREDITS: float = float(os.getenv("AD_POST_COST_CREDITS", "0.5"))
    MIN_CREDIT_PURCHASE_USD: float = float(os.getenv("MIN_CREDIT_PURCHASE_USD", "5"))
    
    # Royal Hospitality Period (days)
    ROYAL_HOSPITALITY_DAYS: int = int(os.getenv("ROYAL_HOSPITALITY_DAYS", "30"))
    
    # Auto-Sweep Configuration
    AUTO_SWEEP_THRESHOLD_USD: float = float(os.getenv("AUTO_SWEEP_THRESHOLD_USD", "50.0"))
    
    # Notification Radius (KM)
    DEFAULT_NOTIFICATION_RADIUS_KM: float = float(os.getenv("DEFAULT_NOTIFICATION_RADIUS_KM", "15"))
    
    # Post Expiration
    COMMERCIAL_POST_EXPIRATION_HOURS: int = int(os.getenv("COMMERCIAL_POST_EXPIRATION_HOURS", "48"))
    NOTIFICATION_COOLDOWN_HOURS: int = int(os.getenv("NOTIFICATION_COOLDOWN_HOURS", "12"))
    
    # Chat Retention (days)
    CHAT_RETENTION_DAYS: int = int(os.getenv("CHAT_RETENTION_DAYS", "30"))
    
    # Socket Grace Period (seconds)
    SOCKET_GRACE_PERIOD_SECONDS: int = int(os.getenv("SOCKET_GRACE_PERIOD_SECONDS", "60"))
    
    # CORS - Allow frontend origins (set CORS_ORIGINS in .env for production, e.g. https://your-app.netlify.app)
    CORS_ORIGINS: List[str] = []
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # allow .env to contain frontend-only vars (e.g. REACT_APP_*)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        origins = [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:3001",
            "http://127.0.0.1:3001"
        ]
        # Add production frontend URL from env (comma-separated for multiple)
        extra = os.getenv("CORS_ORIGINS", "").strip()
        if extra:
            origins.extend([o.strip() for o in extra.split(",") if o.strip()])
        if self.APP_DEBUG:
            origins.append("*")
        self.CORS_ORIGINS = origins


settings = Settings()
