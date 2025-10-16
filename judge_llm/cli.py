"""CLI interface for Judge LLM framework"""

import click
from pathlib import Path
from judge_llm.core.evaluate import evaluate
from judge_llm.core.config_validator import get_validator
from judge_llm.core.registry import get_provider_registry, get_evaluator_registry
from judge_llm.utils.logger import get_logger, set_log_level
import yaml


@click.group()
@click.version_option(version="0.1.0")
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
    "--no-validate",
    is_flag=True,
    help="Disable configuration validation",
)
@click.option(
    "--report",
    "-r",
    type=click.Choice(["console", "json", "html"], case_sensitive=False),
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
    no_validate,
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
            evaluate(config=config, validate_config=not no_validate)
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
                    {"type": "response_validator", "enabled": True, "config": {}},
                    {"type": "trajectory_validator", "enabled": True, "config": {}},
                ],
                "reporters": [{"type": r, "output_path": output} for r in report],
            }

            evaluate(config=cli_config, validate_config=not no_validate)

        click.echo("\n✓ Evaluation completed successfully", err=False)

    except Exception as e:
        logger.error(f"Evaluation failed: {e}")
        click.echo(f"\n✗ Evaluation failed: {e}", err=True)
        raise click.Abort()


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
@click.argument("entity", type=click.Choice(["providers", "evaluators"], case_sensitive=False))
def list(entity):
    """List available providers or evaluators"""
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

    click.echo()


if __name__ == "__main__":
    main()
