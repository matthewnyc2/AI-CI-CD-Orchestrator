import unittest
from unittest.mock import MagicMock, patch
from orchestrator.core.orchestrator import CICDOrchestrator
from orchestrator.core.pipeline_manager import PipelineManager, PipelineType
from monitors.pipeline_monitor import PipelineMonitor
from monitors.alerter import Alerter

class TestIntegration(unittest.TestCase):
    def setUp(self):
        self.config = {"pipeline_settings": "default", "alerter": {"channels": ["test"]}}
        self.orchestrator = CICDOrchestrator(self.config)
        self.pipeline_manager = PipelineManager()
        self.monitor = PipelineMonitor()
        self.alerter = Alerter(self.config["alerter"])

    def test_orchestrator_triggers_pipeline(self):
        # We want to verify that calling trigger_pipeline actually does something (e.g. logs)
        # without mocking the method itself.
        pipeline_type = "build"
        with self.assertLogs('orchestrator.core.orchestrator', level='INFO') as cm:
            self.orchestrator.trigger_pipeline(pipeline_type)
        self.assertIn(f"Triggering {pipeline_type} pipeline...", cm.output[0])

    def test_pipeline_execution_flow(self):
        # Simulate a pipeline execution flow
        pipeline_id = "test_pipeline_123"
        pipeline_type = PipelineType.BUILD

        # 1. Start tracking
        self.monitor.track_pipeline_start(pipeline_id, pipeline_type.value)
        metrics = self.monitor.get_metrics()
        self.assertEqual(len(metrics), 1)
        self.assertEqual(metrics[0]["status"], "running")

        # 2. Execute pipeline (simulated)
        success = self.pipeline_manager.execute_pipeline(pipeline_type, {})
        self.assertTrue(success)

        # 3. End tracking
        self.monitor.track_pipeline_end(pipeline_id, "success", 5.0)
        metrics = self.monitor.get_metrics()
        self.assertEqual(metrics[0]["status"], "success")

        # 4. Check Alerting (if failed, but here success)
        if metrics[0]["status"] != "success":
            self.alerter.send_pipeline_failure_alert(pipeline_id, pipeline_type.value, "error")
            self.assertEqual(len(self.alerter.alerts), 1)
        else:
            self.assertEqual(len(self.alerter.alerts), 0)

if __name__ == '__main__':
    unittest.main()
