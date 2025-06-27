"""
Database Module
Handles database connections and session management
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional
import logging

from .config import ConfigManager

# Configure logging
logger = logging.getLogger("OPRYXX.Database")

# Create base class for models
Base = declarative_base()

# Global session factory
SessionLocal = None

class DatabaseManager:
    """Handles database connections and session management"""
    
    def __init__(self, config_manager: Optional[ConfigManager] = None):
        """Initialize database manager with configuration"""
        self.config_manager = config_manager or ConfigManager()
        self.engine = None
        self.SessionLocal = None
        
    def init_db(self) -> bool:
        """Initialize database connection and create tables"""
        try:
            db_config = self.config_manager.config.database
            
            # Create database URL
            db_url = db_config.url
            
            # Create engine
            self.engine = create_engine(
                db_url,
                echo=db_config.echo,
                pool_size=db_config.pool_size,
                max_overflow=db_config.max_overflow,
                pool_timeout=db_config.pool_timeout,
                pool_recycle=db_config.pool_recycle
            )
            
            # Create session factory
            global SessionLocal
            SessionLocal = scoped_session(
                sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            )
            
            # Import models to ensure they are registered with SQLAlchemy
            from ..models import todo  # noqa: F401
            
            # Create tables
            Base.metadata.create_all(bind=self.engine)
            
            logger.info(f"Database initialized at {db_url}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}", exc_info=True)
            raise
    
    def get_session(self):
        """Get a new database session"""
        if SessionLocal is None:
            self.init_db()
            
        db = SessionLocal()
        try:
            yield db
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error: {e}", exc_info=True)
            raise
        finally:
            db.close()
    
    def close(self):
        """Close all database connections"""
        if self.engine:
            self.engine.dispose()
            logger.info("Database connections closed")

# Global instance
db_manager: Optional[DatabaseManager] = None

def get_db_manager() -> DatabaseManager:
    """Get or create the global database manager instance"""
    global db_manager
    if db_manager is None:
        db_manager = DatabaseManager()
    return db_manager

def init_db() -> bool:
    """Initialize the global database manager"""
    return get_db_manager().init_db()

def get_db():
    """Dependency to get DB session for FastAPI"""
    return next(get_db_manager().get_session())

def close_db():
    """Close all database connections"""
    if db_manager:
        db_manager.close()
