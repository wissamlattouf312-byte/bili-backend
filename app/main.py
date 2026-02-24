"""
BILI Master System - Main Application Entry Point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from app.core.config import settings
from app.api.v1.router import api_router
from app.core.database import Base
from app.core.websocket import websocket_manager
from app.core.background_tasks import start_background_tasks
from contextlib import asynccontextmanager

# Create database tables (only if database is available)
# Import models so their tables are registered with Base before create_all
try:
    from app.core.database import engine
    from app.models import FlashDeal, ManualMapPin  # noqa: F401 - register tables
    if engine is not None:
        Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"Warning: Could not connect to database: {e}")
    print("App will continue but database features may not work.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Start background tasks
    start_background_tasks()
    yield
    # Shutdown: Cleanup if needed
    pass

app = FastAPI(
    title="BILI Master System",
    description="Geolocation-based social platform with real-time radar",
    version="1.0.0-beta",
    docs_url="/api/docs" if settings.APP_DEBUG else None,
    redoc_url="/api/redoc" if settings.APP_DEBUG else None,
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GZip Compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Include API routes
app.include_router(api_router, prefix="/api/v1")


@app.get("/api/v1/health")
def health():
    """No-auth health check; does not use DB. Use to verify backend is reachable."""
    return {"status": "ok"}

# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket):
    user_id = None
    # Try to extract user_id from query params or headers
    try:
        query_params = dict(websocket.query_params)
        user_id = query_params.get("user_id")
    except:
        pass
    
    await websocket_manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_text()
            await websocket_manager.handle_message(websocket, data)
    except Exception as e:
        await websocket_manager.disconnect(websocket)


@app.get("/")
async def root():
    return {
        "message": "BILI Master System API",
        "version": "1.0.0-beta",
        "status": "operational"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
