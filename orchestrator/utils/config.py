"""Configuration management for AI-CI-CD Orchestrator."""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv


class ProjectConfig(BaseModel):
    """Project configuration."""
    name: str
    repository: str
    branch: str = "main"
    language: str = "python"
    workspace: str = "/tmp/ai-cicd-workspace"


class OrchestratorConfig(BaseModel):
    """Orchestrator configuration."""
    polling_interval: int = 60
    max_parallel_pipelines: int = 3
    auto_fix_enabled: bool = True
    max_fix_attempts: int = 3
    zero_downtime: bool = True


class GitConfig(BaseModel):
    """Git configuration."""
    monitor_enabled: bool = True
    monitored_branches: List[str] = ["main"]
    ignore_authors: List[str] = []


class LLMConfig(BaseModel):
    """LLM configuration."""
    provider: str = "anthropic"
    model: str = "claude-3-5-sonnet-20241022"
    api_key: str
    max_tokens: int = 4000
    temperature: float = 0.2
    timeout: int = 60


class PipelineConfig(BaseModel):
    """Individual pipeline configuration."""
    enabled: bool = True
    timeout: int = 1800
    retry_on_failure: bool = False
    max_retries: int = 2


class PipelinesConfig(BaseModel):
    """All pipelines configuration."""
    build: PipelineConfig = Field(default_factory=PipelineConfig)
    test: PipelineConfig = Field(default_factory=PipelineConfig)
    deploy: PipelineConfig = Field(default_factory=PipelineConfig)


class MonitoringConfig(BaseModel):
    """Monitoring configuration."""
    enabled: bool = True
    collect_metrics: bool = True
    metrics_storage: str = "file"
    metrics_file: str = "metrics/pipeline_metrics.json"
    health_check_interval: int = 30
    failure_rate_threshold: float = 0.2
    duration_threshold_multiplier: float = 2.0


class EmailConfig(BaseModel):
    """Email alert configuration."""
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    from_address: str = ""
    recipients: List[str] = []


class SlackConfig(BaseModel):
    """Slack alert configuration."""
    webhook_url: str = ""
    channel: str = "#ci-cd-alerts"
    username: str = "AI-CICD Bot"


class AlertsConfig(BaseModel):
    """Alerts configuration."""
    enabled: bool = True
    channels: List[str] = ["console"]
    email: EmailConfig = Field(default_factory=EmailConfig)
    slack: SlackConfig = Field(default_factory=SlackConfig)
    min_severity: str = "warning"


class LoggingConfig(BaseModel):
    """Logging configuration."""
    level: str = "INFO"
    format: str = "json"
    output: str = "both"
    log_file: str = "logs/orchestrator.log"
    max_file_size: int = 10485760
    backup_count: int = 5


class DatabaseConfig(BaseModel):
    """Database configuration."""
    enabled: bool = False
    url: str = "sqlite:///orchestrator.db"
    pool_size: int = 5
    max_overflow: int = 10


class SecurityConfig(BaseModel):
    """Security configuration."""
    secrets_manager: str = "env"
    allowed_ips: List[str] = []
    api_auth_enabled: bool = False
    api_key: str = ""


class FeaturesConfig(BaseModel):
    """Feature flags configuration."""
    ai_code_review: bool = False
    predictive_failure_detection: bool = False
    auto_rollback: bool = True
    canary_deployments: bool = False


class Config(BaseModel):
    """Main configuration model."""
    project: ProjectConfig
    orchestrator: OrchestratorConfig = Field(default_factory=OrchestratorConfig)
    git: GitConfig = Field(default_factory=GitConfig)
    llm: LLMConfig
    pipelines: PipelinesConfig = Field(default_factory=PipelinesConfig)
    monitoring: MonitoringConfig = Field(default_factory=MonitoringConfig)
    alerts: AlertsConfig = Field(default_factory=AlertsConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    features: FeaturesConfig = Field(default_factory=FeaturesConfig)


def expand_env_vars(config_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively expand environment variables in config values."""
    if isinstance(config_dict, dict):
        return {k: expand_env_vars(v) for k, v in config_dict.items()}
    elif isinstance(config_dict, list):
        return [expand_env_vars(item) for item in config_dict]
    elif isinstance(config_dict, str):
        # Replace ${VAR_NAME} with environment variable value
        if config_dict.startswith("${") and config_dict.endswith("}"):
            var_name = config_dict[2:-1]
            return os.getenv(var_name, config_dict)
        return config_dict
    else:
        return config_dict


def load_config(config_path: Optional[str] = None) -> Config:
    """
    Load configuration from YAML file and environment variables.

    Args:
        config_path: Path to config file. Defaults to config.yaml in current directory.

    Returns:
        Loaded and validated configuration.

    Raises:
        FileNotFoundError: If config file doesn't exist.
        ValueError: If config is invalid.
    """
    # Load environment variables from .env file
    load_dotenv()

    # Determine config file path
    if config_path is None:
        config_path = "config.yaml"
        if not os.path.exists(config_path):
            # Try in parent directory
            config_path = "../config.yaml"

    config_file = Path(config_path)
    if not config_file.exists():
        raise FileNotFoundError(
            f"Configuration file not found: {config_path}\n"
            "Please create config.yaml from config.example.yaml"
        )

    # Load YAML configuration
    with open(config_file, 'r') as f:
        config_dict = yaml.safe_load(f)

    # Expand environment variables
    config_dict = expand_env_vars(config_dict)

    # Validate and create config object
    try:
        config = Config(**config_dict)
    except Exception as e:
        raise ValueError(f"Invalid configuration: {e}")

    return config


def create_default_config(output_path: str = "config.yaml") -> None:
    """
    Create a default configuration file.

    Args:
        output_path: Where to write the config file.
    """
    default_config = {
        "project": {
            "name": "my-project",
            "repository": "https://github.com/username/my-project",
            "branch": "main",
            "language": "python",
            "workspace": "/tmp/ai-cicd-workspace"
        },
        "llm": {
            "provider": "anthropic",
            "model": "claude-3-5-sonnet-20241022",
            "api_key": "${ANTHROPIC_API_KEY}"
        }
    }

    with open(output_path, 'w') as f:
        yaml.dump(default_config, f, default_flow_style=False, sort_keys=False)

    print(f"Default configuration created at: {output_path}")
