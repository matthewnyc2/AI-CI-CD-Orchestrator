import unittest
from unittest.mock import MagicMock, patch
from orchestrator.core.orchestrator import CICDOrchestrator

class TestCICDOrchestrator(unittest.TestCase):
    def setUp(self):
        self.config = {"pipeline_settings": "default"}
        self.orchestrator = CICDOrchestrator(self.config)

    def test_initialization(self):
        self.assertEqual(self.orchestrator.config, self.config)
        self.assertEqual(self.orchestrator.pipelines, [])

    def test_start(self):
        with self.assertLogs('orchestrator.core.orchestrator', level='INFO') as cm:
            self.orchestrator.start()
        self.assertIn("Starting CI/CD orchestration...", cm.output[0])

    def test_stop(self):
        with self.assertLogs('orchestrator.core.orchestrator', level='INFO') as cm:
            self.orchestrator.stop()
        self.assertIn("Stopping CI/CD orchestration...", cm.output[0])

    def test_monitor_changes(self):
        with self.assertLogs('orchestrator.core.orchestrator', level='INFO') as cm:
            self.orchestrator.monitor_changes()
        self.assertIn("Monitoring for code changes...", cm.output[0])

    def test_trigger_pipeline(self):
        pipeline_type = "build"
        with self.assertLogs('orchestrator.core.orchestrator', level='INFO') as cm:
            self.orchestrator.trigger_pipeline(pipeline_type)
        self.assertIn(f"Triggering {pipeline_type} pipeline...", cm.output[0])

    def test_handle_failure(self):
        failure_data = {"error": "build failed"}
        with self.assertLogs('orchestrator.core.orchestrator', level='ERROR') as cm:
            self.orchestrator.handle_failure(failure_data)
        self.assertIn(f"Handling pipeline failure: {failure_data}", cm.output[0])

if __name__ == '__main__':
    unittest.main()
