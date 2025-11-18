"""
Example: Multi-environment deployment workflow.

This example demonstrates deploying to multiple environments with health checks.
"""

from orchestrator.core.pipeline_manager import PipelineManager, PipelineType
from monitors.health_checker import HealthChecker
from monitors.alerter import Alerter

# Configuration
config = {
    "environments": {
        "staging": {
            "url": "https://staging.example.com",
            "replicas": 2
        },
        "production": {
            "url": "https://production.example.com",
            "replicas": 5,
            "canary_percentage": 10
        }
    },
    "deployment": {
        "strategy": "blue_green",
        "health_check_timeout": 60,
        "rollback_on_failure": True
    }
}

# Initialize components
pipeline_manager = PipelineManager()
health_checker = HealthChecker()
alerter = Alerter({"channels": ["slack", "email"]})

def check_staging_health():
    """Check staging environment health."""
    # Simulate health check
    return True

def check_production_health():
    """Check production environment health."""
    # Simulate health check
    return True

# Register health checks
health_checker.register_component("staging", check_staging_health)
health_checker.register_component("production", check_production_health)

def run_multi_env_deployment():
    """Deploy to multiple environments with health checks."""
    print("Starting multi-environment deployment...")
    
    # Deploy to staging first
    print("\n=== Deploying to Staging ===")
    staging_config = {
        "environment": "staging",
        **config["deployment"]
    }
    
    staging_success = pipeline_manager.execute_pipeline(
        PipelineType.DEPLOY,
        staging_config
    )
    
    if staging_success:
        print("Staging deployment successful!")
        
        # Check staging health
        health_status = health_checker.check_health()
        print(f"Health check: {health_status}")
        
        if health_status["components"]["staging"] == "healthy":
            print("\n=== Deploying to Production ===")
            
            # Deploy to production
            production_config = {
                "environment": "production",
                **config["deployment"],
                **config["environments"]["production"]
            }
            
            production_success = pipeline_manager.execute_pipeline(
                PipelineType.DEPLOY,
                production_config
            )
            
            if production_success:
                print("Production deployment successful!")
                alerter.send_deployment_alert(
                    "production",
                    "success",
                    "Deployment completed successfully"
                )
            else:
                print("Production deployment failed! Rolling back...")
                alerter.send_deployment_alert(
                    "production",
                    "failure",
                    "Deployment failed, automatic rollback initiated"
                )
        else:
            print("Staging health check failed! Aborting production deployment.")
            alerter.send_alert(
                "warning",
                "Deployment Aborted",
                "Staging health check failed"
            )
    else:
        print("Staging deployment failed!")
        alerter.send_deployment_alert("staging", "failure", "Deployment failed")


if __name__ == "__main__":
    run_multi_env_deployment()
