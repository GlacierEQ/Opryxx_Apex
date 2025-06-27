"""
AI Workbench Database Models

This module defines the SQLAlchemy models for the AI Workbench, including:
- System metrics and health data
- AI actions and optimizations
- Predictive analytics and failure predictions
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy import Column, Integer, Float, String, Text, DateTime, JSON, ForeignKey, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.ext.declarative import declared_attr

# Use the same Base as our main application
from architecture.db import Base


class SystemMetric(Base):
    """Stores system health metrics collected by the AI Workbench"""
    __tablename__ = 'system_metrics'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Core system metrics
    cpu_usage = Column(Float, nullable=True)  # Percentage
    memory_usage = Column(Float, nullable=True)  # Percentage
    disk_usage = Column(Float, nullable=True)  # Percentage
    disk_space = Column(Float, nullable=True)  # GB free
    temp_files_size = Column(Float, nullable=True)  # MB
    network_status = Column(Boolean, nullable=True)
    security_status = Column(Boolean, nullable=True)
    
    # System information
    os_version = Column(String(100), nullable=True)
    python_version = Column(String(50), nullable=True)
    
    # Calculated health score
    health_score = Column(Float, nullable=False)
    
    # Additional metadata
    metadata_ = Column('metadata', JSON, nullable=True, default=dict)
    
    # Relationships
    actions = relationship("SystemAction", back_populates="metric")
    predictions = relationship("FailurePrediction", back_populates="metric")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'cpu_usage': self.cpu_usage,
            'memory_usage': self.memory_usage,
            'disk_usage': self.disk_usage,
            'disk_space': self.disk_space,
            'temp_files_size': self.temp_files_size,
            'network_status': self.network_status,
            'security_status': self.security_status,
            'os_version': self.os_version,
            'python_version': self.python_version,
            'health_score': self.health_score,
            'metadata': self.metadata_ or {}
        }


class SystemAction(Base):
    """Tracks actions taken by the AI Workbench"""
    __tablename__ = 'system_actions'
    
    id = Column(Integer, primary_key=True)
    metric_id = Column(Integer, ForeignKey('system_metrics.id'), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Action details
    action_type = Column(String(100), nullable=False)  # e.g., 'clean_temp_files', 'optimize_memory'
    description = Column(Text, nullable=False)
    status = Column(String(50), nullable=False)  # 'pending', 'in_progress', 'completed', 'failed'
    
    # Results and metrics
    success = Column(Boolean, nullable=True)
    details = Column(JSON, nullable=True)
    
    # Relationships
    metric = relationship("SystemMetric", back_populates="actions")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'metric_id': self.metric_id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'action_type': self.action_type,
            'description': self.description,
            'status': self.status,
            'success': self.success,
            'details': self.details or {}
        }


class FailurePrediction(Base):
    """Stores failure predictions and system health forecasts"""
    __tablename__ = 'failure_predictions'
    
    id = Column(Integer, primary_key=True)
    metric_id = Column(Integer, ForeignKey('system_metrics.id'), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Prediction details
    prediction_type = Column(String(100), nullable=False)  # e.g., 'disk_failure', 'memory_leak', 'cpu_bottleneck'
    confidence = Column(Float, nullable=False)  # 0.0 to 1.0
    severity = Column(String(50), nullable=False)  # 'low', 'medium', 'high', 'critical'
    
    # Timeframe and status
    predicted_failure_time = Column(DateTime, nullable=True)
    time_to_failure = Column(Float, nullable=True)  # Hours until predicted failure
    resolved = Column(Boolean, default=False, nullable=False)
    
    # Additional context
    contributing_factors = Column(JSON, nullable=True)
    recommended_actions = Column(JSON, nullable=True)
    
    # Relationships
    metric = relationship("SystemMetric", back_populates="predictions")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'metric_id': self.metric_id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'prediction_type': self.prediction_type,
            'confidence': self.confidence,
            'severity': self.severity,
            'predicted_failure_time': self.predicted_failure_time.isoformat() if self.predicted_failure_time else None,
            'time_to_failure': self.time_to_failure,
            'resolved': self.resolved,
            'contributing_factors': self.contributing_factors or {},
            'recommended_actions': self.recommended_actions or []
        }


class OptimizationRule(Base):
    """Stores optimization rules and thresholds for the AI Workbench"""
    __tablename__ = 'optimization_rules'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    
    # Rule conditions (as JSON for flexibility)
    conditions = Column(JSON, nullable=False)
    
    # Actions to take when conditions are met
    actions = Column(JSON, nullable=False)  # List of actions with parameters
    
    # Rule metadata
    enabled = Column(Boolean, default=True, nullable=False)
    priority = Column(Integer, default=0, nullable=False)  # Higher priority runs first
    
    # Timing and scheduling
    last_triggered = Column(DateTime, nullable=True)
    next_scheduled = Column(DateTime, nullable=True)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'conditions': self.conditions or {},
            'actions': self.actions or [],
            'enabled': self.enabled,
            'priority': self.priority,
            'last_triggered': self.last_triggered.isoformat() if self.last_triggered else None,
            'next_scheduled': self.next_scheduled.isoformat() if self.next_scheduled else None
        }
