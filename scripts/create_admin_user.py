#!/usr/bin/env python3
"""
Create an admin user so you can log in to the Admin page.
Run once from bili folder:  python scripts/create_admin_user.py

Default credentials (password is not checked in current code):
  Username: admin@bili.local
  Password: admin123
"""
import os
import sys
from pathlib import Path

# Add project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from app.core.database import SessionLocal
from app.models.user import User, UserRole


def main():
    if SessionLocal is None:
        print("Database not configured. Set DATABASE_URL in .env")
        sys.exit(1)

    db = SessionLocal()
    try:
        email = "admin@bili.local"
        phone = os.environ.get("ADMIN_PHONE_NUMBER", "03520580").strip()

        existing = db.query(User).filter(
            (User.email == email) | (User.phone_number == phone),
            User.role == UserRole.ADMIN,
        ).first()
        if existing:
            print("Admin user already exists.")
            print("  Username: ", existing.email or existing.phone_number)
            print("  Password: (any; not checked in current code)")
            return

        admin = User(
            email=email,
            phone_number=phone,
            role=UserRole.ADMIN,
            is_guest=False,
            display_name="Admin",
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        print("Admin user created.")
        print("  Username: ", email, "  (or use ", phone, ")")
        print("  Password: admin123  (password is not checked yet; any value works)")
    finally:
        db.close()


if __name__ == "__main__":
    main()
