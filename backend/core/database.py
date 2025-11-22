"""
Database setup and session management
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# Database path
DATABASE_PATH = "data/creatorflow.db"
Path(DATABASE_PATH).parent.mkdir(parents=True, exist_ok=True)

# Create engine (SQLite for simplicity)
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Dependency for getting DB session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database tables"""
    from models.user_profile import Base as ProfileBase
    
    ProfileBase.metadata.create_all(bind=engine)
    logger.info("Database tables created")

# Initialize on import
try:
    init_db()
except Exception as e:
    logger.warning(f"Database initialization failed: {e}")

