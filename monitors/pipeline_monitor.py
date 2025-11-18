"""
Monitoring tools for CI/CD pipeline health and metrics.
"""

import logging
from typing import Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)


class PipelineMonitor:
    """
    Monitor pipeline execution and collect metrics.
    """
    
    def __init__(self):
        """Initialize the pipeline monitor."""
        self.metrics: List[Dict[str, Any]] = []
        logger.info("PipelineMonitor initialized")
    
    def track_pipeline_start(self, pipeline_id: str, pipeline_type: str):
        """
        Track the start of a pipeline execution.
        
        Args:
            pipeline_id: Unique identifier for the pipeline
            pipeline_type: Type of pipeline (build, test, deploy)
        """
        metric = {
            "pipeline_id": pipeline_id,
            "type": pipeline_type,
            "start_time": datetime.utcnow().isoformat(),
            "status": "running"
        }
        self.metrics.append(metric)
        logger.info(f"Tracking pipeline {pipeline_id} start")
    
    def track_pipeline_end(self, pipeline_id: str, status: str, duration: float):
        """
        Track the completion of a pipeline execution.
        
        Args:
            pipeline_id: Unique identifier for the pipeline
            status: Final status (success, failure, cancelled)
            duration: Execution duration in seconds
        """
        for metric in self.metrics:
            if metric["pipeline_id"] == pipeline_id:
                metric["end_time"] = datetime.utcnow().isoformat()
                metric["status"] = status
                metric["duration"] = duration
                break
        logger.info(f"Pipeline {pipeline_id} completed with status: {status}")
    
    def get_metrics(self) -> List[Dict[str, Any]]:
        """
        Get all collected metrics.
        
        Returns:
            List of metric dictionaries
        """
        return self.metrics
    
    def get_success_rate(self) -> float:
        """
        Calculate pipeline success rate.
        
        Returns:
            Success rate as a percentage
        """
        if not self.metrics:
            return 0.0
        
        completed = [m for m in self.metrics if m.get("status") in ["success", "failure"]]
        if not completed:
            return 0.0
        
        successful = [m for m in completed if m["status"] == "success"]
        return (len(successful) / len(completed)) * 100
