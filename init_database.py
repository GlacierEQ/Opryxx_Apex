#!/usr/bin/env python3
"""
Initialize the database and apply migrations
"""
import os
import sys
import io
import sys
from pathlib import Path

# Set up console for UTF-8 output
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add the project root to the Python path
project_root = str(Path(__file__).parent.absolute())
sys.path.insert(0, project_root)

# Set PYTHONPATH environment variable
os.environ['PYTHONPATH'] = os.pathsep.join([project_root, os.environ.get('PYTHONPATH', '')])

def create_database():
    """Create the database and apply migrations"""
    from architecture.db import get_db_manager
    
    print("Initializing database...")
    
    # Initialize database
    db_manager = get_db_manager()
    if db_manager.init_db():
        print("[SUCCESS] Database initialized successfully")
        return True
    else:
        print("[ERROR] Failed to initialize database")
        return False

def run_migrations():
    """Run database migrations"""
    print("Applying database migrations...")
    
    try:
        from alembic.config import Config
        from alembic import command
        
        # Get the directory containing this script
        base_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Set up Alembic config
        alembic_cfg = Config(os.path.join(base_dir, "alembic.ini"))
        
        # Run migrations
        command.upgrade(alembic_cfg, "head")
        print("[SUCCESS] Database migrations applied successfully")
        return True
        
    except Exception as e:
        print(f"[ERROR] Error running migrations: {e}")
        return False

if __name__ == "__main__":
    if create_database() and run_migrations():
        print("[SUCCESS] Database setup completed successfully")
        sys.exit(0)
    else:
        print("[ERROR] Database setup failed")
        sys.exit(1)
