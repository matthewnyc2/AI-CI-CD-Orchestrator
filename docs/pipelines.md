# Pipeline Configuration

This guide explains how to configure and customize pipelines.

## Pipeline Overview

The system supports three main pipeline types:
- **Build Pipeline**: Compile code and create artifacts
- **Test Pipeline**: Run automated tests
- **Deploy Pipeline**: Deploy to environments

## Pipeline Structure

Each pipeline consists of stages, which contain tasks:

```python
pipeline = {
    "name": "build",
    "version": "1.0",
    "stages": [
        {
            "name": "stage_name",
            "tasks": [
                {
                    "name": "task_name",
                    "action": "action_type",
                    "config": {}
                }
            ]
        }
    ]
}
```

## Build Pipeline

### Default Configuration

```python
build_pipeline = {
    "name": "build",
    "stages": [
        {
            "name": "checkout",
            "tasks": [{"name": "clone", "action": "git_clone"}]
        },
        {
            "name": "dependencies",
            "tasks": [{"name": "install", "action": "install"}]
        },
        {
            "name": "compile",
            "tasks": [{"name": "build", "action": "build"}]
        }
    ]
}
```

### Customization

```python
# Add linting stage
build_pipeline["stages"].insert(2, {
    "name": "lint",
    "tasks": [
        {"name": "pylint", "action": "lint", "config": {"tool": "pylint"}},
        {"name": "mypy", "action": "type_check", "config": {"tool": "mypy"}}
    ]
})
```

## Test Pipeline

### Test Types

```yaml
test_pipeline:
  stages:
    - name: unit_tests
      parallel: true
      tasks:
        - name: run_unit_tests
          action: test
          config:
            type: unit
            coverage: true
            threshold: 80
    
    - name: integration_tests
      tasks:
        - name: run_integration_tests
          action: test
          config:
            type: integration
            requires:
              - database
              - redis
    
    - name: e2e_tests
      tasks:
        - name: run_e2e_tests
          action: test
          config:
            type: e2e
            browser: chrome
            headless: true
```

## Deploy Pipeline

### Deployment Strategies

#### Blue-Green Deployment

```python
deploy_config = {
    "strategy": "blue_green",
    "environments": {
        "production": {
            "blue": "prod-blue.example.com",
            "green": "prod-green.example.com",
            "switch_timeout": 60
        }
    }
}
```

#### Rolling Deployment

```python
deploy_config = {
    "strategy": "rolling",
    "batch_size": 2,
    "health_check_interval": 30,
    "max_unavailable": 1
}
```

#### Canary Deployment

```python
deploy_config = {
    "strategy": "canary",
    "canary_percentage": 10,
    "monitoring_duration": 300,
    "success_criteria": {
        "error_rate": 0.01,
        "latency_p95": 500
    }
}
```

## Custom Actions

Define custom actions for tasks:

```python
from orchestrator.core.pipeline_manager import PipelineManager

pipeline_manager = PipelineManager()

@pipeline_manager.register_action("custom_build")
def custom_build(config):
    # Custom build logic
    print("Running custom build...")
    return True

# Use in pipeline
task = {
    "name": "special_build",
    "action": "custom_build",
    "config": {"option": "value"}
}
```

## Conditional Stages

Execute stages conditionally:

```python
stage = {
    "name": "deploy_production",
    "condition": "branch == 'main' and tests_passed",
    "tasks": [...]
}
```

## Parallel Execution

Run tasks in parallel:

```python
stage = {
    "name": "parallel_tests",
    "parallel": True,
    "tasks": [
        {"name": "test_module_a", "action": "test"},
        {"name": "test_module_b", "action": "test"},
        {"name": "test_module_c", "action": "test"}
    ]
}
```

## Environment Variables

Use environment variables in pipelines:

```python
task = {
    "name": "deploy",
    "action": "deploy",
    "config": {
        "api_key": "${API_KEY}",
        "region": "${AWS_REGION}"
    }
}
```

## Artifacts

Handle build artifacts:

```python
{
    "name": "artifacts",
    "tasks": [
        {
            "name": "create_artifacts",
            "action": "archive",
            "config": {
                "files": ["dist/*", "build/*"],
                "output": "artifacts.tar.gz",
                "compression": "gzip"
            }
        },
        {
            "name": "upload_artifacts",
            "action": "upload",
            "config": {
                "destination": "s3://bucket/artifacts/"
            }
        }
    ]
}
```

## Failure Handling

Configure failure behavior:

```python
pipeline = {
    "name": "build",
    "stages": [...],
    "on_failure": {
        "action": "trigger_ai_fixer",
        "retry_count": 3,
        "notify": ["team@example.com"],
        "rollback": True
    }
}
```

## Best Practices

1. **Keep Pipelines Simple**: Break complex workflows into stages
2. **Use Caching**: Cache dependencies and build outputs
3. **Parallelize When Possible**: Run independent tasks in parallel
4. **Set Timeouts**: Prevent hanging pipelines
5. **Use Artifacts**: Share outputs between stages
6. **Test Pipelines**: Validate pipeline configurations before deploying
7. **Version Pipelines**: Track pipeline configuration changes
8. **Monitor Performance**: Track execution times and optimize

## Examples

See [examples directory](../examples/README.md) for complete pipeline examples.
