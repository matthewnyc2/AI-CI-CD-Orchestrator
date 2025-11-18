# Monitoring Tools

This directory contains monitoring and alerting tools for the CI/CD system.

## Components

### Pipeline Monitor
Tracks pipeline execution metrics, including:
- Pipeline start/end times
- Success/failure rates
- Execution duration
- Resource usage

### Health Checker
Monitors the health of system components:
- Orchestrator status
- Pipeline runner status
- Database connectivity
- External service availability

### Alerter
Sends alerts for important events:
- Pipeline failures
- Deployment status
- System health issues
- Performance degradation

## Usage

```python
from monitors.pipeline_monitor import PipelineMonitor
from monitors.health_checker import HealthChecker
from monitors.alerter import Alerter

# Initialize monitors
monitor = PipelineMonitor()
health_checker = HealthChecker()
alerter = Alerter(config)

# Track pipeline execution
monitor.track_pipeline_start(pipeline_id, "build")
# ... pipeline runs ...
monitor.track_pipeline_end(pipeline_id, "success", duration)

# Check system health
health_status = health_checker.check_health()

# Send alerts
alerter.send_pipeline_failure_alert(pipeline_id, "test", error_msg)
```
