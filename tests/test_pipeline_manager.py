import unittest
from unittest.mock import MagicMock
from orchestrator.core.pipeline_manager import PipelineManager, PipelineType

class TestPipelineManager(unittest.TestCase):
    def setUp(self):
        self.manager = PipelineManager()

    def test_initialization(self):
        self.assertEqual(self.manager.active_pipelines, {})

    def test_execute_pipeline(self):
        config = {"key": "value"}
        result = self.manager.execute_pipeline(PipelineType.BUILD, config)
        self.assertTrue(result)

    def test_get_pipeline_status(self):
        pipeline_id = "pipeline_1"
        self.manager.active_pipelines[pipeline_id] = {"status": "running"}
        status = self.manager.get_pipeline_status(pipeline_id)
        self.assertEqual(status, {"status": "running"})

    def test_get_pipeline_status_not_found(self):
        status = self.manager.get_pipeline_status("non_existent")
        self.assertIsNone(status)

    def test_cancel_pipeline(self):
        pipeline_id = "pipeline_1"
        result = self.manager.cancel_pipeline(pipeline_id)
        self.assertTrue(result)

if __name__ == '__main__':
    unittest.main()
