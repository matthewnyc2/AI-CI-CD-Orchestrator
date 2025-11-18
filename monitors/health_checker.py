"""
Health checker for CI/CD system components.
"""

import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class HealthChecker:
    """
    Monitor the health of CI/CD system components.
    """
    
    def __init__(self):
        """Initialize the health checker."""
        self.components: Dict[str, Dict[str, Any]] = {}
        logger.info("HealthChecker initialized")
    
    def register_component(self, name: str, check_function):
        """
        Register a component for health monitoring.
        
        Args:
            name: Component name
            check_function: Function to check component health
        """
        self.components[name] = {
            "check_function": check_function,
            "status": "unknown"
        }
        logger.info(f"Registered component: {name}")
    
    def check_health(self) -> Dict[str, Any]:
        """
        Check the health of all registered components.
        
        Returns:
            Dictionary with health status of all components
        """
        health_report = {
            "overall_status": "healthy",
            "components": {}
        }
        
        for name, component in self.components.items():
            try:
                status = component["check_function"]()
                component["status"] = "healthy" if status else "unhealthy"
                health_report["components"][name] = component["status"]
                
                if not status:
                    health_report["overall_status"] = "degraded"
            except Exception as e:
                logger.error(f"Health check failed for {name}: {e}")
                component["status"] = "error"
                health_report["components"][name] = "error"
                health_report["overall_status"] = "degraded"
        
        return health_report
    
    def get_component_status(self, name: str) -> str:
        """
        Get the status of a specific component.
        
        Args:
            name: Component name
            
        Returns:
            Component status
        """
        return self.components.get(name, {}).get("status", "unknown")
