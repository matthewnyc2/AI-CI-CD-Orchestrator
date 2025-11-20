import unittest
from unittest.mock import MagicMock
from monitors.alerter import Alerter, AlertLevel
from monitors.pipeline_monitor import PipelineMonitor
from monitors.health_checker import HealthChecker

class TestAlerter(unittest.TestCase):
    def setUp(self):
        self.config = {"channels": ["slack"]}
        self.alerter = Alerter(self.config)

    def test_send_alert(self):
        self.alerter.send_alert(AlertLevel.INFO, "Test Title", "Test Message")
        self.assertEqual(len(self.alerter.alerts), 1)
        self.assertEqual(self.alerter.alerts[0]["title"], "Test Title")

    def test_send_pipeline_failure_alert(self):
        self.alerter.send_pipeline_failure_alert("p1", "build", "error msg")
        self.assertEqual(len(self.alerter.alerts), 1)
        self.assertEqual(self.alerter.alerts[0]["level"], AlertLevel.ERROR)

    def test_send_deployment_alert_success(self):
        self.alerter.send_deployment_alert("prod", "success", "deployed")
        self.assertEqual(len(self.alerter.alerts), 1)
        self.assertEqual(self.alerter.alerts[0]["level"], AlertLevel.INFO)

    def test_send_deployment_alert_failure(self):
        self.alerter.send_deployment_alert("prod", "failed", "error")
        self.assertEqual(len(self.alerter.alerts), 1)
        self.assertEqual(self.alerter.alerts[0]["level"], AlertLevel.CRITICAL)

    def test_get_alerts(self):
        self.alerter.send_alert(AlertLevel.INFO, "Info Alert", "msg")
        self.alerter.send_alert(AlertLevel.ERROR, "Error Alert", "msg")

        info_alerts = self.alerter.get_alerts(AlertLevel.INFO)
        self.assertEqual(len(info_alerts), 1)

        all_alerts = self.alerter.get_alerts()
        self.assertEqual(len(all_alerts), 2)

class TestPipelineMonitor(unittest.TestCase):
    def setUp(self):
        self.monitor = PipelineMonitor()

    def test_track_pipeline_lifecycle(self):
        self.monitor.track_pipeline_start("p1", "build")
        self.assertEqual(len(self.monitor.metrics), 1)
        self.assertEqual(self.monitor.metrics[0]["status"], "running")

        self.monitor.track_pipeline_end("p1", "success", 10.5)
        self.assertEqual(self.monitor.metrics[0]["status"], "success")
        self.assertEqual(self.monitor.metrics[0]["duration"], 10.5)

    def test_get_success_rate(self):
        self.monitor.metrics = [
            {"status": "success"},
            {"status": "success"},
            {"status": "failure"},
            {"status": "running"} # Should be ignored
        ]
        rate = self.monitor.get_success_rate()
        self.assertAlmostEqual(rate, 66.66666666666666)

    def test_get_success_rate_empty(self):
        self.assertEqual(self.monitor.get_success_rate(), 0.0)

class TestHealthChecker(unittest.TestCase):
    def setUp(self):
        self.checker = HealthChecker()

    def test_register_component(self):
        self.checker.register_component("comp1", lambda: True)
        self.assertIn("comp1", self.checker.components)

    def test_check_health_all_healthy(self):
        self.checker.register_component("comp1", lambda: True)
        self.checker.register_component("comp2", lambda: True)
        report = self.checker.check_health()
        self.assertEqual(report["overall_status"], "healthy")
        self.assertEqual(report["components"]["comp1"], "healthy")

    def test_check_health_degraded(self):
        self.checker.register_component("comp1", lambda: True)
        self.checker.register_component("comp2", lambda: False)
        report = self.checker.check_health()
        self.assertEqual(report["overall_status"], "degraded")
        self.assertEqual(report["components"]["comp2"], "unhealthy")

    def test_check_health_exception(self):
        def raise_error():
            raise Exception("error")
        self.checker.register_component("comp1", raise_error)
        report = self.checker.check_health()
        self.assertEqual(report["overall_status"], "degraded")
        self.assertEqual(report["components"]["comp1"], "error")

    def test_get_component_status(self):
        self.checker.register_component("comp1", lambda: True)
        self.assertEqual(self.checker.get_component_status("comp1"), "unknown") # Before check
        self.checker.check_health()
        self.assertEqual(self.checker.get_component_status("comp1"), "healthy")

if __name__ == '__main__':
    unittest.main()
