#!/usr/bin/env python3
"""
Initialize the database and run migrations
"""
import argparse
import os
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.absolute()))

def init_db():
    """Initialize the database and run migrations"""
    from architecture.db import init_db as init_database
    from architecture.config import ConfigManager
    
    print("Initializing database...")
    
    # Initialize configuration
    config_manager = ConfigManager()
    
    # Initialize database
    if init_database():
        print("✅ Database initialized successfully")
    else:
        print("❌ Failed to initialize database")
        return False
    
    # Run migrations
    if run_migrations():
        print("✅ Database migrations applied successfully")
    else:
        print("❌ Failed to apply database migrations")
        return False
    
    return True

def run_migrations() -> bool:
    """Run database migrations"""
    print("Running database migrations...")
    
    try:
        from alembic.config import Config
        from alembic import command
        
        # Get the directory containing this script
        base_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Set up Alembic config
        alembic_cfg = Config(os.path.join(base_dir, "alembic.ini"))
        
        # Run migrations
        command.upgrade(alembic_cfg, "head")
        return True
        
    except Exception as e:
        print(f"Error running migrations: {e}")
        return False

def create_migration(message: str = None) -> bool:
    """Create a new migration"""
    if not message:
        print("Error: Please provide a message for the migration")
        return False
    
    print(f"Creating new migration: {message}")
    
    try:
        from alembic.config import Config
        from alembic import command
        
        # Get the directory containing this script
        base_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Set up Alembic config
        alembic_cfg = Config(os.path.join(base_dir, "alembic.ini"))
        
        # Generate migration
        command.revision(alembic_cfg, autogenerate=True, message=message)
        return True
        
    except Exception as e:
        print(f"Error creating migration: {e}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Database management utility")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Init command
    init_parser = subparsers.add_parser("init", help="Initialize the database")
    
    # Migrate command
    migrate_parser = subparsers.add_parser("migrate", help="Run database migrations")
    
    # Create migration command
    create_parser = subparsers.add_parser("create-migration", help="Create a new migration")
    create_parser.add_argument("message", help="Migration message")
    
    args = parser.parse_args()
    
    if args.command == "init":
        success = init_db()
    elif args.command == "migrate":
        success = run_migrations()
    elif args.command == "create-migration":
        success = create_migration(args.message)
    else:
        parser.print_help()
        success = False
    
    sys.exit(0 if success else 1)
