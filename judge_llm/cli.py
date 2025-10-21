"""CLI interface for Judge LLM framework"""

import click
from pathlib import Path
from dotenv import load_dotenv
from judge_llm.core.evaluate import evaluate
from judge_llm.core.config_validator import get_validator
from judge_llm.core.registry import get_provider_registry, get_evaluator_registry, get_reporter_registry
from judge_llm.utils.logger import get_logger, set_log_level
import yaml

# Load environment variables from .env file if present
load_dotenv()


@click.group()
@click.version_option(version="1.0.3")
def main():
    """Judge LLM - A lightweight LLM evaluation framework"""
    pass


@main.command()
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True),
    help="Path to configuration YAML file",
)
@click.option(
    "--dataset",
    "-d",
    multiple=True,
    type=click.Path(exists=True),
    help="Path to dataset file(s)",
)
@click.option(
    "--provider",
    "-p",
    type=str,
    help="Provider type (e.g., mock, gemini, openai)",
)
@click.option(
    "--agent-id",
    type=str,
    help="Agent identifier",
)
@click.option(
    "--num-runs",
    "-n",
    type=int,
    default=1,
    help="Number of runs per eval case",
)
@click.option(
    "--parallel/--sequential",
    default=False,
    help="Enable parallel execution",
)
@click.option(
    "--max-workers",
    type=int,
    default=4,
    help="Maximum worker threads for parallel execution",
)
@click.option(
    "--log-level",
    "-l",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], case_sensitive=False),
    default="INFO",
    help="Logging level",
)
@click.option(
    "--no-defaults",
    is_flag=True,
    help="Disable default configuration loading",
)
@click.option(
    "--defaults",
    type=click.Path(exists=True),
    help="Path to custom defaults configuration file",
)
@click.option(
    "--report",
    "-r",
    type=click.Choice(["console", "json", "html", "database"], case_sensitive=False),
    multiple=True,
    default=["console"],
    help="Report types to generate",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Output path for report (for json/html reporters)",
)
def run(
    config,
    dataset,
    provider,
    agent_id,
    num_runs,
    parallel,
    max_workers,
    log_level,
    no_defaults,
    defaults,
    report,
    output,
):
    """Run LLM evaluation"""
    set_log_level(log_level)
    logger = get_logger()

    try:
        if config:
            # Run from config file
            logger.info(f"Running evaluation from config file: {config}")
            evaluate(
                config=config,
                use_defaults=not no_defaults,
                defaults=defaults,
            )
        else:
            # Run from CLI arguments
            if not dataset:
                click.echo("Error: --dataset is required when not using --config", err=True)
                raise click.Abort()

            if not provider:
                click.echo("Error: --provider is required when not using --config", err=True)
                raise click.Abort()

            if not agent_id:
                click.echo("Error: --agent-id is required when not using --config", err=True)
                raise click.Abort()

            # Build configuration from CLI args
            cli_config = {
                "agent": {
                    "log_level": log_level,
                    "num_runs": num_runs,
                    "parallel_execution": parallel,
                    "max_workers": max_workers,
                },
                "dataset": {
                    "loader": "local_file",
                    "paths": list(dataset),
                },
                "providers": [
                    {
                        "type": provider,
                        "agent_id": agent_id,
                    }
                ],
                "evaluators": [
                    {"type": "response_evaluator", "enabled": True, "config": {}},
                    {"type": "trajectory_evaluator", "enabled": True, "config": {}},
                ],
                "reporters": [{"type": r, "output_path": output} for r in report],
            }

            evaluate(
                config=cli_config,
                use_defaults=not no_defaults,
                defaults=defaults,
            )

        click.echo("\n✓ Evaluation completed successfully", err=False)

    except ValueError as e:
        # ValueError raised for threshold violations - error message already logged
        # Check if this is a threshold violation error
        if "THRESHOLD VIOLATION" in str(e):
            # Error message already contains detailed info, don't duplicate
            raise SystemExit(1)
        else:
            # Other ValueError - show the error
            logger.error(f"Evaluation failed: {e}")
            click.echo(f"\n✗ Evaluation failed: {e}", err=True)
            raise SystemExit(1)
    except Exception as e:
        logger.error(f"Evaluation failed: {e}")
        click.echo(f"\n✗ Evaluation failed: {e}", err=True)
        raise SystemExit(1)


