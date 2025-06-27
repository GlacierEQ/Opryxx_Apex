"""
Alembic environment configuration for database migrations.
"""

import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, inspect, pool

from alembic import context
from sqlalchemy import engine_from_config, pool

# Import the Base class from models
from models.base import Base
from architecture.config import ConfigManager

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the Base class from models
from models.base import Base
from architecture.config import ConfigManager

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import all models to ensure they are registered with SQLAlchemy
from models import todo  # noqa: F401

# Add your model's MetaData object here for 'autogenerate' support
target_metadata = Base.metadata

def get_url() -> str:
    """Get database URL from configuration"""
    # Load configuration
    config_manager = ConfigManager()
    db_config = config_manager.config.database
    
    # Ensure the directory exists for SQLite
    if db_config.type == "sqlite":
        db_dir = os.path.dirname(os.path.abspath(os.path.join(os.getcwd(), db_config.url.split("///")[-1])))
        os.makedirs(db_dir, exist_ok=True)
    
    # Return the URL from the DatabaseConfig
    return db_config.url

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well. By skipping the Engine creation
    we don't even need a DBAPI to be available.
    """
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    configuration = config.get_section(config.config_ini_section, {})
    url = get_url()
    configuration["sqlalchemy.url"] = url
    
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        # Create a migration context
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
            # Skip table existence checks for tables we know exist
            include_name=lambda name, type_, parent_names, is_compare_foreign_key: 
                not (type_ == 'table' and name in ['todo_categories', 'todos', 'todo_subtasks', 'todo_processing_logs'])
        )

        with context.begin_transaction():
            inspector = inspect(connection)
            
            # Check if any of our tables already exist
            existing_tables = set(inspector.get_table_names())
            our_tables = {'todo_categories', 'todos', 'todo_subtasks', 'todo_processing_logs'}
            tables_exist = len(our_tables.intersection(existing_tables)) > 0
            
            # Always run migrations - let Alembic handle the versioning
            print("[INFO] Running database migrations...")
            context.run_migrations()
            
            # If our tables existed but alembic_version didn't, we need to stamp the current revision
            if tables_exist and 'alembic_version' not in existing_tables:
                print("[INFO] Tables already existed - ensuring migration is stamped")
                # The migration will have created the version table, but we need to ensure it's at the right version
                # This is handled by the stamp command in init_database.py

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
