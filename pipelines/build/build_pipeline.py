"""
Build pipeline configuration and execution.
"""

build_pipeline = {
    "name": "build",
    "version": "1.0",
    "stages": [
        {
            "name": "checkout",
            "tasks": [
                {
                    "name": "clone_repository",
                    "action": "git_clone",
                    "config": {
                        "depth": 1
                    }
                }
            ]
        },
        {
            "name": "dependencies",
            "tasks": [
                {
                    "name": "install_dependencies",
                    "action": "install",
                    "config": {
                        "package_manager": "auto_detect"
                    }
                }
            ]
        },
        {
            "name": "compile",
            "tasks": [
                {
                    "name": "build_project",
                    "action": "build",
                    "config": {
                        "build_tool": "auto_detect",
                        "parallel": True
                    }
                }
            ]
        },
        {
            "name": "artifacts",
            "tasks": [
                {
                    "name": "create_artifacts",
                    "action": "archive",
                    "config": {
                        "output_format": "tar.gz"
                    }
                }
            ]
        }
    ],
    "on_failure": {
        "action": "trigger_ai_fixer",
        "retry_count": 3
    }
}
