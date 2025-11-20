import unittest
from pipelines.build.build_pipeline import build_pipeline
from pipelines.test.test_pipeline import test_pipeline
from pipelines.deploy.deploy_pipeline import deploy_pipeline

class TestPipelinesConfig(unittest.TestCase):

    def validate_pipeline_structure(self, pipeline):
        self.assertIn("name", pipeline)
        self.assertIn("version", pipeline)
        self.assertIn("stages", pipeline)
        self.assertIsInstance(pipeline["stages"], list)
        self.assertIn("on_failure", pipeline)

        for stage in pipeline["stages"]:
            self.assertIn("name", stage)
            self.assertIn("tasks", stage)
            self.assertIsInstance(stage["tasks"], list)

            for task in stage["tasks"]:
                self.assertIn("name", task)
                self.assertIn("action", task)
                self.assertIn("config", task)

    def test_build_pipeline_structure(self):
        self.validate_pipeline_structure(build_pipeline)
        self.assertEqual(build_pipeline["name"], "build")

    def test_test_pipeline_structure(self):
        self.validate_pipeline_structure(test_pipeline)
        self.assertEqual(test_pipeline["name"], "test")

    def test_deploy_pipeline_structure(self):
        self.validate_pipeline_structure(deploy_pipeline)
        self.assertEqual(deploy_pipeline["name"], "deploy")

if __name__ == '__main__':
    unittest.main()
