#!/usr/bin/env python3
"""
Initialize the database and apply migrations
"""
import os
import sys
import io
import sqlite3
from pathlib import Path
from typing import Optional, List

# Set up console for UTF-8 output
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add the project root to the Python path
project_root = str(Path(__file__).parent.absolute())
sys.path.insert(0, project_root)

from architecture.db import get_db_manager, DatabaseManager
from architecture.config import ConfigManager
from alembic.config import Config
from alembic import command, script
from alembic.runtime.migration import MigrationContext
from sqlalchemy import create_engine, inspect

def check_tables_exist(db_manager: DatabaseManager) -> bool:
    """Check if any of our tables already exist in the database."""
    try:
        # Ensure the engine is initialized
        if db_manager.engine is None:
            db_manager.init_db()
            
        # Create an inspector
        inspector = inspect(db_manager.engine)
        
        # Get list of existing tables
        existing_tables = set(inspector.get_table_names())
        our_tables = {'todo_categories', 'todos', 'todo_subtasks', 'todo_processing_logs'}
        
        # Check if any of our tables exist
        return len(our_tables.intersection(existing_tables)) > 0
    except Exception as e:
        print(f"[WARNING] Error checking for existing tables: {e}")
        return False

def check_migrations_applied(db_url: str) -> bool:
    """Check if migrations have already been applied."""
    try:
        engine = create_engine(db_url)
        with engine.connect() as conn:
            context = MigrationContext.configure(conn)
            current_rev = context.get_current_revision()
            
        if current_rev is None:
            print("[INFO] No migrations have been applied yet")
            return False
            
        print(f"[INFO] Current database revision: {current_rev}")
        return True
    except Exception as e:
        print(f"[WARNING] Could not check migration status: {e}")
        return False

def create_database() -> bool:
    """Initialize the database"""
    try:
        # Initialize database manager
        db_manager = get_db_manager()
        
        # First, ensure the database directory exists
        db_url = db_manager.config_manager.config.database.url
        if db_url.startswith('sqlite'):
            db_path = db_url.split('///')[-1]
            db_dir = os.path.dirname(db_path)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir, exist_ok=True)
        
        # Initialize the database engine
        if not db_manager.init_db():
            print("[ERROR] Failed to initialize database engine")
            return False
            
        # Check if tables already exist
        if check_tables_exist(db_manager):
            print("[INFO] Database tables already exist")
            return True
            
        # If no tables exist, create them
        print("[INFO] Creating database tables...")
        from models.base import Base
        Base.metadata.create_all(db_manager.engine)
        print("[SUCCESS] Database tables created successfully")
        return True
        
    except Exception as e:
        print(f"[ERROR] Error initializing database: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_migrations() -> bool:
    """Run database migrations"""
    try:
        # Set up Alembic config
        alembic_cfg = Config("alembic.ini")
        db_url = alembic_cfg.get_main_option("sqlalchemy.url", "")
        
        # Check if migrations have already been applied
        if check_migrations_applied(db_url):
            print("[INFO] Database migrations are already up to date")
            return True
            
        # Ensure the database directory exists for SQLite
        if db_url.startswith("sqlite"):
            db_path = db_url.split("///")[-1]
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        print("[INFO] Applying database migrations...")
        command.upgrade(alembic_cfg, "head")
        print("[SUCCESS] Database migrations applied successfully")
        return True
        
    except Exception as e:
        print(f"[ERROR] Error running migrations: {e}")
        return False

def main() -> int:
    """Main entry point for database initialization."""
    print("=" * 50)
    print("OPRYXX Database Initialization")
    print("=" * 50)
    
    # Step 1: Create database and tables if they don't exist
    if not create_database():
        print("[ERROR] Failed to initialize database")
        return 1
    
    # Step 2: Apply migrations if needed
    if not run_migrations():
        print("[WARNING] Some database migrations may have failed")
    
    print("\n[SUCCESS] Database setup completed successfully")
    return 0

if __name__ == "__main__":
    sys.exit(main())
