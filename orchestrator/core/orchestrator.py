"""
Main Orchestrator class for AI-driven CI/CD automation.
"""

import logging
import time
import threading
from typing import Dict, Any, List, Optional
from datetime import datetime
import git

from .pipeline_manager import PipelineManager, PipelineType, PipelineStatus
from ..fixers.ai_fixer import AIFixer
from ..fixers.build_fixer import BuildFixer
from ..fixers.test_fixer import TestFixer
from monitors.pipeline_monitor import PipelineMonitor
from monitors.alerter import Alerter, AlertSeverity

logger = logging.getLogger(__name__)


class CICDOrchestrator:
    """
    Main orchestrator that manages the CI/CD pipeline lifecycle.

    This class monitors code changes, triggers builds and tests,
    and coordinates automated fixes when issues are detected.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the orchestrator with configuration.

        Args:
            config: Configuration dictionary containing pipeline settings
        """
        self.config = config
        self.running = False
        self.monitor_thread: Optional[threading.Thread] = None

        # Initialize components
        self.pipeline_manager = PipelineManager(
            workspace=config.get("project", {}).get("workspace", "/tmp/ai-cicd-workspace")
        )

        # Initialize AI fixer if configured
        llm_config = config.get("llm", {})
        try:
            self.ai_fixer = AIFixer(llm_config)
        except Exception as e:
            logger.warning(f"AI fixer initialization failed: {e}. Auto-fix disabled.")
            self.ai_fixer = None

        # Initialize specialized fixers
        self.build_fixer = BuildFixer(self.ai_fixer)
        self.test_fixer = TestFixer()

        # Initialize monitoring
        self.pipeline_monitor = PipelineMonitor()
        self.alerter = Alerter(config.get("alerts", {}))

        # Pipeline definitions
        self.pipeline_definitions = self._load_pipeline_definitions()

        # Git repository tracking
        self.repo_path = None
        self.last_commit_sha = None

        logger.info("CICDOrchestrator initialized")

    def _load_pipeline_definitions(self) -> Dict[str, Dict[str, Any]]:
        """Load pipeline definitions."""
        from pipelines.build.build_pipeline import build_pipeline
        from pipelines.test.test_pipeline import test_pipeline
        from pipelines.deploy.deploy_pipeline import deploy_pipeline

        return {
            "build": build_pipeline,
            "test": test_pipeline,
            "deploy": deploy_pipeline
        }

    def start(self):
        """Start the orchestration process."""
        logger.info("Starting CI/CD orchestration...")

        if self.running:
            logger.warning("Orchestrator is already running")
            return

        self.running = True

        # Clone or open repository
        self._setup_repository()

        # Start monitoring thread if git monitoring is enabled
        if self.config.get("git", {}).get("monitor_enabled", True):
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
            logger.info("Git monitoring started")

        self.alerter.send_alert(
            "CI/CD Orchestrator Started",
            "The AI-powered CI/CD orchestrator is now running and monitoring for changes.",
            AlertSeverity.INFO
        )

    def stop(self):
        """Stop the orchestration process."""
        logger.info("Stopping CI/CD orchestration...")

        self.running = False

        # Wait for monitor thread to finish
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5)

        self.alerter.send_alert(
            "CI/CD Orchestrator Stopped",
            "The orchestrator has been stopped.",
            AlertSeverity.INFO
        )

        logger.info("Orchestrator stopped")

    def _setup_repository(self):
        """Setup or clone the git repository."""
        project_config = self.config.get("project", {})
        repo_url = project_config.get("repository")
        workspace = project_config.get("workspace", "/tmp/ai-cicd-workspace")

        if not repo_url:
            logger.warning("No repository configured. Skipping git setup.")
            return

        import os
        self.repo_path = os.path.join(workspace, "repo")

        try:
            if os.path.exists(self.repo_path):
                # Open existing repository
                repo = git.Repo(self.repo_path)
                logger.info(f"Using existing repository at {self.repo_path}")
            else:
                # Clone repository
                logger.info(f"Cloning repository: {repo_url}")
                repo = git.Repo.clone_from(repo_url, self.repo_path)

            # Get current commit
            self.last_commit_sha = repo.head.commit.hexsha
            logger.info(f"Repository ready. Current commit: {self.last_commit_sha[:8]}")

        except Exception as e:
            logger.error(f"Failed to setup repository: {e}")
            self.alerter.send_alert(
                "Repository Setup Failed",
                f"Failed to setup repository: {e}",
                AlertSeverity.ERROR
            )

    def _monitor_loop(self):
        """Main monitoring loop."""
        polling_interval = self.config.get("orchestrator", {}).get("polling_interval", 60)

        while self.running:
            try:
                self.monitor_changes()
                time.sleep(polling_interval)
            except Exception as e:
                logger.error(f"Error in monitor loop: {e}")
                time.sleep(polling_interval)

    def monitor_changes(self):
        """Monitor code repository for changes."""
        if not self.repo_path:
            return

        try:
            repo = git.Repo(self.repo_path)

            # Fetch latest changes
            origin = repo.remotes.origin
            origin.fetch()

            # Check for new commits
            current_sha = repo.head.commit.hexsha
            branch = self.config.get("project", {}).get("branch", "main")

            # Get remote branch commit
            remote_branch = f"origin/{branch}"
            if remote_branch not in [ref.name for ref in repo.refs]:
                logger.warning(f"Remote branch {remote_branch} not found")
                return

            remote_sha = repo.refs[remote_branch].commit.hexsha

            if current_sha != remote_sha:
                logger.info(f"New commits detected: {current_sha[:8]} -> {remote_sha[:8]}")

                # Pull latest changes
                repo.git.pull('origin', branch)
                self.last_commit_sha = remote_sha

                # Trigger build and test pipelines
                self._trigger_ci_pipeline()

        except Exception as e:
            logger.error(f"Error monitoring changes: {e}")

    def _trigger_ci_pipeline(self):
        """Trigger CI pipeline (build + test)."""
        logger.info("Triggering CI pipeline due to code changes")

        # Trigger build
        build_result = self.trigger_pipeline("build")

        if build_result.get("status") == PipelineStatus.SUCCESS:
            # Build succeeded, run tests
            test_result = self.trigger_pipeline("test")

            if test_result.get("status") == PipelineStatus.SUCCESS:
                # All good, optionally trigger deployment
                if self.config.get("pipelines", {}).get("deploy", {}).get("auto_deploy", False):
                    self.trigger_pipeline("deploy")
            else:
                # Handle test failure
                self.handle_failure(test_result)
        else:
            # Handle build failure
            self.handle_failure(build_result)

    def trigger_pipeline(self, pipeline_type: str) -> Dict[str, Any]:
        """
        Trigger a specific pipeline.

        Args:
            pipeline_type: Type of pipeline (build, test, deploy)

        Returns:
            Pipeline execution result
        """
        logger.info(f"Triggering {pipeline_type} pipeline...")

        # Check if pipeline is enabled
        pipeline_config = self.config.get("pipelines", {}).get(pipeline_type, {})
        if not pipeline_config.get("enabled", True):
            logger.info(f"{pipeline_type} pipeline is disabled")
            return {"status": "disabled"}

        # Get pipeline definition
        pipeline_def = self.pipeline_definitions.get(pipeline_type)
        if not pipeline_def:
            logger.error(f"Unknown pipeline type: {pipeline_type}")
            return {"status": "error", "error": f"Unknown pipeline: {pipeline_type}"}

        # Prepare execution context
        project_config = self.config.get("project", {})
        context = {
            "repository": project_config.get("repository"),
            "branch": project_config.get("branch", "main"),
            "workspace": project_config.get("workspace"),
            "repo_path": self.repo_path
        }

        # Execute pipeline
        try:
            result = self.pipeline_manager.execute_pipeline(
                PipelineType(pipeline_type),
                pipeline_def,
                context
            )
            
            # Get pipeline ID from result
            pipeline_id = result.get("id", "unknown")
            start_time = result.get("start_time")
            end_time = result.get("end_time")
            
            # Calculate duration if both timestamps available
            duration = 0.0
            if start_time and end_time:
                duration = (end_time - start_time).total_seconds()

            # Track pipeline start (retroactively with ID)
            self.pipeline_monitor.track_pipeline_start(pipeline_id, pipeline_type)

            # Track completion
            success = result.get("status") == PipelineStatus.SUCCESS
            status_str = "success" if success else "failure"
            self.pipeline_monitor.track_pipeline_end(pipeline_id, status_str, duration)

            if success:
                self.alerter.send_alert(
                    f"{pipeline_type.title()} Pipeline Succeeded",
                    f"The {pipeline_type} pipeline completed successfully.",
                    AlertSeverity.INFO
                )
            else:
                self.alerter.send_alert(
                    f"{pipeline_type.title()} Pipeline Failed",
                    f"The {pipeline_type} pipeline failed. Error: {result.get('error', 'Unknown')}",
                    AlertSeverity.ERROR
                )

            return result

        except Exception as e:
            logger.error(f"Pipeline {pipeline_type} failed with exception: {e}")
            # Cannot track end without pipeline_id in this case - pipeline never started properly

            self.alerter.send_alert(
                f"{pipeline_type.title()} Pipeline Error",
                f"Pipeline failed with exception: {e}",
                AlertSeverity.CRITICAL
            )

            return {
                "status": PipelineStatus.FAILED,
                "error": str(e),
                "type": pipeline_type
            }

    def handle_failure(self, failure_data: Dict[str, Any]):
        """
        Handle pipeline failures by coordinating fixes.

        Args:
            failure_data: Information about the failure
        """
        logger.error(f"Handling pipeline failure: {failure_data.get('type', 'unknown')}")

        # Check if auto-fix is enabled
        auto_fix_enabled = self.config.get("orchestrator", {}).get("auto_fix_enabled", True)
        if not auto_fix_enabled:
            logger.info("Auto-fix is disabled. Manual intervention required.")
            return

        max_attempts = self.config.get("orchestrator", {}).get("max_fix_attempts", 3)
        pipeline_type = failure_data.get("type", "unknown")

        # Try to fix the failure
        for attempt in range(1, max_attempts + 1):
            logger.info(f"Fix attempt {attempt}/{max_attempts} for {pipeline_type} failure")

            fix_result = self._attempt_fix(failure_data)

            if fix_result.get("success"):
                logger.info("Fix applied successfully. Retrying pipeline...")

                # Retry the pipeline
                retry_result = self.trigger_pipeline(pipeline_type)

                if retry_result.get("status") == PipelineStatus.SUCCESS:
                    logger.info("Pipeline succeeded after applying fix!")

                    self.alerter.send_alert(
                        f"{pipeline_type.title()} Fixed Successfully",
                        f"AI-powered fix resolved the {pipeline_type} failure on attempt {attempt}.",
                        AlertSeverity.INFO
                    )

                    return

                # Update failure data for next attempt
                failure_data = retry_result

            else:
                logger.warning(f"Fix attempt {attempt} failed: {fix_result.get('error', 'Unknown')}")

        # All attempts exhausted
        logger.error(f"Failed to fix {pipeline_type} after {max_attempts} attempts")

        self.alerter.send_alert(
            f"{pipeline_type.title()} Auto-Fix Failed",
            f"Failed to automatically fix {pipeline_type} failure after {max_attempts} attempts. Manual intervention required.",
            AlertSeverity.CRITICAL
        )

    def _attempt_fix(self, failure_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Attempt to fix a pipeline failure.

        Args:
            failure_data: Failure information

        Returns:
            Fix result
        """
        pipeline_type = failure_data.get("type", "unknown")
        error_message = failure_data.get("error", "")

        logger.info(f"Analyzing {pipeline_type} failure...")

        # Use specialized fixer based on pipeline type
        if pipeline_type == "build":
            return self._fix_build_failure(failure_data)
        elif pipeline_type == "test":
            return self._fix_test_failure(failure_data)
        else:
            # Use general AI fixer
            return self._fix_with_ai(failure_data)

    def _fix_build_failure(self, failure_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fix build failure using BuildFixer."""
        error_logs = failure_data.get("error", "")

        # Analyze the failure
        analysis = self.build_fixer.analyze_build_failure(error_logs)

        # Apply appropriate fix based on error type
        error_type = analysis.get("error_type")

        if error_type == "dependency":
            fix_result = self.build_fixer.fix_dependency_issues(analysis)
        elif error_type == "compilation":
            fix_result = self.build_fixer.fix_compilation_errors(analysis)
        elif error_type == "configuration":
            fix_result = self.build_fixer.fix_configuration_issues(analysis)
        else:
            # Use AI fixer for unknown issues
            return self._fix_with_ai(failure_data)

        # Apply the fix if we have file changes
        if self.ai_fixer and fix_result.get("files"):
            return self.ai_fixer.apply_fix(fix_result, self.repo_path)

        return fix_result

    def _fix_test_failure(self, failure_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fix test failure using TestFixer."""
        # Use AI fixer for test failures (test fixer needs more implementation)
        return self._fix_with_ai(failure_data)

    def _fix_with_ai(self, failure_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fix failure using general AI fixer."""
        if not self.ai_fixer:
            return {
                "success": False,
                "error": "AI fixer not available. Check LLM configuration."
            }

        try:
            # Analyze failure
            analysis = self.ai_fixer.analyze_failure(failure_data)

            if analysis.get("status") != "analyzed":
                return {"success": False, "error": "Failed to analyze failure"}

            # Generate fix
            context = {"repo_path": self.repo_path}
            fix = self.ai_fixer.generate_fix(analysis, context)

            if fix.get("status") != "generated":
                return {"success": False, "error": "Failed to generate fix"}

            # Apply fix
            result = self.ai_fixer.apply_fix(fix, self.repo_path)

            return result

        except Exception as e:
            logger.error(f"AI fix failed: {e}")
            return {"success": False, "error": str(e)}
