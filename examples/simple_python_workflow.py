"""
Example: Simple Python project CI/CD workflow.

This example demonstrates a basic CI/CD setup for a Python project.
"""

from orchestrator.core.orchestrator import CICDOrchestrator
from orchestrator.core.pipeline_manager import PipelineManager, PipelineType
from monitors.pipeline_monitor import PipelineMonitor
from monitors.alerter import Alerter

# Configuration
config = {
    "project": {
        "name": "my-python-app",
        "repository": "https://github.com/user/my-python-app.git",
        "language": "python",
        "version": "3.9"
    },
    "pipelines": {
        "build": {
            "enabled": True,
            "trigger": "on_commit"
        },
        "test": {
            "enabled": True,
            "trigger": "after_build"
        },
        "deploy": {
            "enabled": True,
            "trigger": "on_tag",
            "environments": ["staging", "production"]
        }
    },
    "alerts": {
        "channels": ["email", "slack"],
        "recipients": ["team@example.com"]
    }
}

# Initialize components
orchestrator = CICDOrchestrator(config)
pipeline_manager = PipelineManager()
monitor = PipelineMonitor()
alerter = Alerter(config["alerts"])

# Example workflow execution
def run_workflow():
    """Run the complete CI/CD workflow."""
    print("Starting CI/CD workflow for Python project...")
    
    # Start monitoring
    pipeline_id = "build-001"
    monitor.track_pipeline_start(pipeline_id, "build")
    
    # Execute build pipeline
    build_success = pipeline_manager.execute_pipeline(
        PipelineType.BUILD,
        config["pipelines"]["build"]
    )
    
    if build_success:
        print("Build succeeded!")
        
        # Execute test pipeline
        test_success = pipeline_manager.execute_pipeline(
            PipelineType.TEST,
            config["pipelines"]["test"]
        )
        
        if test_success:
            print("Tests passed!")
            
            # Execute deployment
            deploy_success = pipeline_manager.execute_pipeline(
                PipelineType.DEPLOY,
                config["pipelines"]["deploy"]
            )
            
            if deploy_success:
                print("Deployment successful!")
                alerter.send_deployment_alert("production", "success", "Deployed version 1.0.0")
            else:
                print("Deployment failed!")
                alerter.send_alert("error", "Deployment Failed", "Check logs for details")
        else:
            print("Tests failed!")
            alerter.send_pipeline_failure_alert(pipeline_id, "test", "Unit tests failed")
    else:
        print("Build failed!")
        alerter.send_pipeline_failure_alert(pipeline_id, "build", "Compilation error")
    
    # Track completion
    monitor.track_pipeline_end(pipeline_id, "success" if build_success else "failure", 120.5)
    
    # Print metrics
    success_rate = monitor.get_success_rate()
    print(f"Overall success rate: {success_rate}%")


if __name__ == "__main__":
    run_workflow()
