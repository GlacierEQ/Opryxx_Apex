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
        # Create a temporary engine to check migrations
        from sqlalchemy import create_engine
        from sqlalchemy.engine import reflection
        
        engine = create_engine(db_url)
        inspector = reflection.Inspector.from_engine(engine)
        
        # Check if alembic_version table exists
        if 'alembic_version' not in inspector.get_table_names():
            # Check if our tables exist
            existing_tables = set(inspector.get_table_names())
            our_tables = {'todo_categories', 'todos', 'todo_subtasks', 'todo_processing_logs'}
            
            # If our tables exist but alembic_version doesn't, we need to stamp
            if our_tables.intersection(existing_tables):
                return False
            return True  # No tables, no migrations needed
            
        return True  # alembic_version exists, migrations are managed
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
    """Run database migrations."""
    try:
        from alembic import command
        from alembic.config import Config
        from sqlalchemy import create_engine, inspect
        
        # Get database URL from config
        db_manager = get_db_manager()
        db_url = db_manager.config_manager.config.database.url
        
        # Create alembic.ini if it doesn't exist
        if not os.path.exists("alembic.ini"):
            with open("alembic.ini", "w") as f:
                f.write(f"[alembic]\n")
                f.write(f"script_location = migrations\n")
                f.write(f"sqlalchemy.url = {db_url}\n")
                f.write("\n[loggers]\n")
                f.write("keys = root,sqlalchemy,alembic\n\n")
                f.write("[handlers]\n")
                f.write("keys = console\n\n")
                f.write("[formatters]\n")
                f.write("keys = generic\n\n")
                f.write("[logger_root]\n")
                f.write("level = WARN\n")
                f.write("handlers = console\n")
                f.write("qualname =\n\n")
                f.write("[logger_sqlalchemy]\n")
                f.write("level = WARN\n")
                f.write("handlers =\n")
                f.write("qualname = sqlalchemy.engine\n\n")
                f.write("[logger_alembic]\n")
        config = Config("alembic.ini")
        config.set_main_option("sqlalchemy.url", db_url)
        
        # Get the script directory to find the latest revision
        script = ScriptDirectory.from_config(config)
        head_revision = script.get_current_head()
        
        if not head_revision:
            print("[ERROR] No migration scripts found")
            return False
        
        # Check the current database revision
        with db_manager.engine.connect() as connection:
            context = MigrationContext.configure(connection)
            current_rev = context.get_current_revision()
            
            if current_rev == head_revision:
                print("[INFO] Database is already at the latest revision")
                return True
                
            if current_rev is None:
                print("[INFO] No migration history found - initializing database")
                # Check if tables already exist
                inspector = inspect(db_manager.engine)
                existing_tables = set(inspector.get_table_names())
                our_tables = {'todo_categories', 'todos', 'todo_subtasks', 'todo_processing_logs'}
                tables_exist = len(our_tables.intersection(existing_tables)) > 0
                
                if tables_exist:
                    print("[INFO] Tables exist but no migration history - stamping current revision")
                    command.stamp(config, "head")
                    print("[SUCCESS] Database stamped with current revision")
                    return True
        
        # Run migrations normally
        print("[INFO] Running database migrations...")
        command.upgrade(config, "head")
        print("[SUCCESS] Database migrations completed successfully")
        return True
        
    except Exception as e:
        print(f"[ERROR] Error running migrations: {e}")
        import traceback
        traceback.print_exc()
        return False

def backup_database(db_path: str) -> bool:
    """Backup the existing database file if it exists."""
    import shutil
    import time
    
    if not os.path.exists(db_path):
        return True
        
    try:
        # Create a backup with timestamp
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        backup_path = f"{db_path}.bak_{timestamp}"
        shutil.copy2(db_path, backup_path)
        print(f"[INFO] Backed up existing database to {backup_path}")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to backup database: {e}")
        return False

def main() -> int:
    """Main entry point for database initialization."""
    print("=" * 50)
    print("OPRYXX Database Initialization")
    print("=" * 50)
    
    # Get database path from config
    db_manager = get_db_manager()
    db_url = db_manager.config_manager.config.database.url
    
    if db_url.startswith('sqlite'):
        db_path = db_url.split('///')[-1]
        # Backup existing database if it exists
        if os.path.exists(db_path):
            if not backup_database(db_path):
                print("[WARNING] Could not backup existing database, but will try to continue")
            try:
                os.remove(db_path)
                print(f"[INFO] Removed existing database at {db_path}")
            except Exception as e:
                print(f"[ERROR] Failed to remove existing database: {e}")
                return 1
    
    # Initialize the database
    if not create_database():
        print("[ERROR] Failed to initialize database")
        return 1
    
    # Run migrations
    if not run_migrations():
        print("[WARNING] Some database migrations may have failed")
    
    print("\n[SUCCESS] Database setup completed successfully")
    return 0

if __name__ == "__main__":
    sys.exit(main())
