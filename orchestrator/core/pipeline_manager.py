"""
Pipeline Manager for coordinating different pipeline types.
"""

import logging
import subprocess
import uuid
import os
import shutil
from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path
import git

logger = logging.getLogger(__name__)


class PipelineType(Enum):
    """Enum for pipeline types."""
    BUILD = "build"
    TEST = "test"
    DEPLOY = "deploy"


class PipelineStatus(Enum):
    """Pipeline execution status."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


class PipelineExecutor:
    """Executes individual pipeline tasks."""

    def __init__(self, workspace: str):
        """Initialize executor with workspace."""
        self.workspace = workspace

    def execute_task(self, task: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a single pipeline task.

        Args:
            task: Task configuration
            context: Execution context (repo path, env vars, etc.)

        Returns:
            Task execution result
        """
        action = task.get("action")
        task_config = task.get("config", {})
        task_name = task.get("name", "unnamed_task")

        logger.info(f"Executing task: {task_name} (action: {action})")

        try:
            if action == "git_clone":
                return self._git_clone(context, task_config)
            elif action == "install":
                return self._install_dependencies(context, task_config)
            elif action == "build":
                return self._build_project(context, task_config)
            elif action == "test":
                return self._run_tests(context, task_config)
            elif action == "archive":
                return self._create_archive(context, task_config)
            elif action == "deploy":
                return self._deploy(context, task_config)
            elif action == "health_check":
                return self._health_check(context, task_config)
            else:
                return {"success": False, "error": f"Unknown action: {action}"}

        except Exception as e:
            logger.error(f"Task {task_name} failed: {e}")
            return {"success": False, "error": str(e)}

    def _git_clone(self, context: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Clone git repository."""
        repo_url = context.get("repository")
        branch = context.get("branch", "main")
        depth = config.get("depth", 1)

        repo_path = os.path.join(self.workspace, "repo")

        # Clean existing directory
        # Clean existing directory - validate path first
        if os.path.exists(repo_path):
            # Ensure repo_path is within workspace to prevent directory traversal
            if not os.path.commonpath([repo_path, self.workspace]) == self.workspace:
                return {"success": False, "error": "Invalid repository path"}
            shutil.rmtree(repo_path)

        logger.info(f"Cloning {repo_url} (branch: {branch})")

        try:
            git.Repo.clone_from(
                repo_url,
                repo_path,
                branch=branch,
                depth=depth if depth > 0 else None
            )
            context["repo_path"] = repo_path
            return {"success": True, "repo_path": repo_path}
        except Exception as e:
            return {"success": False, "error": f"Git clone failed: {e}"}

    def _install_dependencies(self, context: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Install project dependencies."""
        repo_path = context.get("repo_path", self.workspace)
        package_manager = config.get("package_manager", "auto_detect")

        # Auto-detect package manager
        if package_manager == "auto_detect":
            if os.path.exists(os.path.join(repo_path, "requirements.txt")):
                package_manager = "pip"
            elif os.path.exists(os.path.join(repo_path, "package.json")):
                package_manager = "npm"
            elif os.path.exists(os.path.join(repo_path, "go.mod")):
                package_manager = "go"
            elif os.path.exists(os.path.join(repo_path, "pom.xml")):
                package_manager = "maven"
            else:
                return {"success": True, "message": "No dependencies to install"}

        logger.info(f"Installing dependencies using {package_manager}")

        try:
            if package_manager == "pip":
                cmd = ["pip", "install", "-r", "requirements.txt"]
            elif package_manager == "npm":
                cmd = ["npm", "install"]
            elif package_manager == "go":
                cmd = ["go", "mod", "download"]
            elif package_manager == "maven":
                cmd = ["mvn", "dependency:resolve"]
            else:
                return {"success": False, "error": f"Unsupported package manager: {package_manager}"}

            result = subprocess.run(
                cmd,
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=600
            )

            if result.returncode == 0:
                return {"success": True, "output": result.stdout}
            else:
                return {"success": False, "error": result.stderr}

        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Dependency installation timed out"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _build_project(self, context: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Build the project."""
        repo_path = context.get("repo_path", self.workspace)
        build_tool = config.get("build_tool", "auto_detect")

        # Auto-detect build tool
        if build_tool == "auto_detect":
            if os.path.exists(os.path.join(repo_path, "setup.py")):
                build_tool = "python"
            elif os.path.exists(os.path.join(repo_path, "package.json")):
                build_tool = "npm"
            elif os.path.exists(os.path.join(repo_path, "Makefile")):
                build_tool = "make"
            else:
                return {"success": True, "message": "No build required"}

        logger.info(f"Building project using {build_tool}")

        try:
            if build_tool == "python":
                cmd = ["python", "setup.py", "build"]
            elif build_tool == "npm":
                cmd = ["npm", "run", "build"]
            elif build_tool == "make":
                cmd = ["make"]
            else:
                return {"success": False, "error": f"Unsupported build tool: {build_tool}"}

            result = subprocess.run(
                cmd,
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=1800
            )

            if result.returncode == 0:
                return {"success": True, "output": result.stdout}
            else:
                return {"success": False, "error": result.stderr, "stdout": result.stdout}

        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Build timed out"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _run_tests(self, context: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Run tests."""
        repo_path = context.get("repo_path", self.workspace)
        test_type = config.get("test_type", "all")

        logger.info(f"Running {test_type} tests")

        try:
            # Detect test framework
            if os.path.exists(os.path.join(repo_path, "pytest.ini")) or \
               os.path.exists(os.path.join(repo_path, "tests")):
                cmd = ["pytest", "-v"]
            elif os.path.exists(os.path.join(repo_path, "package.json")):
                cmd = ["npm", "test"]
            else:
                return {"success": True, "message": "No tests found"}

            result = subprocess.run(
                cmd,
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=3600
            )

            # Some test runners exit with non-zero even on success (e.g., no tests found)
            success = result.returncode == 0 or "no tests ran" in result.stdout.lower()

            return {
                "success": success,
                "output": result.stdout,
                "error": result.stderr if not success else None
            }

        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Tests timed out"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _create_archive(self, context: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Create artifact archive."""
        repo_path = context.get("repo_path", self.workspace)
        output_format = config.get("output_format", "tar.gz")

        artifact_name = f"artifact-{datetime.now().strftime('%Y%m%d-%H%M%S')}.{output_format}"
        artifact_path = os.path.join(self.workspace, artifact_name)

        logger.info(f"Creating artifact: {artifact_name}")

        try:
            shutil.make_archive(
                artifact_path.replace(f".{output_format}", ""),
                output_format.split('.')[0],
                repo_path
            )
            return {"success": True, "artifact_path": artifact_path}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _deploy(self, context: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Deploy to environment."""
        environment = config.get("environment", "staging")
        logger.info(f"Deploying to {environment}")

        # Placeholder for actual deployment logic
        # In a real implementation, this would integrate with deployment platforms
        return {
            "success": True,
            "environment": environment,
            "message": f"Deployed to {environment}"
        }

    def _health_check(self, context: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Perform health check."""
        endpoint = config.get("endpoint", "http://localhost:8080/health")
        logger.info(f"Health check: {endpoint}")

        # Placeholder for actual health check
        return {"success": True, "healthy": True}


class PipelineManager:
    """
    Manages pipeline execution and coordination.
    """

    def __init__(self, workspace: str = "/tmp/ai-cicd-workspace"):
        """Initialize the pipeline manager."""
        self.active_pipelines: Dict[str, Any] = {}
        self.workspace = workspace
        self.executor = PipelineExecutor(workspace)

        # Create workspace directory
        Path(workspace).mkdir(parents=True, exist_ok=True)

        logger.info("PipelineManager initialized")

    def execute_pipeline(
        self,
        pipeline_type: PipelineType,
        pipeline_def: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a specific pipeline.

        Args:
            pipeline_type: Type of pipeline to execute
            pipeline_def: Pipeline definition with stages and tasks
            context: Execution context (repo, branch, etc.)

        Returns:
            Pipeline execution result
        """
        pipeline_id = str(uuid.uuid4())

        pipeline_info = {
            "id": pipeline_id,
            "type": pipeline_type.value,
            "status": PipelineStatus.RUNNING,
            "start_time": datetime.now(),
            "stages": [],
            "context": context
        }

        self.active_pipelines[pipeline_id] = pipeline_info

        logger.info(f"Executing {pipeline_type.value} pipeline (ID: {pipeline_id})")

        try:
            stages = pipeline_def.get("stages", [])

            for stage in stages:
                stage_name = stage.get("name")
                stage_result = self._execute_stage(stage, context)

                pipeline_info["stages"].append(stage_result)

                if not stage_result["success"]:
                    logger.error(f"Stage '{stage_name}' failed")
                    pipeline_info["status"] = PipelineStatus.FAILED
                    pipeline_info["end_time"] = datetime.now()
                    pipeline_info["error"] = stage_result.get("error")

                    return pipeline_info

            # All stages succeeded
            pipeline_info["status"] = PipelineStatus.SUCCESS
            pipeline_info["end_time"] = datetime.now()
            logger.info(f"Pipeline {pipeline_id} completed successfully")

            return pipeline_info

        except Exception as e:
            logger.error(f"Pipeline {pipeline_id} failed with exception: {e}")
            pipeline_info["status"] = PipelineStatus.FAILED
            pipeline_info["end_time"] = datetime.now()
            pipeline_info["error"] = str(e)

            return pipeline_info

    def _execute_stage(self, stage: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a pipeline stage."""
        stage_name = stage.get("name")
        tasks = stage.get("tasks", [])

        logger.info(f"Executing stage: {stage_name}")

        stage_result = {
            "name": stage_name,
            "success": True,
            "tasks": []
        }

        for task in tasks:
            task_result = self.executor.execute_task(task, context)
            stage_result["tasks"].append(task_result)

            if not task_result.get("success", False):
                stage_result["success"] = False
                stage_result["error"] = task_result.get("error")
                break

        return stage_result

    def get_pipeline_status(self, pipeline_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the status of a specific pipeline.

        Args:
            pipeline_id: Unique identifier for the pipeline

        Returns:
            Pipeline status information or None if not found
        """
        return self.active_pipelines.get(pipeline_id)

    def cancel_pipeline(self, pipeline_id: str) -> bool:
        """
        Cancel a running pipeline.

        Args:
            pipeline_id: Unique identifier for the pipeline

        Returns:
            True if cancellation succeeds, False otherwise
        """
        logger.info(f"Cancelling pipeline {pipeline_id}")

        if pipeline_id in self.active_pipelines:
            pipeline = self.active_pipelines[pipeline_id]
            if pipeline["status"] == PipelineStatus.RUNNING:
                pipeline["status"] = PipelineStatus.CANCELLED
                pipeline["end_time"] = datetime.now()
                return True

        return False
