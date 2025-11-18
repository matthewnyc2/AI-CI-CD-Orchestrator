"""
Test pipeline configuration and execution.
"""

test_pipeline = {
    "name": "test",
    "version": "1.0",
    "stages": [
        {
            "name": "setup",
            "tasks": [
                {
                    "name": "prepare_environment",
                    "action": "setup_test_env",
                    "config": {
                        "test_database": True,
                        "test_services": []
                    }
                }
            ]
        },
        {
            "name": "unit_tests",
            "tasks": [
                {
                    "name": "run_unit_tests",
                    "action": "test",
                    "config": {
                        "test_type": "unit",
                        "parallel": True,
                        "coverage": True
                    }
                }
            ]
        },
        {
            "name": "integration_tests",
            "tasks": [
                {
                    "name": "run_integration_tests",
                    "action": "test",
                    "config": {
                        "test_type": "integration",
                        "timeout": 300
                    }
                }
            ]
        },
        {
            "name": "reports",
            "tasks": [
                {
                    "name": "generate_reports",
                    "action": "report",
                    "config": {
                        "formats": ["html", "xml", "json"],
                        "coverage_threshold": 80
                    }
                }
            ]
        }
    ],
    "on_failure": {
        "action": "trigger_ai_fixer",
        "capture_logs": True,
        "retry_count": 2
    }
}
