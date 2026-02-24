"""
BILI Master System - Database Configuration
Supports PostgreSQL and SQLite (for local dev without PostgreSQL).
"""
import uuid
from sqlalchemy import create_engine, String
from sqlalchemy.types import TypeDecorator, CHAR
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.core.config import settings


class GUID(TypeDecorator):
    """Portable UUID type: stores as 36-char string for SQLite/PostgreSQL."""
    impl = CHAR(36)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, uuid.UUID):
            return str(value)
        return str(uuid.UUID(value))

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, uuid.UUID):
            return value
        return uuid.UUID(value)

def _make_engine():
    url = settings.DATABASE_URL
    if url and "sqlite" in url.lower():
        return create_engine(
            url,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
            echo=settings.APP_DEBUG,
        )
    try:
        return create_engine(
            url,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20,
            echo=settings.APP_DEBUG,
            connect_args={"connect_timeout": 5},
        )
    except Exception as e:
        print(f"Warning: Database engine creation failed: {e}")
        raise

try:
    engine = _make_engine()
except Exception as e:
    print(f"Warning: Database engine creation failed: {e}")
    print("App will continue but database features may not work.")
    engine = None

if engine:
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
else:
    SessionLocal = None

Base = declarative_base()


def get_db():
    """Strict dependency for getting database session.

    Will raise if the database is not available.
    """
    if engine is None or SessionLocal is None:
        raise Exception("Database not available")

    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def try_get_db():
    """Lenient dependency that yields a DB session when available, otherwise None.

    This allows certain endpoints (like the 20-point guest claim) to keep working
    in demo mode even if PostgreSQL is down.
    """
    if engine is None or SessionLocal is None:
        # Demo mode: no database, just yield None
        yield None
        return

    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
