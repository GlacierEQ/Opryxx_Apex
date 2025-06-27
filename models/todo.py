"""
Todo Models
SQLAlchemy models for the task management system
"""

from datetime import datetime
from enum import Enum as PyEnum
from typing import List, Optional, Dict, Any

from sqlalchemy import (
    Column, String, Text, DateTime, Boolean, Integer, 
    ForeignKey, JSON, Enum, event, func, Index
)
from sqlalchemy.orm import relationship, validates
from sqlalchemy.ext.declarative import declared_attr

# Import Base from models.base to avoid circular imports
from .base import Base

class Priority(str, PyEnum):
    """Priority levels for todos"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class TodoStatus(str, PyEnum):
    """Status of todo items"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ARCHIVED = "archived"
    FAILED = "failed"

class ProcessingStatus(str, PyEnum):
    """Auto-processing status"""
    QUEUED = "queued"
    PROCESSING = "processing"
    PROCESSED = "processed"
    ERROR = "error"

class Todo(Base):
    """Main Todo model"""
    __tablename__ = "todos"
    
    # Core fields
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(200), nullable=False)
    description = Column(Text)
    priority = Column(Enum(Priority), default=Priority.MEDIUM, nullable=False)
    status = Column(Enum(TodoStatus), default=TodoStatus.PENDING, nullable=False, index=True)
    due_date = Column(DateTime, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime)
    
    # Metadata
    tags = Column(JSON, default=list, nullable=False)
    metadata_ = Column("metadata", JSON, default=dict, nullable=False)
    
    # Relationships
    category_id = Column(String(36), ForeignKey("todo_categories.id"), index=True)
    parent_id = Column(String(36), ForeignKey("todos.id"), index=True)
    
    # Relationships
    category = relationship("TodoCategory", back_populates="todos")
    subtasks = relationship(
        "Todo", 
        back_populates="parent",
        lazy="dynamic",
        cascade="all, delete-orphan"
    )
    parent = relationship("Todo", remote_side=[id], back_populates="subtasks")
    processing_logs = relationship(
        "TodoProcessingLog", 
        back_populates="todo",
        cascade="all, delete-orphan"
    )
    
    # Indexes
    __table_args__ = (
        Index('idx_todo_status_priority', 'status', 'priority', 'due_date'),
    )
    
    def __repr__(self):
        return f"<Todo(id='{self.id}', title='{self.title}', status='{self.status}')>"
    
    @validates('title')
    def validate_title(self, key, title):
        if not title or not title.strip():
            raise ValueError("Title cannot be empty")
        return title.strip()
    
    @property
    def is_overdue(self) -> bool:
        """Check if the todo is overdue"""
        return self.due_date and self.due_date < datetime.utcnow()
    
    @property
    def progress(self) -> float:
        """Calculate completion progress (0-1)"""
        if not self.subtasks.count():
            return 1.0 if self.status == TodoStatus.COMPLETED else 0.0
        
        completed = self.subtasks.filter_by(status=TodoStatus.COMPLETED).count()
        return completed / self.subtasks.count()

class TodoCategory(Base):
    """Categories for organizing todos"""
    __tablename__ = "todo_categories"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text)
    color = Column(String(7))  # Hex color code
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    todos = relationship("Todo", back_populates="category", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<TodoCategory(id='{self.id}', name='{self.name}')>"

class TodoSubtask(Base):
    """Subtasks for breaking down todos"""
    __tablename__ = "todo_subtasks"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    todo_id = Column(String(36), ForeignKey("todos.id"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    completed = Column(Boolean, default=False, nullable=False)
    order = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    todo = relationship("Todo", back_populates="subtasks")
    
    def __repr__(self):
        return f"<TodoSubtask(id='{self.id}', title='{self.title}')>"

class TodoProcessingLog(Base):
    """Log of automatic processing activities"""
    __tablename__ = "todo_processing_logs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    todo_id = Column(String(36), ForeignKey("todos.id"), nullable=False, index=True)
    action = Column(String(100), nullable=False)
    details = Column(JSON)
    status = Column(Enum(ProcessingStatus), default=ProcessingStatus.QUEUED, nullable=False, index=True)
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    completed_at = Column(DateTime)
    
    # Relationships
    todo = relationship("Todo", back_populates="processing_logs")
    
    def __repr__(self):
        return f"<TodoProcessingLog(id='{self.id}', action='{self.action}')>"

# Event listeners
@event.listens_for(Todo, 'before_update')
def update_timestamps(mapper, connection, target):
    """Update timestamps automatically"""
    target.updated_at = datetime.utcnow()
    
    # Set completed_at when status changes to COMPLETED
    if target.status == TodoStatus.COMPLETED and \
       'status' in target.__dict__ and \
       target.__dict__['status'] != TodoStatus.COMPLETED:
        target.completed_at = datetime.utcnow()

# Import uuid at the bottom to avoid circular imports
import uuid
