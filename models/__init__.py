"""
Database Models
SQLAlchemy models for the OPRYXX system
"""

# Import models to ensure they are registered with SQLAlchemy
from .todo import *  # noqa: F401, F403

__all__ = ['Base']

# Import the Base class from db module to make it easily accessible
from architecture.db import Base
