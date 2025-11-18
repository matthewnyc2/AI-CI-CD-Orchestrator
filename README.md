# AI-CI-CD-Orchestrator

A fully autonomous CI/CD system driven by AI that monitors code changes, runs builds and tests, detects failures, and applies fixes using LLMs, ensuring zero-downtime deployments.

## Features

- **Autonomous Monitoring**: Continuously monitors Git repositories for code changes
- **Automated Pipelines**: Runs build, test, and deployment pipelines automatically
- **AI-Powered Fixes**: Uses LLMs (Claude/GPT-4) to analyze failures and generate fixes
- **Specialized Fixers**: Domain-specific fixers for build, test, and deployment issues
- **Real-time Alerts**: Multi-channel alerting (console, email, Slack)
- **Metrics & Monitoring**: Comprehensive pipeline metrics and health checks
- **Zero-Downtime Deployments**: Smart deployment strategies with health checks
- **Configurable**: Flexible YAML-based configuration

## Architecture

```
┌─────────────────────────────────────────────────┐
│          CICDOrchestrator (Main Controller)      │
│  - Monitors Git changes                          │
│  - Coordinates pipelines                         │
│  - Manages AI-powered fixes                      │
└─────────────┬───────────────────────────────────┘
              │
    ┌─────────┼──────────┬──────────────┐
    ▼         ▼          ▼              ▼
┌──────────┐ ┌────────┐ ┌─────────┐ ┌─────────┐
│ Pipeline │ │ AI     │ │Monitors │ │ Alerts  │
│ Manager  │ │ Fixers │ │         │ │         │
└──────────┘ └────────┘ └─────────┘ └─────────┘
    │           │          │            │
    ├─►BUILD    ├─►AIFixer ├─►Metrics   ├─►Email
    ├─►TEST     ├─►Build   ├─►Health    ├─►Slack
    └─►DEPLOY   └─►Test    └─►Alerter   └─►Console
```

## Quick Start

### Prerequisites

- Python 3.8 or higher
- Git
- API key for Anthropic (Claude) or OpenAI (GPT-4)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/matthewnyc2/AI-CI-CD-Orchestrator.git
cd AI-CI-CD-Orchestrator
```

2. Install the package:
```bash
pip install -e .
```

Or install with dev dependencies:
```bash
pip install -e ".[dev]"
```

3. Create configuration:
```bash
ai-cicd init
```

This creates a `config.yaml` file. Edit it with your settings.

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env and add your API keys
```

### Configuration

Edit `config.yaml` to configure your project:

```yaml
project:
  name: "my-project"
  repository: "https://github.com/username/my-project"
  branch: "main"
  language: "python"
  workspace: "/tmp/ai-cicd-workspace"

llm:
  provider: "anthropic"  # or "openai"
  model: "claude-3-5-sonnet-20241022"
  api_key: "${ANTHROPIC_API_KEY}"

orchestrator:
  polling_interval: 60
  auto_fix_enabled: true
  max_fix_attempts: 3
```

See `config.example.yaml` for all available options.

## Usage

### Start the Orchestrator

Start monitoring and auto-fixing:
```bash
ai-cicd start
```

Start in daemon mode:
```bash
ai-cicd start --daemon
```

### Run a Single Pipeline

Run a specific pipeline once:
```bash
ai-cicd run build
ai-cicd run test
ai-cicd run deploy
```

### Check Status

View orchestrator configuration and status:
```bash
ai-cicd status
```

### Validate Configuration

Validate your configuration file:
```bash
ai-cicd validate
```

## How It Works

### 1. Git Monitoring

The orchestrator continuously monitors your Git repository for changes:

- Polls the repository at configurable intervals
- Detects new commits on monitored branches
- Automatically triggers CI/CD pipelines

### 2. Pipeline Execution

Three types of pipelines are available:

**Build Pipeline**:
- Clones repository
- Installs dependencies
- Compiles/builds the project
- Creates artifacts

**Test Pipeline**:
- Sets up test environment
- Runs unit tests
- Runs integration tests
- Generates test reports

**Deploy Pipeline**:
- Pre-deployment validation
- Deploys to staging
- Runs smoke tests
- Deploys to production (if configured)

### 3. AI-Powered Failure Detection & Fixing

When a pipeline fails:

1. **Analysis**: AI analyzes error logs to identify root cause
2. **Fix Generation**: AI generates specific code/config fixes
3. **Application**: Fixes are automatically applied to the repository
4. **Verification**: Pipeline is re-run to verify the fix
5. **Retry**: Process repeats up to `max_fix_attempts` times

### 4. Specialized Fixers

**Build Fixer**:
- Detects and fixes dependency issues
- Resolves compilation errors
- Corrects configuration problems

**Test Fixer**:
- Fixes flaky tests
- Updates test assertions
- Corrects test data

