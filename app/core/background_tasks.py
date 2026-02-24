"""
BILI Master System - Background Tasks
Silent Decay monitoring and cleanup tasks
"""
import asyncio
from datetime import datetime, timedelta
from app.core.database import SessionLocal
from app.models.user import User, UserStatus
from app.core.websocket import websocket_manager
from app.core.config import settings
from app.models.post import Post
from app.models.chat import Chat
from app.models.manual_map_pin import ManualMapPin
from app.wallet_finance import WalletFinanceHandler
from app.services.pin_content_refresh import refresh_pin_content
from sqlalchemy import or_, and_


async def silent_decay_monitor():
    """
    Background task: Monitor and apply Silent Decay Logic
    Runs every 30 seconds to remove offline users with 0 credits
    """
    while True:
        try:
            await asyncio.sleep(30)  # Check every 30 seconds
            
            if SessionLocal is None:
                continue
            db = SessionLocal()
            try:
                # Find all offline users with zero balance
                offline_zero_users = db.query(User).filter(
                    User.status == UserStatus.OFFLINE,
                    User.credit_balance == 0.00,
                    User.is_invisible == False
                ).all()
                
                for user in offline_zero_users:
                    # Remove from radar via WebSocket
                    await websocket_manager.remove_from_radar(str(user.id))
                    
            finally:
                db.close()
                
        except Exception as e:
            print(f"Error in Silent Decay monitor: {e}")


async def expire_posts():
    """
    Background task: Expire commercial posts after 48 hours
    """
    while True:
        try:
            await asyncio.sleep(3600)  # Check every hour
            
            if SessionLocal is None:
                continue
            db = SessionLocal()
            try:
                expired_posts = db.query(Post).filter(
                    Post.is_expired == False,
                    Post.expires_at.isnot(None),
                    Post.expires_at < datetime.utcnow()
                ).all()
                
                for post in expired_posts:
                    post.is_expired = True
                    post.is_active = False
                
                db.commit()
            finally:
                db.close()
                
        except Exception as e:
            print(f"Error in post expiration: {e}")


async def cleanup_chats():
    """
    Background task: Auto-delete chats after 30-day retention period
    """
    while True:
        try:
            await asyncio.sleep(86400)  # Check daily
            
            if SessionLocal is None:
                continue
            db = SessionLocal()
            try:
                expired_chats = db.query(Chat).filter(
                    Chat.expires_at < datetime.utcnow(),
                    Chat.status != "deleted"
                ).all()
                
                for chat in expired_chats:
                    chat.status = "deleted"
                    chat.deleted_at = datetime.utcnow()
                    # Delete associated messages
                    for message in chat.messages:
                        db.delete(message)
                
                db.commit()
            finally:
                db.close()
                
        except Exception as e:
            print(f"Error in chat cleanup: {e}")


async def automatic_withdrawal_monitor():
    """
    Background task: Monitor user balances and process automatic withdrawals
    when balance reaches $50 threshold [cite: 2026-02-03]
    Runs every 5 minutes to check eligible users
    """
    while True:
        try:
            await asyncio.sleep(300)  # Check every 5 minutes
            
            if SessionLocal is None:
                continue
            db = SessionLocal()
            try:
                handler = WalletFinanceHandler(db)
                
                # Get all users with credit balance > 0
                users_with_credits = db.query(User).filter(
                    User.credit_balance > 0.00
                ).all()
                
                processed_count = 0
                for user in users_with_credits:
                    try:
                        # Check if eligible for withdrawal
                        threshold_check = handler.check_withdrawal_threshold(str(user.id))
                        
                        if threshold_check.get("eligible_for_withdrawal"):
                            # Process automatic withdrawal
                            result = await handler.process_automatic_withdrawal(str(user.id))
                            if result.get("success"):
                                processed_count += 1
                                print(f"Automatic withdrawal processed for user {user.id}: {result.get('amount_usdt')} USDT")
                    except Exception as e:
                        print(f"Error processing withdrawal for user {user.id}: {e}")
                        continue
                
                if processed_count > 0:
                    print(f"Automatic withdrawal monitor: Processed {processed_count} withdrawals")
                    
            finally:
                db.close()
                
        except Exception as e:
            print(f"Error in automatic withdrawal monitor: {e}")


async def refresh_store_pins_content():
    """
    Background task: Refresh latest video/post content for all pins with a profile URL.
    Runs every 30 minutes so pins stay fresh without manual updates.
    """
    while True:
        try:
            await asyncio.sleep(1800)  # 30 minutes
            if SessionLocal is None:
                continue
            db = SessionLocal()
            try:
                pins = db.query(ManualMapPin).filter(ManualMapPin.profile_url.isnot(None)).all()
                for pin in pins:
                    try:
                        if refresh_pin_content(pin):
                            db.commit()
                    except Exception as e:
                        print(f"Error refreshing pin {pin.id}: {e}")
                        db.rollback()
            finally:
                db.close()
        except Exception as e:
            print(f"Error in store pins refresh: {e}")


def start_background_tasks():
    """Start all background tasks"""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    if not loop.is_running():
        loop.create_task(silent_decay_monitor())
        loop.create_task(expire_posts())
        loop.create_task(cleanup_chats())
        loop.create_task(automatic_withdrawal_monitor())
        loop.create_task(refresh_store_pins_content())
    else:
        asyncio.create_task(silent_decay_monitor())
        asyncio.create_task(expire_posts())
        asyncio.create_task(cleanup_chats())
        asyncio.create_task(automatic_withdrawal_monitor())
        asyncio.create_task(refresh_store_pins_content())
