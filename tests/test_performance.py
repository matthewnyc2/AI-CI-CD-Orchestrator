import unittest
import time
from orchestrator.core.pipeline_manager import PipelineManager, PipelineType

class TestPerformance(unittest.TestCase):
    def setUp(self):
        self.manager = PipelineManager()

    def test_pipeline_execution_performance(self):
        """
        Test that pipeline execution overhead is minimal.
        """
        start_time = time.time()

        # Execute a simple pipeline multiple times
        iterations = 1000
        for _ in range(iterations):
            self.manager.execute_pipeline(PipelineType.BUILD, {})

        end_time = time.time()
        duration = end_time - start_time

        # Expectation: 1000 simulated executions should be very fast (< 1 second)
        # since they are just logging and returning True.
        self.assertLess(duration, 1.0, f"Performance test failed: took {duration}s for {iterations} iterations")

    def test_metrics_tracking_performance(self):
        """
        Test performance of metrics tracking (simulating high load).
        """
        from monitors.pipeline_monitor import PipelineMonitor
        monitor = PipelineMonitor()

        start_time = time.time()
        iterations = 10000

        for i in range(iterations):
            monitor.track_pipeline_start(f"p-{i}", "build")

        end_time = time.time()
        duration = end_time - start_time

        # Expectation: Adding 10000 metrics should be fast (< 1 second)
        self.assertLess(duration, 1.0, f"Metrics performance test failed: took {duration}s for {iterations} iterations")

if __name__ == '__main__':
    unittest.main()
