"""
Example: AI-powered automatic fix workflow.

This example demonstrates how the AI fixer automatically resolves build failures.
"""

from orchestrator.core.orchestrator import CICDOrchestrator
from orchestrator.core.pipeline_manager import PipelineManager, PipelineType
from orchestrator.fixers.ai_fixer import AIFixer
from orchestrator.fixers.build_fixer import BuildFixer
from monitors.alerter import Alerter

# Configuration
config = {
    "project": {
        "name": "auto-fix-demo",
        "repository": "https://github.com/user/auto-fix-demo.git"
    },
    "llm": {
        "provider": "openai",
        "model": "gpt-4",
        "api_key": "your-api-key"
    },
    "auto_fix": {
        "enabled": True,
        "max_retries": 3,
        "verify_fix": True
    }
}

# Initialize components
orchestrator = CICDOrchestrator(config)
pipeline_manager = PipelineManager()
ai_fixer = AIFixer(config["llm"])
build_fixer = BuildFixer()
alerter = Alerter({"channels": ["slack"]})

# Example workflow with automatic fixing
def run_auto_fix_workflow():
    """Run workflow with automatic failure resolution."""
    print("Starting AI-powered CI/CD workflow...")
    
    # Attempt build
    build_success = pipeline_manager.execute_pipeline(
        PipelineType.BUILD,
        {}
    )
    
    if not build_success:
        print("Build failed! Triggering AI fixer...")
        
        # Simulate failure logs
        failure_logs = """
        Error: ModuleNotFoundError: No module named 'requests'
        File "app.py", line 3, in <module>
            import requests
        """
        
        # AI analyzes the failure
        analysis = ai_fixer.analyze_failure(failure_logs)
        print(f"Analysis: {analysis}")
        
        # Generate fix
        fix = ai_fixer.generate_fix(analysis)
        print(f"Generated fix: {fix}")
        
        # Apply fix
        fix_applied = ai_fixer.apply_fix(fix, "requirements.txt")
        
        if fix_applied:
            print("Fix applied! Retrying build...")
            
            # Retry build
            retry_success = pipeline_manager.execute_pipeline(
                PipelineType.BUILD,
                {}
            )
            
            if retry_success:
                print("Build succeeded after fix!")
                alerter.send_alert(
                    "info",
                    "Auto-Fix Success",
                    "AI fixer resolved build failure automatically"
                )
            else:
                print("Build still failing after fix")
                alerter.send_alert(
                    "error",
                    "Auto-Fix Failed",
                    "Manual intervention required"
                )
        else:
            print("Failed to apply fix")
    else:
        print("Build succeeded on first try!")


if __name__ == "__main__":
    run_auto_fix_workflow()
