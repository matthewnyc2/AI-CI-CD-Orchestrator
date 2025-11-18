# Example Workflows

This directory contains example workflows demonstrating various CI/CD scenarios.

## Examples

### 1. Simple Python Workflow (`simple_python_workflow.py`)
A basic CI/CD workflow for a Python project demonstrating:
- Build pipeline execution
- Test pipeline execution
- Deployment to multiple environments
- Monitoring and alerting

**Usage:**
```bash
python examples/simple_python_workflow.py
```

### 2. AI Auto-Fix Workflow (`ai_auto_fix_workflow.py`)
Demonstrates AI-powered automatic failure resolution:
- Automatic detection of build failures
- AI analysis of failure logs
- Automatic fix generation and application
- Retry mechanism with verification

**Usage:**
```bash
python examples/ai_auto_fix_workflow.py
```

### 3. Multi-Environment Deployment (`multi_env_deployment.py`)
Shows deployment to multiple environments with health checks:
- Staging deployment with health verification
- Production deployment with canary releases
- Automatic rollback on failure
- Health monitoring across environments

**Usage:**
```bash
python examples/multi_env_deployment.py
```

## Getting Started

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure your settings in each example file

3. Run the examples to see the CI/CD system in action

## Customization

Each example can be customized by modifying the `config` dictionary:
- Change repository URLs
- Adjust pipeline settings
- Configure alert channels
- Modify deployment strategies