**AI Fixer** (General):
- Uses LLMs for complex issues
- Supports both Anthropic (Claude) and OpenAI (GPT-4)
- Provides detailed analysis and fixes

## Examples

### Example 1: Simple Python Workflow

```python
from orchestrator.core.orchestrator import CICDOrchestrator
from orchestrator.utils.config import load_config

# Load configuration
config = load_config("config.yaml")

# Create and start orchestrator
orchestrator = CICDOrchestrator(config.model_dump())
orchestrator.start()

# Orchestrator will now monitor for changes and run pipelines
```

### Example 2: Manual Pipeline Trigger

```python
from orchestrator.core.orchestrator import CICDOrchestrator
from orchestrator.utils.config import load_config

config = load_config("config.yaml")
orchestrator = CICDOrchestrator(config.model_dump())

# Run build pipeline
result = orchestrator.trigger_pipeline("build")

if result["status"] == "success":
    print("Build succeeded!")
else:
    print(f"Build failed: {result['error']}")
```

See `examples/` directory for more examples.

## Configuration Options

### Project Settings

- `name`: Project name
- `repository`: Git repository URL
- `branch`: Branch to monitor
- `language`: Programming language
- `workspace`: Working directory

### LLM Settings

- `provider`: "anthropic" or "openai"
- `model`: LLM model to use
- `api_key`: API key (use environment variable)
- `max_tokens`: Maximum response length
- `temperature`: Creativity level (0.0-1.0)

### Pipeline Settings

Each pipeline (build/test/deploy) supports:
- `enabled`: Enable/disable pipeline
- `timeout`: Maximum execution time
- `retry_on_failure`: Auto-retry on failure
- `max_retries`: Maximum retry attempts

### Monitoring & Alerts

- **Metrics**: Track success rates, durations, failures
- **Health Checks**: Monitor component health
- **Alerts**: Email, Slack, console notifications

## Advanced Features

### Custom Pipeline Definitions

Define custom pipelines in `pipelines/`:

```python
custom_pipeline = {
    "name": "security-scan",
    "version": "1.0",
    "stages": [
        {
            "name": "scan",
            "tasks": [
                {
                    "name": "run_security_scan",
                    "action": "test",
                    "config": {"test_type": "security"}
                }
            ]
        }
    ]
}
```

### Extending Fixers

Create custom fixers by extending `AIFixer`:

```python
from orchestrator.fixers.ai_fixer import AIFixer

class SecurityFixer(AIFixer):
    def fix_vulnerability(self, vuln_data):
        # Custom fix logic
        pass
```

## Monitoring & Metrics

The system tracks:

- Pipeline success/failure rates
- Average execution times
- Failed stages and tasks
- Fix success rates
- System health metrics

Access metrics via:
```python
orchestrator.pipeline_monitor.get_metrics()
```

## Alerting

Configure alerts in `config.yaml`:

```yaml
alerts:
  enabled: true
  channels:
    - console
    - email
    - slack

  email:
    smtp_host: "smtp.gmail.com"
    recipients:
      - "team@example.com"

  slack:
    webhook_url: "${SLACK_WEBHOOK_URL}"
    channel: "#ci-cd-alerts"
```

## Development

### Running Tests

```bash
pytest tests/
```

### Code Quality

```bash
# Format code
black orchestrator/

# Lint
flake8 orchestrator/

# Type checking
mypy orchestrator/
```

## Documentation

Comprehensive documentation is available in `docs/`:

- [Getting Started](docs/getting_started.md)
- [Architecture](docs/architecture.md)
- [AI Fixers Guide](docs/fixers.md)
- [Pipeline Configuration](docs/pipelines.md)
- [Monitoring & Alerts](docs/monitoring.md)

## Troubleshooting

### Common Issues

**Orchestrator won't start**:
- Check configuration file is valid: `ai-cicd validate`
- Verify API keys are set in `.env`
- Check logs in `logs/orchestrator.log`

**AI fixes not working**:
- Verify LLM API key is correct
- Check API rate limits
- Review LLM provider status

**Pipeline failures**:
- Check repository access
- Verify dependencies are installed
- Review pipeline logs

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Roadmap

- [ ] Support for additional LLM providers
- [ ] Kubernetes deployment support
- [ ] Advanced deployment strategies (canary, blue-green)
- [ ] Web dashboard for monitoring
- [ ] Plugin system for extensibility
- [ ] Multi-repository support
- [ ] Predictive failure detection

## Support

For issues and questions:
- GitHub Issues: https://github.com/matthewnyc2/AI-CI-CD-Orchestrator/issues
- Documentation: See `docs/` directory

## Acknowledgments

Built with:
- [Anthropic Claude](https://www.anthropic.com/)
- [OpenAI GPT-4](https://openai.com/)
- [GitPython](https://gitpython.readthedocs.io/)
- [Click](https://click.palletsprojects.com/)
- [Rich](https://rich.readthedocs.io/)
