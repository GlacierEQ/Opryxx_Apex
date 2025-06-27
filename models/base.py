"""
Base Model
SQLAlchemy base class for all models
"""
from sqlalchemy.ext.declarative import declarative_base

# Create a base class for all models
Base = declarative_base()

# This allows us to import Base without circular imports
__all__ = ['Base']
