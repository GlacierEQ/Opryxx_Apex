"""
Database Service for AI Workbench

This module provides database access and operations for the AI Workbench,
including saving metrics, recording actions, and managing predictions.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from sqlalchemy import create_engine, func, and_, or_
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError

# Import models
from ..models.workbench_models import (
    SystemMetric, SystemAction, FailurePrediction, OptimizationRule
)

# Import database configuration
from architecture.db import DatabaseManager, get_db_manager

# Set up logging
logger = logging.getLogger(__name__)


class WorkbenchDatabaseService:
    """Service for handling database operations for the AI Workbench"""
    
    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        """Initialize the database service"""
        self.db_manager = db_manager or get_db_manager()
        self.Session = sessionmaker(bind=self.db_manager.engine)
    
    def save_system_metric(self, metric_data: Dict[str, Any]) -> Optional[SystemMetric]:
        """
        Save system metrics to the database
        
        Args:
            metric_data: Dictionary containing metric data
            
        Returns:
            The created SystemMetric object or None if failed
        """
        session = self.Session()
        try:
            # Extract metadata if present
            metadata = metric_data.pop('metadata', {})
            
            # Create the metric
            metric = SystemMetric(
                **metric_data,
                metadata_=metadata
            )
            
            session.add(metric)
            session.commit()
            session.refresh(metric)
            return metric
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error saving system metric: {e}")
            return None
        finally:
            session.close()
    
    def record_action(
        self, 
        metric_id: int,
        action_type: str,
        description: str,
        status: str = 'pending',
        success: Optional[bool] = None,
        details: Optional[Dict] = None
    ) -> Optional[SystemAction]:
        """
        Record an action taken by the AI Workbench
        
        Args:
            metric_id: ID of the related system metric
            action_type: Type of action (e.g., 'clean_temp_files')
            description: Human-readable description of the action
            status: Current status of the action
            success: Whether the action was successful (if completed)
            details: Additional details about the action
            
        Returns:
            The created SystemAction object or None if failed
        """
        session = self.Session()
        try:
            action = SystemAction(
                metric_id=metric_id,
                action_type=action_type,
                description=description,
                status=status,
                success=success,
                details=details or {}
            )
            
            session.add(action)
            session.commit()
            session.refresh(action)
            return action
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error recording action: {e}")
            return None
        finally:
            session.close()
    
    def add_failure_prediction(
        self,
        metric_id: int,
        prediction_type: str,
        confidence: float,
        severity: str,
        predicted_failure_time: Optional[datetime] = None,
        time_to_failure: Optional[float] = None,
        contributing_factors: Optional[Dict] = None,
        recommended_actions: Optional[List[Dict]] = None
    ) -> Optional[FailurePrediction]:
        """
        Add a failure prediction to the database
        
        Args:
            metric_id: ID of the related system metric
            prediction_type: Type of failure being predicted
            confidence: Confidence score (0.0 to 1.0)
            severity: Severity level ('low', 'medium', 'high', 'critical')
            predicted_failure_time: When the failure is predicted to occur
            time_to_failure: Hours until predicted failure
            contributing_factors: Factors contributing to the prediction
            recommended_actions: List of recommended actions
            
        Returns:
            The created FailurePrediction object or None if failed
        """
        session = self.Session()
        try:
            prediction = FailurePrediction(
                metric_id=metric_id,
                prediction_type=prediction_type,
                confidence=confidence,
                severity=severity,
                predicted_failure_time=predicted_failure_time,
                time_to_failure=time_to_failure,
                contributing_factors=contributing_factors or {},
                recommended_actions=recommended_actions or []
            )
            
            session.add(prediction)
            session.commit()
            session.refresh(prediction)
            return prediction
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error adding failure prediction: {e}")
            return None
        finally:
            session.close()
    
    def get_recent_metrics(self, limit: int = 100) -> List[Dict]:
        """
        Get recent system metrics
        
        Args:
            limit: Maximum number of metrics to return
            
        Returns:
            List of metric dictionaries
        """
        session = self.Session()
        try:
            metrics = session.query(SystemMetric)\
                .order_by(SystemMetric.timestamp.desc())\
                .limit(limit)\
                .all()
            return [m.to_dict() for m in metrics]
        except Exception as e:
            logger.error(f"Error getting recent metrics: {e}")
            return []
        finally:
            session.close()
    
    def get_actions_by_status(self, status: str = None) -> List[Dict]:
        """
        Get system actions, optionally filtered by status
        
        Args:
            status: Optional status to filter by
            
        Returns:
            List of action dictionaries
        """
        session = self.Session()
        try:
            query = session.query(SystemAction)
            
            if status:
                query = query.filter(SystemAction.status == status)
                
            actions = query.order_by(SystemAction.timestamp.desc()).all()
            return [a.to_dict() for a in actions]
        except Exception as e:
            logger.error(f"Error getting actions: {e}")
            return []
        finally:
            session.close()
    
    def get_active_predictions(self) -> List[Dict]:
        """
        Get active failure predictions (not yet resolved)
        
        Returns:
            List of active prediction dictionaries
        """
        session = self.Session()
        try:
            predictions = session.query(FailurePrediction)\
                .filter(FailurePrediction.resolved == False)\
                .order_by(FailurePrediction.timestamp.desc())\
                .all()
            return [p.to_dict() for p in predictions]
        except Exception as e:
            logger.error(f"Error getting active predictions: {e}")
            return []
        finally:
            session.close()
    
    def get_optimization_rules(self, enabled_only: bool = True) -> List[Dict]:
        """
        Get optimization rules
        
        Args:
            enabled_only: If True, only return enabled rules
            
        Returns:
            List of optimization rule dictionaries
        """
        session = self.Session()
        try:
            query = session.query(OptimizationRule)
            
            if enabled_only:
                query = query.filter(OptimizationRule.enabled == True)
                
            rules = query.order_by(
                OptimizationRule.priority.desc(),
                OptimizationRule.name
            ).all()
            
            return [r.to_dict() for r in rules]
        except Exception as e:
            logger.error(f"Error getting optimization rules: {e}")
            return []
        finally:
            session.close()
    
    def update_action_status(
        self, 
        action_id: int, 
        status: str, 
        success: Optional[bool] = None,
        details: Optional[Dict] = None
    ) -> bool:
        """
        Update an action's status
        
        Args:
            action_id: ID of the action to update
            status: New status
            success: Whether the action was successful
            details: Additional details to update
            
        Returns:
            True if update was successful, False otherwise
        """
        session = self.Session()
        try:
            action = session.query(SystemAction).get(action_id)
            if not action:
                logger.warning(f"Action with ID {action_id} not found")
                return False
                
            action.status = status
            
            if success is not None:
                action.success = success
                
            if details is not None:
                action.details = details
                
            session.commit()
            return True
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error updating action status: {e}")
            return False
        finally:
            session.close()
    
    def resolve_prediction(self, prediction_id: int, resolved: bool = True) -> bool:
        """
        Mark a prediction as resolved or unresolved
        
        Args:
            prediction_id: ID of the prediction to update
            resolved: Whether to mark as resolved or unresolved
            
        Returns:
            True if update was successful, False otherwise
        """
        session = self.Session()
        try:
            prediction = session.query(FailurePrediction).get(prediction_id)
            if not prediction:
                logger.warning(f"Prediction with ID {prediction_id} not found")
                return False
                
            prediction.resolved = resolved
            session.commit()
            return True
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error updating prediction status: {e}")
            return False
        finally:
            session.close()


# Create a singleton instance
db_service = WorkbenchDatabaseService()
