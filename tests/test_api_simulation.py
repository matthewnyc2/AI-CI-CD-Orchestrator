import unittest
from unittest.mock import MagicMock, patch
from orchestrator.core.orchestrator import CICDOrchestrator
from orchestrator.core.pipeline_manager import PipelineManager, PipelineType

class TestAPISimulation(unittest.TestCase):
    """
    Simulates API endpoint tests for the Orchestrator.
    Since there are no explicit web frameworks like Flask/Django,
    we treat public methods of the main classes as the "API".
    """

    def setUp(self):
        self.config = {"pipeline_settings": "default"}
        self.orchestrator = CICDOrchestrator(self.config)
        self.pipeline_manager = PipelineManager()

    def test_trigger_pipeline_api(self):
        """Test the 'trigger_pipeline' endpoint."""
        pipeline_type = "build"
        # Simulate API call
        with self.assertLogs('orchestrator.core.orchestrator', level='INFO') as cm:
            self.orchestrator.trigger_pipeline(pipeline_type)

        # Verify response/effect
        self.assertTrue(any(f"Triggering {pipeline_type} pipeline" in log for log in cm.output))

    def test_handle_failure_api(self):
        """Test the 'handle_failure' endpoint."""
        failure_data = {"error": "Critical failure"}
        # Simulate API call
        with self.assertLogs('orchestrator.core.orchestrator', level='ERROR') as cm:
            self.orchestrator.handle_failure(failure_data)

        # Verify response/effect
        self.assertTrue(any("Handling pipeline failure" in log for log in cm.output))

    def test_get_pipeline_status_api(self):
        """Test the 'get_pipeline_status' endpoint."""
        pipeline_id = "p-123"
        self.pipeline_manager.active_pipelines[pipeline_id] = {"status": "running"}

        # Simulate API call
        status = self.pipeline_manager.get_pipeline_status(pipeline_id)

        # Verify response
        self.assertEqual(status, {"status": "running"})

    def test_cancel_pipeline_api(self):
        """Test the 'cancel_pipeline' endpoint."""
        pipeline_id = "p-123"

        # Simulate API call
        with self.assertLogs('orchestrator.core.pipeline_manager', level='INFO') as cm:
            result = self.pipeline_manager.cancel_pipeline(pipeline_id)

        # Verify response
        self.assertTrue(result)
        self.assertTrue(any(f"Cancelling pipeline {pipeline_id}" in log for log in cm.output))

if __name__ == '__main__':
    unittest.main()
