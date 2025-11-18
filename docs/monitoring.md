# Monitoring & Alerts

This guide covers monitoring pipeline execution and configuring alerts.

## Overview

The monitoring system tracks:
- Pipeline execution metrics
- System health
- Resource usage
- Failure patterns

## Pipeline Monitoring

### Metrics Collection

```python
from monitors.pipeline_monitor import PipelineMonitor

monitor = PipelineMonitor()

# Track pipeline execution
monitor.track_pipeline_start(pipeline_id, "build")
# ... pipeline runs ...
monitor.track_pipeline_end(pipeline_id, "success", duration)

# Get metrics
metrics = monitor.get_metrics()
success_rate = monitor.get_success_rate()
```

### Available Metrics

- **Execution Time**: Duration of each pipeline run
- **Success Rate**: Percentage of successful runs
- **Failure Rate**: Percentage of failed runs
- **Queue Time**: Time spent waiting for execution
- **Resource Usage**: CPU, memory, disk usage

### Metrics Dashboard

Access metrics via the built-in dashboard:

```bash
# Start metrics server
python -m monitors.metrics_server --port 9090
```

Visit `http://localhost:9090/metrics` to view dashboard.

## Health Monitoring

### Health Checks

```python
from monitors.health_checker import HealthChecker

health_checker = HealthChecker()

# Register components
health_checker.register_component("database", check_db_health)
health_checker.register_component("api", check_api_health)

# Check health
health_status = health_checker.check_health()
```

### Health Check Configuration

```yaml
health_checks:
  enabled: true
  interval: 30  # Check every 30 seconds
  
  components:
    - name: database
      type: tcp
      host: localhost
      port: 5432
      timeout: 5
    
    - name: api
      type: http
      url: http://localhost:8080/health
      expected_status: 200
      timeout: 10
    
    - name: disk_space
      type: system
      metric: disk_usage
      threshold: 90  # Alert if >90% used
```

## Alerting

### Alert Configuration

```yaml
alerts:
  channels:
    - type: email
      enabled: true
      recipients:
        - team@example.com
        - oncall@example.com
      smtp:
        host: smtp.gmail.com
        port: 587
        username: ${SMTP_USER}
        password: ${SMTP_PASS}
    
    - type: slack
      enabled: true
      webhook_url: ${SLACK_WEBHOOK}
      channel: "#ci-cd-alerts"
      mention_on_failure: "@channel"
    
    - type: pagerduty
      enabled: true
      service_key: ${PAGERDUTY_KEY}
      severity_threshold: critical
```

### Alert Levels

- **INFO**: Informational messages (deployment success)
- **WARNING**: Non-critical issues (slow pipeline)
- **ERROR**: Pipeline failures
- **CRITICAL**: System-wide issues

### Sending Alerts

```python
from monitors.alerter import Alerter, AlertLevel

alerter = Alerter(config)

# Pipeline failure
alerter.send_pipeline_failure_alert(
    pipeline_id="build-123",
    pipeline_type="build",
    error="Compilation failed"
)

# Deployment notification
alerter.send_deployment_alert(
    environment="production",
    status="success",
    details="Version 1.2.3 deployed"
)

# Custom alert
alerter.send_alert(
    level=AlertLevel.WARNING,
    title="High Resource Usage",
    message="CPU usage at 85%",
    metadata={"cpu_percent": 85}
)
```

### Alert Rules

Define custom alert rules:

```yaml
alert_rules:
  - name: high_failure_rate
    condition: pipeline_failure_rate > 0.5
    duration: 300  # 5 minutes
    severity: error
    message: "Pipeline failure rate exceeded 50%"
    notify:
      - team@example.com
      - "#ci-cd-alerts"
  
  - name: slow_pipeline
    condition: pipeline_duration > 1800
    severity: warning
    message: "Pipeline execution taking longer than 30 minutes"
  
  - name: deployment_to_production
    condition: deployment.environment == "production"
    severity: info
    message: "Production deployment initiated"
    notify:
      - all-hands@example.com
```

## Logging

### Log Configuration

```yaml
logging:
  level: INFO
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  
  handlers:
    - type: file
      filename: cicd.log
      max_bytes: 10485760  # 10MB
      backup_count: 5
      level: DEBUG
    
    - type: console
      level: INFO
    
    - type: syslog
      address: localhost:514
      level: WARNING
```

### Log Aggregation

Forward logs to aggregation services:

```yaml
logging:
  aggregation:
    - type: elasticsearch
      hosts: ["localhost:9200"]
      index: cicd-logs
    
    - type: cloudwatch
      log_group: /aws/cicd
      log_stream: orchestrator
```

## Metrics Export

### Prometheus

Export metrics for Prometheus:

```yaml
metrics:
  prometheus:
    enabled: true
    port: 9090
    path: /metrics
```

Metrics exposed:
- `cicd_pipeline_duration_seconds`
- `cicd_pipeline_success_total`
- `cicd_pipeline_failure_total`
- `cicd_queue_size`

### Custom Metrics

Define custom metrics:

```python
from monitors.pipeline_monitor import PipelineMonitor

monitor = PipelineMonitor()

# Record custom metric
monitor.record_metric(
    "test_coverage",
    value=85.5,
    labels={"project": "my-app", "branch": "main"}
)
```

## Performance Monitoring

### Track Performance

```python
from monitors.pipeline_monitor import PipelineMonitor
import time

monitor = PipelineMonitor()

# Measure stage performance
start = time.time()
# ... stage execution ...
duration = time.time() - start

monitor.record_stage_duration(
    pipeline_id="build-123",
    stage_name="compile",
    duration=duration
)
```

### Performance Thresholds

Set performance thresholds:

```yaml
performance:
  thresholds:
    build:
      warning: 600   # 10 minutes
      critical: 1200 # 20 minutes
    test:
      warning: 900   # 15 minutes
      critical: 1800 # 30 minutes
    deploy:
      warning: 300   # 5 minutes
      critical: 600  # 10 minutes
```

## Troubleshooting

### Debug Mode

Enable debug logging:

```bash
python -m orchestrator.core.orchestrator --log-level DEBUG
```

### View Recent Alerts

```python
alerter = Alerter(config)

# Get all alerts
all_alerts = alerter.get_alerts()

# Get only errors
errors = alerter.get_alerts(level="error")
```

### Check Health Status

```bash
# Via CLI
python -m monitors.health_checker --check-all

# Via API
curl http://localhost:9090/health
```

## Best Practices

1. **Set Appropriate Alert Thresholds**: Avoid alert fatigue
2. **Use Alert Aggregation**: Group related alerts
3. **Monitor Trends**: Track metrics over time
4. **Set Up Dashboards**: Visualize key metrics
5. **Regular Health Checks**: Ensure system reliability
6. **Log Everything Important**: Detailed logs help debugging
7. **Use Structured Logging**: Makes parsing easier
8. **Archive Old Logs**: Manage disk space

## Examples

See [examples directory](../examples/README.md) for monitoring examples.
