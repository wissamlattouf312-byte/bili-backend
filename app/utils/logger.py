"""
BILI Master System - Logging Configuration
"""
import logging
import sys
from app.core.config import settings

# Configure root logger
logging.basicConfig(
    level=logging.INFO if settings.APP_DEBUG else logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('bili.log')
    ]
)

logger = logging.getLogger("bili")

def get_logger(name: str):
    """Get a logger instance for a specific module"""
    return logging.getLogger(f"bili.{name}")
