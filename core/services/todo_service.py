"""
Todo Service
Business logic for todo management
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Union
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_
import logging

from ..models.todo import (
    Todo, TodoCategory, TodoSubtask, TodoProcessingLog,
    Priority, TodoStatus, ProcessingStatus
)
from ..architecture.db import get_db_manager

logger = logging.getLogger("OPRYXX.TodoService")

class TodoService:
    """Service class for todo management"""
    
    def __init__(self, db_session: Optional[Session] = None):
        """Initialize with optional database session"""
        self.db = db_session or next(get_db_manager().get_session())
    
    # ===== CRUD Operations =====
    
    def create_todo(self, title: str, **kwargs) -> Todo:
        """Create a new todo item"""
        try:
            todo = Todo(title=title, **kwargs)
            self.db.add(todo)
            self.db.commit()
            self.db.refresh(todo)
            logger.info(f"Created todo: {todo.id}")
            return todo
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create todo: {e}", exc_info=True)
            raise
    
    def get_todo(self, todo_id: str, include_relations: bool = True) -> Optional[Todo]:
        """Get a todo by ID"""
        query = self.db.query(Todo)
        
        if include_relations:
            query = query.options(
                joinedload(Todo.category),
                joinedload(Todo.subtasks),
                joinedload(Todo.processing_logs)
            )
            
        return query.get(todo_id)
    
    def update_todo(self, todo_id: str, **kwargs) -> Optional[Todo]:
        """Update a todo"""
        try:
            todo = self.get_todo(todo_id, include_relations=False)
            if not todo:
                return None
                
            for key, value in kwargs.items():
                if hasattr(todo, key):
                    setattr(todo, key, value)
            
            self.db.commit()
            self.db.refresh(todo)
            logger.info(f"Updated todo: {todo_id}")
            return todo
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to update todo {todo_id}: {e}", exc_info=True)
            raise
    
    def delete_todo(self, todo_id: str) -> bool:
        """Delete a todo and its subtasks"""
        try:
            todo = self.get_todo(todo_id, include_relations=False)
            if not todo:
                return False
                
            self.db.delete(todo)
            self.db.commit()
            logger.info(f"Deleted todo: {todo_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to delete todo {todo_id}: {e}", exc_info=True)
            raise
    
    # ===== Query Methods =====
    
    def list_todos(
        self,
        status: Optional[TodoStatus] = None,
        priority: Optional[Priority] = None,
        category_id: Optional[str] = None,
        due_before: Optional[datetime] = None,
        due_after: Optional[datetime] = None,
        search: Optional[str] = None,
        include_completed: bool = False,
        limit: int = 100,
        offset: int = 0
    ) -> List[Todo]:
        """List todos with filtering and pagination"""
        query = self.db.query(Todo)
        
        # Apply filters
        if status:
            query = query.filter(Todo.status == status)
        if priority:
            query = query.filter(Todo.priority == priority)
        if category_id:
            query = query.filter(Todo.category_id == category_id)
        if due_before:
            query = query.filter(Todo.due_date <= due_before)
        if due_after:
            query = query.filter(Todo.due_date >= due_after)
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Todo.title.ilike(search_term),
                    Todo.description.ilike(search_term)
                )
            )
        if not include_completed:
            query = query.filter(Todo.status != TodoStatus.COMPLETED)
        
        # Apply sorting and pagination
        return query.order_by(
            Todo.due_date.asc(),
            Todo.priority.desc(),
            Todo.created_at.desc()
        ).offset(offset).limit(limit).all()
    
    # ===== Category Operations =====
    
    def create_category(self, name: str, **kwargs) -> TodoCategory:
        """Create a new category"""
        try:
            category = TodoCategory(name=name, **kwargs)
            self.db.add(category)
            self.db.commit()
            self.db.refresh(category)
            logger.info(f"Created category: {category.id}")
            return category
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create category: {e}", exc_info=True)
            raise
    
    def get_category(self, category_id: str) -> Optional[TodoCategory]:
        """Get a category by ID"""
        return self.db.query(TodoCategory).get(category_id)
    
    def list_categories(self) -> List[TodoCategory]:
        """List all categories"""
        return self.db.query(TodoCategory).order_by(TodoCategory.name).all()
    
    # ===== Subtask Operations =====
    
    def add_subtask(self, todo_id: str, title: str, **kwargs) -> Optional[TodoSubtask]:
        """Add a subtask to a todo"""
        try:
            todo = self.get_todo(todo_id, include_relations=False)
            if not todo:
                return None
                
            subtask = TodoSubtask(todo_id=todo_id, title=title, **kwargs)
            self.db.add(subtask)
            self.db.commit()
            self.db.refresh(subtask)
            logger.info(f"Added subtask {subtask.id} to todo {todo_id}")
            return subtask
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to add subtask to todo {todo_id}: {e}", exc_info=True)
            raise
    
    def update_subtask_status(
        self, 
        subtask_id: str, 
        completed: bool
    ) -> Optional[TodoSubtask]:
        """Update subtask completion status"""
        try:
            subtask = self.db.query(TodoSubtask).get(subtask_id)
            if not subtask:
                return None
                
            subtask.completed = completed
            subtask.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(subtask)
            
            # Update parent todo status if needed
            if completed:
                todo = self.get_todo(subtask.todo_id)
                if todo and all(st.completed for st in todo.subtasks):
                    self.update_todo(todo.id, status=TodoStatus.COMPLETED)
            
            return subtask
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to update subtask {subtask_id}: {e}", exc_info=True)
            raise
    
    # ===== Processing Logs =====
    
    def log_processing(
        self,
        todo_id: str,
        action: str,
        details: Optional[Dict] = None,
        status: ProcessingStatus = ProcessingStatus.PROCESSING,
        error_message: Optional[str] = None
    ) -> TodoProcessingLog:
        """Log a processing action for a todo"""
        try:
            log = TodoProcessingLog(
                todo_id=todo_id,
                action=action,
                details=details or {},
                status=status,
                error_message=error_message
            )
            
            if status == ProcessingStatus.PROCESSED:
                log.completed_at = datetime.utcnow()
            
            self.db.add(log)
            self.db.commit()
            self.db.refresh(log)
            return log
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to log processing for todo {todo_id}: {e}", exc_info=True)
            raise
    
    def get_processing_logs(
        self,
        todo_id: Optional[str] = None,
        action: Optional[str] = None,
        status: Optional[ProcessingStatus] = None,
        limit: int = 100
    ) -> List[TodoProcessingLog]:
        """Get processing logs with optional filtering"""
        query = self.db.query(TodoProcessingLog)
        
        if todo_id:
            query = query.filter(TodoProcessingLog.todo_id == todo_id)
        if action:
            query = query.filter(TodoProcessingLog.action == action)
        if status:
            query = query.filter(TodoProcessingLog.status == status)
            
        return query.order_by(TodoProcessingLog.created_at.desc()).limit(limit).all()
    
    # ===== Utility Methods =====
    
    def get_upcoming_todos(self, days: int = 7) -> List[Todo]:
        """Get todos due in the next N days"""
        now = datetime.utcnow()
        due_by = now + timedelta(days=days)
        
        return self.db.query(Todo).filter(
            Todo.due_date.between(now, due_by),
            Todo.status != TodoStatus.COMPLETED
        ).order_by(Todo.due_date).all()
    
    def get_todo_stats(self) -> Dict[str, int]:
        """Get statistics about todos"""
        from sqlalchemy import func
        
        total = self.db.query(func.count(Todo.id)).scalar() or 0
        completed = self.db.query(func.count(Todo.id))\
            .filter(Todo.status == TodoStatus.COMPLETED)\
            .scalar() or 0
        overdue = self.db.query(func.count(Todo.id))\
            .filter(
                Todo.due_date < datetime.utcnow(),
                Todo.status != TodoStatus.COMPLETED
            )\
            .scalar() or 0
            
        return {
            'total': total,
            'completed': completed,
            'pending': total - completed,
            'overdue': overdue,
            'completion_rate': (completed / total * 100) if total > 0 else 0
        }
