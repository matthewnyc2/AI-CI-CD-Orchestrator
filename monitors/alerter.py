"""
Alert system for CI/CD events and failures.
"""

import logging
from typing import Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)


class AlertLevel:
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class Alerter:
    """
    Send alerts for CI/CD events and failures.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the alerter with configuration.
        
        Args:
            config: Alert configuration including channels and thresholds
        """
        self.config = config
        self.alerts: List[Dict[str, Any]] = []
        logger.info("Alerter initialized")
    
    def send_alert(self, level: str, title: str, message: str, metadata: Dict[str, Any] = None):
        """
        Send an alert.
        
        Args:
            level: Alert level (info, warning, error, critical)
            title: Alert title
            message: Alert message
            metadata: Additional metadata
        """
        alert = {
            "level": level,
            "title": title,
            "message": message,
            "metadata": metadata or {},
            "timestamp": datetime.utcnow().isoformat()
        }
        self.alerts.append(alert)
        logger.log(
            self._get_log_level(level),
            f"Alert [{level}] {title}: {message}"
        )
        # Implementation for sending alerts to configured channels
    
    def send_pipeline_failure_alert(self, pipeline_id: str, pipeline_type: str, error: str):
        """
        Send an alert for pipeline failure.
        
        Args:
            pipeline_id: Pipeline identifier
            pipeline_type: Type of pipeline
            error: Error message
        """
        self.send_alert(
            AlertLevel.ERROR,
            f"{pipeline_type.capitalize()} Pipeline Failure",
            f"Pipeline {pipeline_id} failed: {error}",
            {"pipeline_id": pipeline_id, "pipeline_type": pipeline_type}
        )
    
    def send_deployment_alert(self, environment: str, status: str, details: str):
        """
        Send an alert for deployment events.
        
        Args:
            environment: Deployment environment
            status: Deployment status
            details: Deployment details
        """
        level = AlertLevel.INFO if status == "success" else AlertLevel.CRITICAL
        self.send_alert(
            level,
            f"Deployment to {environment}",
            f"Status: {status}. {details}",
            {"environment": environment, "status": status}
        )
    
    def get_alerts(self, level: str = None) -> List[Dict[str, Any]]:
        """
        Get alerts, optionally filtered by level.
        
        Args:
            level: Optional alert level filter
            
        Returns:
            List of alerts
        """
        if level:
            return [a for a in self.alerts if a["level"] == level]
        return self.alerts
    
    def _get_log_level(self, alert_level: str) -> int:
        """Convert alert level to logging level."""
        mapping = {
            AlertLevel.INFO: logging.INFO,
            AlertLevel.WARNING: logging.WARNING,
            AlertLevel.ERROR: logging.ERROR,
            AlertLevel.CRITICAL: logging.CRITICAL
        }
        return mapping.get(alert_level, logging.INFO)
