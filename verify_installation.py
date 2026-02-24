"""
BILI Master System - Installation Verification Script
Run this to verify all files are in place and ready
"""
import os
import sys
from pathlib import Path

# Required files checklist
REQUIRED_FILES = [
    # Core
    "app/main.py",
    "app/core/config.py",
    "app/core/database.py",
    "app/core/websocket.py",
    "app/core/background_tasks.py",
    
    # API Endpoints (KEY FILES)
    "app/api/v1/endpoints/radar.py",  # Silent Decay Logic
    "app/api/v1/endpoints/admin.py",  # Alerts to 03 520 580
    "app/api/v1/endpoints/claim.py",  # 20 Credits reward
    "app/api/v1/endpoints/guest.py",
    "app/api/v1/endpoints/credits.py",
    "app/api/v1/router.py",
    
    # Models
    "app/models/user.py",
    "app/models/business.py",
    "app/models/credit.py",
    "app/models/post.py",
    "app/models/chat.py",
    
    # Schemas
    "app/schemas/claim.py",
    "app/schemas/radar.py",
    "app/schemas/credits.py",
    
    # Services
    "app/services/sms.py",
    "app/services/admin_alert.py",
    
    # Configuration
    ".env",
    "requirements.txt",
    "run.py",
]

def verify_installation():
    """Verify all required files exist"""
    print("🔍 Verifying BILI Master System Installation...")
    print("=" * 60)
    
    base_path = Path(__file__).parent
    missing_files = []
    found_files = []
    
    for file_path in REQUIRED_FILES:
        full_path = base_path / file_path
        if full_path.exists():
            found_files.append(file_path)
            print(f"✅ {file_path}")
        else:
            missing_files.append(file_path)
            print(f"❌ {file_path} - MISSING!")
    
    print("\n" + "=" * 60)
    print(f"✅ Found: {len(found_files)}/{len(REQUIRED_FILES)} files")
    
    if missing_files:
        print(f"❌ Missing: {len(missing_files)} files")
        print("\nMissing files:")
        for f in missing_files:
            print(f"  - {f}")
        return False
    else:
        print("✅ All required files are present!")
        print("\n🎉 Installation verification complete!")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Set up PostgreSQL database")
        print("3. Update .env file with database credentials")
        print("4. Run migrations: alembic upgrade head")
        print("5. Start server: python run.py")
        print("6. Test Radar: python test_radar.py")
        return True

if __name__ == "__main__":
    success = verify_installation()
    sys.exit(0 if success else 1)