@main.command()
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True),
    required=True,
    help="Path to configuration YAML file",
)
def validate(config):
    """Validate configuration file"""
    set_log_level("INFO")
    logger = get_logger()

    try:
        logger.info(f"Validating configuration file: {config}")

        with open(config, 'r', encoding='utf-8') as f:
            config_dict = yaml.safe_load(f)

        validator = get_validator()
        is_valid, errors = validator.validate(config_dict)

        if is_valid:
            click.echo("\n✓ Configuration is valid", err=False)
        else:
            click.echo("\n✗ Configuration validation failed:", err=True)
            for error in errors:
                click.echo(f"  - {error}", err=True)
            raise click.Abort()

    except Exception as e:
        logger.error(f"Validation failed: {e}")
        click.echo(f"\n✗ Validation failed: {e}", err=True)
        raise click.Abort()


@main.command()
@click.argument("entity", type=click.Choice(["providers", "evaluators", "reporters"], case_sensitive=False))
def list(entity):
    """List available providers, evaluators, or reporters"""
    set_log_level("WARNING")  # Suppress most logs for list command

    if entity.lower() == "providers":
        registry = get_provider_registry()
        providers = registry.list_providers()

        click.echo("\nAvailable Providers:")
        if providers:
            for provider in sorted(providers):
                click.echo(f"  - {provider}")
        else:
            click.echo("  (none)")

    elif entity.lower() == "evaluators":
        registry = get_evaluator_registry()
        evaluators = registry.list_evaluators()

        click.echo("\nAvailable Evaluators:")
        if evaluators:
            for evaluator in sorted(evaluators):
                click.echo(f"  - {evaluator}")
        else:
            click.echo("  (none)")

    elif entity.lower() == "reporters":
        registry = get_reporter_registry()
        reporters = registry.list_reporters()

        click.echo("\nAvailable Reporters:")
        if reporters:
            for reporter in sorted(reporters):
                click.echo(f"  - {reporter}")
        else:
            click.echo("  (none)")

    click.echo()


@main.command()
@click.option(
    "--db",
    "-d",
    type=click.Path(exists=True),
    help="Path to SQLite database file to open in dashboard",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    default="./dashboard.html",
    help="Output path for dashboard HTML file",
)
@click.option(
    "--no-browser",
    is_flag=True,
    help="Don't automatically open browser",
)
def dashboard(db, output, no_browser):
    """Generate and launch evaluation dashboard"""
    import shutil
    import webbrowser
    from pathlib import Path

    set_log_level("INFO")
    logger = get_logger()

    try:
        # Get the dashboard template
        template_path = Path(__file__).parent / "templates" / "monitor.html"

        if not template_path.exists():
            click.echo(f"✗ Dashboard template not found at: {template_path}", err=True)
            raise click.Abort()

        # Copy to output location
        output_file = Path(output).expanduser().resolve()
        output_file.parent.mkdir(parents=True, exist_ok=True)

        shutil.copy(template_path, output_file)

        click.echo("=" * 80)
        click.echo("✅ Dashboard Generated Successfully!")
        click.echo("=" * 80)
        click.echo()
        click.echo(f"📁 Dashboard: {output_file}")

        if db:
            click.echo(f"📊 Database: {Path(db).resolve()}")

        click.echo()
        click.echo("📖 How to use:")
        click.echo("   1. Dashboard will open in your browser")
        click.echo("   2. Drag and drop your .db file (or click to browse)")
        click.echo("   3. Explore your evaluation results!")
        click.echo()
        click.echo("🔒 Privacy: All data stays local - no uploads or external services")
        click.echo()
        click.echo("=" * 80)

        # Open in browser
        if not no_browser:
            click.echo("\n🌐 Opening dashboard in browser...")
            webbrowser.open(f"file://{output_file}")
        else:
            click.echo(f"\n💡 Open manually: file://{output_file}")

        click.echo("✓ Dashboard ready!", err=False)

    except Exception as e:
        logger.error(f"Dashboard generation failed: {e}")
        click.echo(f"\n✗ Dashboard generation failed: {e}", err=True)
        raise click.Abort()


if __name__ == "__main__":
    main()
