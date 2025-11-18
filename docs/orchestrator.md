# Orchestrator Guide

This guide explains how to use and configure the orchestrator component.

## Overview

The orchestrator is the central component that manages the entire CI/CD workflow. It monitors code changes, triggers pipelines, handles failures, and coordinates AI-powered fixes.

## Configuration

### Basic Configuration

```yaml
orchestrator:
  # How often to check for code changes (seconds)
  polling_interval: 60
  
  # Maximum number of pipelines to run in parallel
  max_parallel_pipelines: 3
  
  # Enable auto-fix on failures
  auto_fix_enabled: true
  
  # Maximum number of auto-fix retries
  max_fix_retries: 3
```

### Advanced Configuration

```yaml
orchestrator:
  # Working directory for pipeline execution
  workspace: /tmp/cicd-workspace
  
  # Cache configuration
  cache:
    enabled: true
    ttl: 3600  # Cache TTL in seconds
    max_size: 1073741824  # 1GB
  
  # Resource limits
  resources:
    max_memory: "4GB"
    max_cpu_cores: 4
  
  # Timeout settings
  timeouts:
    build: 1800  # 30 minutes
    test: 3600   # 60 minutes
    deploy: 1200 # 20 minutes
```

## Usage

### Starting the Orchestrator

```python
from orchestrator.core.orchestrator import CICDOrchestrator

config = {
    "project": {
        "name": "my-app",
        "repository": "https://github.com/user/my-app.git"
    }
}

orchestrator = CICDOrchestrator(config)
orchestrator.start()
```

### Command Line

```bash
# Start with default configuration
python -m orchestrator.core.orchestrator

# Start with custom config file
python -m orchestrator.core.orchestrator --config config.yaml

# Start in daemon mode
python -m orchestrator.core.orchestrator --daemon

# Stop the orchestrator
python -m orchestrator.core.orchestrator --stop
```

## Monitoring Changes

The orchestrator monitors code changes through two methods:

### 1. Polling (Default)

Periodically checks the repository for new commits:

```yaml
orchestrator:
  monitoring:
    method: polling
    interval: 60
    branches:
      - main
      - develop
```

### 2. Webhooks

Receives push events from Git providers:

```yaml
orchestrator:
  monitoring:
    method: webhook
    port: 8080
    secret: ${WEBHOOK_SECRET}
```

## Triggering Pipelines

### Automatic Triggers

Pipelines are automatically triggered based on configuration:

```yaml
pipelines:
  build:
    trigger: on_commit  # Every commit
  test:
    trigger: after_build  # After successful build
  deploy:
    trigger: on_tag  # Only on tags (releases)
```

### Manual Triggers

```python
orchestrator.trigger_pipeline("build")
orchestrator.trigger_pipeline("test")
orchestrator.trigger_pipeline("deploy")
```

### API Triggers

```bash
# Trigger via REST API
curl -X POST http://localhost:8080/trigger/build \
  -H "Authorization: Bearer ${API_TOKEN}"
```

## Failure Handling

### Automatic Fix Workflow

When a pipeline fails:

1. Capture failure logs
2. Analyze with AI fixer
3. Generate and apply fix
4. Retry pipeline
5. Alert on success/failure

```yaml
orchestrator:
  failure_handling:
    auto_fix: true
    max_retries: 3
    escalate_after: 3
    notify_on_failure: true
```

### Manual Intervention

Disable auto-fix for manual control:

```yaml
orchestrator:
  failure_handling:
    auto_fix: false
    pause_on_failure: true
```

## Workflow Customization

### Custom Workflow

Define a custom workflow:

```python
from orchestrator.core.orchestrator import CICDOrchestrator
from orchestrator.core.pipeline_manager import PipelineType

orchestrator = CICDOrchestrator(config)

# Custom workflow
def custom_workflow():
    # Build
    if orchestrator.trigger_pipeline("build"):
        # Run only unit tests
        if orchestrator.trigger_pipeline("test", {"type": "unit"}):
            # Deploy to staging only
            orchestrator.trigger_pipeline("deploy", {
                "environment": "staging"
            })

orchestrator.register_workflow("custom", custom_workflow)
orchestrator.start_workflow("custom")
```

### Conditional Execution

```python
def conditional_deploy():
    # Only deploy on main branch
    if git_branch == "main":
        if all_tests_pass():
            orchestrator.trigger_pipeline("deploy", {
                "environment": "production"
            })
```

## State Management

### Pipeline State

Track pipeline execution state:

```python
# Get current state
state = orchestrator.get_state()

# Check if pipeline is running
is_running = orchestrator.is_pipeline_running("build")

# Get pipeline history
history = orchestrator.get_pipeline_history("build", limit=10)
```

### Persistence

Enable state persistence:

```yaml
orchestrator:
  persistence:
    enabled: true
    backend: redis
    redis:
      host: localhost
      port: 6379
      db: 0
```

## Logging

### Configure Logging

```yaml
logging:
  level: INFO
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  handlers:
    - type: file
      filename: orchestrator.log
      max_bytes: 10485760  # 10MB
      backup_count: 5
    - type: console
```

### Access Logs

```python
import logging

logger = logging.getLogger("orchestrator")
logger.info("Starting orchestrator")
```

## Performance Tuning

### Optimize for Speed

```yaml
orchestrator:
  optimization:
    parallel_execution: true
    cache_dependencies: true
    incremental_builds: true
    skip_unchanged_tests: true
```

### Optimize for Reliability

```yaml
orchestrator:
  optimization:
    parallel_execution: false
    retry_failed_tests: true
    verify_fixes: true
    thorough_health_checks: true
```

## Best Practices

1. **Use Specific Triggers**: Don't run all pipelines on every commit
2. **Enable Caching**: Speed up builds with dependency caching
3. **Set Appropriate Timeouts**: Prevent hanging pipelines
4. **Monitor Resources**: Ensure adequate CPU and memory
5. **Test Auto-Fixes**: Verify fixes in staging before production
6. **Use Webhooks**: More efficient than polling for active repos
7. **Enable Logging**: Essential for debugging issues
8. **Configure Alerts**: Get notified of critical failures

## Troubleshooting

### Orchestrator Won't Start

```bash
# Check configuration
python -m orchestrator.core.orchestrator --validate-config

# Check logs
tail -f orchestrator.log
```

### Pipelines Not Triggering

1. Verify repository access
2. Check trigger configuration
3. Review monitoring logs
4. Validate webhook configuration

### High Resource Usage

1. Reduce max_parallel_pipelines
2. Enable incremental builds
3. Optimize test execution
4. Review cache settings

## Examples

See the [examples directory](../examples/README.md) for complete working examples.
