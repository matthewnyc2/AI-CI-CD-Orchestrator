# Getting Started

This guide will help you set up and run the AI-CI-CD-Orchestrator for your projects.

## Installation

### Prerequisites

- Python 3.8+
- Git
- pip or poetry for dependency management

### Step 1: Clone the Repository

```bash
git clone https://github.com/matthewnyc2/AI-CI-CD-Orchestrator.git
cd AI-CI-CD-Orchestrator
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

Or using poetry:

```bash
poetry install
```

### Step 3: Configure the System

Create a configuration file:

```bash
cp config.example.yaml config.yaml
```

Edit `config.yaml` with your settings:

```yaml
project:
  name: my-project
  repository: https://github.com/user/my-project.git
  language: python
  version: "3.9"

orchestrator:
  polling_interval: 60  # Check for changes every 60 seconds
  max_parallel_pipelines: 3

pipelines:
  build:
    enabled: true
    trigger: on_commit
  test:
    enabled: true
    trigger: after_build
  deploy:
    enabled: true
    trigger: on_tag

llm:
  provider: openai
  model: gpt-4
  api_key: ${OPENAI_API_KEY}
  max_retries: 3

monitoring:
  enabled: true
  metrics_port: 9090

alerts:
  channels:
    - type: email
      recipients: ["team@example.com"]
    - type: slack
      webhook_url: ${SLACK_WEBHOOK}
```

### Step 4: Set Environment Variables

```bash
export OPENAI_API_KEY="your-api-key"
export SLACK_WEBHOOK="your-slack-webhook-url"
```

### Step 5: Run the Orchestrator

```bash
python -m orchestrator.core.orchestrator
```

Or run in the background:

```bash
nohup python -m orchestrator.core.orchestrator &
```

## Verify Installation

Run a test workflow:

```bash
python examples/simple_python_workflow.py
```

## Next Steps

- [Configure pipelines](pipelines.md)
- [Set up monitoring](monitoring.md)
- [Configure AI fixers](fixers.md)
- [Review examples](../examples/README.md)

## Troubleshooting

### Common Issues

**Issue: Module not found errors**
```bash
# Make sure you're in the right directory and dependencies are installed
pip install -r requirements.txt
```

**Issue: API key errors**
```bash
# Verify environment variables are set
echo $OPENAI_API_KEY
```

**Issue: Permission errors**
```bash
# Ensure scripts have execute permissions
chmod +x scripts/*.sh
```

For more help, see the [FAQ](faq.md) or open an issue on GitHub.
