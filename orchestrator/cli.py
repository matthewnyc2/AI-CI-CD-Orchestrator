"""
Command-line interface for AI-CI-CD Orchestrator.
"""

import click
import logging
import sys
import signal
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich import print as rprint

from .core.orchestrator import CICDOrchestrator
from .utils.config import load_config, create_default_config
from .utils.logger import setup_logging

console = Console()
orchestrator_instance = None


def signal_handler(sig, frame):
    """Handle interrupt signals gracefully."""
    console.print("\n[yellow]Shutting down orchestrator...[/yellow]")
    if orchestrator_instance:
        orchestrator_instance.stop()
    sys.exit(0)


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """AI-CI-CD Orchestrator - Autonomous CI/CD with AI-powered fixes."""
    pass


@cli.command()
@click.option('--config', '-c', default='config.yaml', help='Path to configuration file')
@click.option('--daemon', '-d', is_flag=True, help='Run in daemon mode')
def start(config, daemon):
    """Start the AI-CI-CD orchestrator."""
    global orchestrator_instance

    try:
        # Load configuration
        console.print(f"[blue]Loading configuration from {config}...[/blue]")
        cfg = load_config(config)

        # Setup logging
        log_config = cfg.logging
        setup_logging(
            level=log_config.level,
            log_format=log_config.format,
            output=log_config.output,
            log_file=log_config.log_file,
            max_file_size=log_config.max_file_size,
            backup_count=log_config.backup_count
        )

        console.print("[green]Configuration loaded successfully[/green]")

        # Create orchestrator
        console.print("[blue]Initializing AI-CI-CD Orchestrator...[/blue]")

        # Convert config to dict for orchestrator
        config_dict = cfg.model_dump()

        orchestrator_instance = CICDOrchestrator(config_dict)

        # Setup signal handlers
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        # Start orchestrator
        console.print("[green]Starting orchestrator...[/green]")
        orchestrator_instance.start()

        # Display status
        _display_status(config_dict)

        if daemon:
            console.print("[yellow]Running in daemon mode. Press Ctrl+C to stop.[/yellow]")
            # Keep running
            signal.pause()
        else:
            console.print("[yellow]Orchestrator started. Press Ctrl+C to stop.[/yellow]")
            # Keep the main thread alive
            import time
            while True:
                time.sleep(1)

    except FileNotFoundError as e:
        console.print(f"[red]Error: {e}[/red]")
        console.print("[yellow]Run 'ai-cicd init' to create a default configuration.[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error starting orchestrator: {e}[/red]")
        logging.exception("Failed to start orchestrator")
        sys.exit(1)


@cli.command()
@click.option('--config', '-c', default='config.yaml', help='Path to configuration file')
@click.argument('pipeline_type', type=click.Choice(['build', 'test', 'deploy']))
def run(config, pipeline_type):
    """Run a specific pipeline once."""
    try:
        # Load configuration
        cfg = load_config(config)

        # Setup logging
        setup_logging(level=cfg.logging.level)

        console.print(f"[blue]Running {pipeline_type} pipeline...[/blue]")

        # Create orchestrator
        config_dict = cfg.model_dump()
        orchestrator = CICDOrchestrator(config_dict)

        # Trigger the pipeline
        result = orchestrator.trigger_pipeline(pipeline_type)

        # Display result
        if result.get("status") == "success":
            console.print(f"[green]{pipeline_type.title()} pipeline completed successfully![/green]")
            sys.exit(0)
        else:
            console.print(f"[red]{pipeline_type.title()} pipeline failed![/red]")
            console.print(f"[red]Error: {result.get('error', 'Unknown error')}[/red]")
            sys.exit(1)

    except Exception as e:
        console.print(f"[red]Error running pipeline: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.option('--output', '-o', default='config.yaml', help='Output path for configuration file')
def init(output):
    """Initialize a new configuration file."""
    try:
        if Path(output).exists():
            if not click.confirm(f"{output} already exists. Overwrite?"):
                console.print("[yellow]Initialization cancelled.[/yellow]")
                return

        create_default_config(output)
        console.print(f"[green]Configuration file created: {output}[/green]")
        console.print("[yellow]Please edit the configuration and add your API keys.[/yellow]")
        console.print("[yellow]Also create a .env file from .env.example[/yellow]")

    except Exception as e:
        console.print(f"[red]Error creating configuration: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.option('--config', '-c', default='config.yaml', help='Path to configuration file')
def status(config):
    """Show orchestrator status."""
    try:
        cfg = load_config(config)
        config_dict = cfg.model_dump()

        _display_status(config_dict)

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.option('--config', '-c', default='config.yaml', help='Path to configuration file')
def validate(config):
    """Validate configuration file."""
    try:
        console.print(f"[blue]Validating {config}...[/blue]")

        cfg = load_config(config)

        console.print("[green]Configuration is valid![/green]")

        # Display key settings
        table = Table(title="Configuration Summary")
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Project", cfg.project.name)
        table.add_row("Repository", cfg.project.repository)
        table.add_row("Branch", cfg.project.branch)
        table.add_row("LLM Provider", cfg.llm.provider)
        table.add_row("LLM Model", cfg.llm.model)
        table.add_row("Auto-fix Enabled", str(cfg.orchestrator.auto_fix_enabled))
        table.add_row("Polling Interval", f"{cfg.orchestrator.polling_interval}s")

        console.print(table)

    except Exception as e:
        console.print(f"[red]Configuration validation failed: {e}[/red]")
        sys.exit(1)


def _display_status(config_dict):
    """Display orchestrator status."""
    table = Table(title="AI-CI-CD Orchestrator Status")

    table.add_column("Component", style="cyan", no_wrap=True)
    table.add_column("Status", style="green")
    table.add_column("Details", style="yellow")

    # Project info
    project = config_dict.get("project", {})
    table.add_row(
        "Project",
        "[green]●[/green] Active",
        f"{project.get('name', 'Unknown')}"
    )

    # Repository
    table.add_row(
        "Repository",
        "[green]●[/green] Configured",
        project.get("repository", "Not set")
    )

    # LLM
    llm = config_dict.get("llm", {})
    table.add_row(
        "AI Fixer",
        "[green]●[/green] Enabled" if config_dict.get("orchestrator", {}).get("auto_fix_enabled") else "[red]●[/red] Disabled",
        f"{llm.get('provider', 'Unknown')} - {llm.get('model', 'Unknown')}"
    )

    # Pipelines
    pipelines = config_dict.get("pipelines", {})
    for pipeline_name in ["build", "test", "deploy"]:
        pipeline_cfg = pipelines.get(pipeline_name, {})
        enabled = pipeline_cfg.get("enabled", True)
        table.add_row(
            f"{pipeline_name.title()} Pipeline",
            f"[green]●[/green] Enabled" if enabled else "[red]●[/red] Disabled",
            f"Timeout: {pipeline_cfg.get('timeout', 'N/A')}s"
        )

    # Monitoring
    monitoring = config_dict.get("monitoring", {})
    table.add_row(
        "Monitoring",
        "[green]●[/green] Enabled" if monitoring.get("enabled") else "[red]●[/red] Disabled",
        f"Metrics: {monitoring.get('metrics_storage', 'N/A')}"
    )

    # Alerts
    alerts = config_dict.get("alerts", {})
    channels = ", ".join(alerts.get("channels", []))
    table.add_row(
        "Alerts",
        "[green]●[/green] Enabled" if alerts.get("enabled") else "[red]●[/red] Disabled",
        f"Channels: {channels}"
    )

    console.print(table)


def main():
    """Main entry point."""
    cli()


if __name__ == "__main__":
    main()
