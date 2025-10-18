"""Main evaluate function for Judge LLM framework"""

import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from judge_llm.core.models import (
    EvalSet,
    EvalCase,
    ExecutionRun,
    EvaluationReport,
    ProviderResult,
)
from judge_llm.core.config_validator import get_validator
from judge_llm.core.config_loader import get_loader
from judge_llm.core.registry import get_provider_registry, get_evaluator_registry
from judge_llm.loaders.base import BaseLoader
from judge_llm.loaders.local_file_loader import LocalFileLoader
from judge_llm.loaders.directory_loader import DirectoryLoader
from judge_llm.providers.base import BaseProvider
from judge_llm.evaluators.base import BaseEvaluator
from judge_llm.reporters.base import BaseReporter
from judge_llm.reporters.console_reporter import ConsoleReporter
from judge_llm.reporters.json_reporter import JSONReporter
from judge_llm.reporters.html_reporter import HTMLReporter
from judge_llm.utils.logger import get_logger, set_log_level


def _print_configuration_summary(
    agent_config: Dict[str, Any],
    dataset_config: Dict[str, Any],
    providers_config: List[Dict[str, Any]],
    evaluators_config: List[Dict[str, Any]],
    reporters_config: List[Dict[str, Any]],
):
    """Print a nice summary of the configuration in grid format - one row per agent"""
    logger = get_logger()

    # Prepare summary data
    num_runs = agent_config.get('num_runs', 1)
    parallel = "Yes" if agent_config.get('parallel_execution', False) else "No"
    if agent_config.get('parallel_execution', False):
        parallel += f" ({agent_config.get('max_workers', 4)})"

    # Get dataset info
    paths = dataset_config.get('paths', [])
    datasets_str = ', '.join([p.split('/')[-1] for p in paths]) if paths else 'N/A'
    if len(datasets_str) > 25:
        datasets_str = datasets_str[:22] + "..."

    # Get evaluators summary
    evaluators_str = ', '.join([e.get('name', e.get('type', 'unknown'))[:15] for e in evaluators_config])
    if len(evaluators_str) > 30:
        evaluators_str = evaluators_str[:27] + "..."

    # Get reporters summary
    reporters_str = ', '.join([r.get('type', 'unknown') for r in reporters_config])
    if len(reporters_str) > 20:
        reporters_str = reporters_str[:17] + "..."

    # Build grid
    summary = "\n" + "="*140 + "\n"
    summary += "  EVALUATION CONFIGURATION\n"
    summary += "="*140 + "\n"

    # Table header
    summary += "┌" + "─"*138 + "┐\n"
    summary += "│ Agent ID / Provider    │ Type    │ Runs │ Parallel │ Datasets             │ Evaluators                   │ Reporters           │\n"
    summary += "├" + "─"*138 + "┤\n"

    # One row per provider (agent)
    for provider in providers_config:
        agent_id = provider.get('agent_id', 'N/A')[:22]
        provider_type = provider.get('type', 'unknown')[:7]

        summary += f"│ {agent_id:<22} │ {provider_type:<7} │ {num_runs:^4} │ {parallel:<8} │ {datasets_str:<20} │ {evaluators_str:<28} │ {reporters_str:<19} │\n"

    summary += "└" + "─"*138 + "┘\n"
    summary += "="*140 + "\n\n"

    logger.info(summary)


def evaluate(
    config: Optional[Union[str, Dict[str, Any]]] = None,
    agent: Optional[Dict[str, Any]] = None,
    dataset: Optional[Dict[str, Any]] = None,
    providers: Optional[List[Dict[str, Any]]] = None,
    evaluators: Optional[List[Dict[str, Any]]] = None,
    reporters: Optional[List[Dict[str, Any]]] = None,
    validate_config: bool = True,
    use_defaults: bool = True,
    defaults: Optional[str] = None,
) -> EvaluationReport:
    """Main evaluation function

    Args:
        config: Configuration file path or dictionary (YAML structure)
        agent: Agent configuration dict:
            {
                "log_level": "INFO",
                "num_runs": 1,
                "parallel_execution": False,
                "max_workers": 4,
                "fail_on_threshold_violation": True,
                "validate_config": True
            }
        dataset: Dataset configuration dict:
            {
                "loader": "local_file",
                "paths": ["./data/eval.json"]
            }
        providers: List of provider configuration dicts:
            [{
                "type": "mock",
                "agent_id": "my_agent",
                "model": "mock-model-v1",
                ... (any additional provider-specific config)
            }]
        evaluators: List of evaluator configuration dicts:
            [{
                "type": "response_evaluator",
                "enabled": True,
                "config": {"similarity_threshold": 0.8}
            }]
        reporters: List of reporter configuration dicts:
            [{
                "type": "console"
            }, {
                "type": "html",
                "output_path": "./report.html"
            }]
        validate_config: Validate configuration before execution (default: True)
        use_defaults: Use default configuration if available (default: True)
        defaults: Path to custom defaults file (optional)

    Returns:
        EvaluationReport with all results

    Examples:
        # From config file (uses defaults automatically)
        report = evaluate(config="config.yaml")

        # From config file without defaults
        report = evaluate(config="config.yaml", use_defaults=False)

        # With custom defaults file
        report = evaluate(config="config.yaml", defaults="./my-defaults.yaml")

        # Programmatic with dict structure
        report = evaluate(
            agent={"log_level": "INFO", "num_runs": 1},
            dataset={"loader": "local_file", "paths": ["./data.json"]},
            providers=[{"type": "mock", "agent_id": "test"}],
            evaluators=[{"type": "response_evaluator", "config": {}}],
            reporters=[{"type": "console"}]
        )
    """
    logger = get_logger()

    # If config is provided, load it with defaults support
    if config is not None:
        config_dict = _load_config(config, use_defaults, defaults)
        # Set log level from config or use default
        agent_config = config_dict.get("agent", {})
        set_log_level(agent_config.get("log_level", "INFO"))
    else:
        # Build config from provided dicts
        if agent is None:
            agent = {}

        set_log_level(agent.get("log_level", "INFO"))

        config_dict = {
            "agent": agent,
            "dataset": dataset or {},
            "providers": providers or [],
            "evaluators": evaluators or [],
            "reporters": reporters or [{"type": "console"}],
        }

    logger.info("Starting Judge LLM evaluation")

    return _evaluate_from_config(config_dict, validate_config)


def _load_config(
    config: Union[str, Dict[str, Any]],
    use_defaults: bool = True,
    defaults_path: Optional[str] = None,
) -> Dict[str, Any]:
    """Load configuration from file or dict with optional defaults

    Args:
        config: Configuration file path or dict
        use_defaults: Whether to use default configuration
        defaults_path: Path to custom defaults file

    Returns:
        Configuration dictionary (merged with defaults if enabled)
    """
    loader = get_loader()
    return loader.load(config, use_defaults=use_defaults, defaults_path=defaults_path)


def _evaluate_from_config(config: Dict[str, Any], validate: bool = True) -> EvaluationReport:
    """Execute evaluation from configuration dictionary"""
    logger = get_logger()

    # Validate configuration
    if validate:
        validator = get_validator()
        is_valid, errors = validator.validate(config)

        if not is_valid:
            # Format nice validation summary
            error_msg = "\n" + "="*80 + "\n"
            error_msg += "  CONFIGURATION VALIDATION FAILED\n"
            error_msg += "="*80 + "\n\n"
            error_msg += f"Found {len(errors)} error(s) in your configuration:\n\n"

            for idx, err in enumerate(errors, 1):
                error_msg += f"{idx}. [{err.field}]\n"
                error_msg += f"   ✗ Error: {err.message}\n"
                error_msg += f"   ✓ Fix:   {err.fix_suggestion}\n\n"

            error_msg += "="*80 + "\n"
            error_msg += "Please fix the above issues and try again.\n"
            error_msg += "="*80

            logger.error(error_msg)
            raise ValueError(error_msg)

    # Extract configuration
    agent_config = config.get("agent", {})
    dataset_config = config.get("dataset", {})
    providers_config = config.get("providers", [])
    evaluators_config = config.get("evaluators", [])
    reporters_config = config.get("reporters", [{"type": "console"}])

    # Set log level
    log_level = agent_config.get("log_level", "INFO")
    set_log_level(log_level)

    # Print configuration summary
    _print_configuration_summary(
        agent_config=agent_config,
        dataset_config=dataset_config,
        providers_config=providers_config,
        evaluators_config=evaluators_config,
        reporters_config=reporters_config
    )

    # Load datasets
    logger.debug("Loading datasets")
    eval_sets = _load_datasets(dataset_config)
    logger.debug(f"Loaded {len(eval_sets)} eval set(s)")

    # Initialize providers
    logger.debug("Initializing providers")
    providers = _initialize_providers(providers_config, agent_config)
    logger.debug(f"Initialized {len(providers)} provider(s)")

    # Initialize evaluators
    logger.debug("Initializing evaluators")
    evaluators = _initialize_evaluators(evaluators_config)
    logger.debug(f"Initialized {len(evaluators)} evaluator(s)")

    # Execute evaluations
    logger.info("▶ Starting evaluation...")
    execution_runs = _execute_evaluations(
        eval_sets=eval_sets,
        providers=providers,
        evaluators=evaluators,
        num_runs=agent_config.get("num_runs", 1),
        parallel_execution=agent_config.get("parallel_execution", False),
        max_workers=agent_config.get("max_workers", 4),
    )

    # Generate report
    logger.debug("Generating evaluation report")
    report = _generate_report(execution_runs)

    # Generate reports via reporters
    logger.debug("Generating reports via reporters")
    reporters = _initialize_reporters(reporters_config)
    for reporter in reporters:
        reporter.generate_report(report)
        reporter.cleanup()

    # Cleanup resources
    logger.debug("Cleaning up resources")
    for provider in providers:
        provider.cleanup()

    logger.info("✓ Evaluation completed successfully")

    return report


def _load_datasets(dataset_config: Dict[str, Any]) -> List[EvalSet]:
    """Load datasets using configured loader"""
    loader_type = dataset_config.get("loader", "local_file")
    paths = dataset_config.get("paths", [])

    if not paths:
        raise ValueError("No dataset paths provided")

    eval_sets = []

    for path in paths:
        if loader_type == "local_file":
            loader = LocalFileLoader(path)
        elif loader_type == "directory":
            loader = DirectoryLoader(path)
        else:
            raise ValueError(f"Unknown loader type: {loader_type}")

        eval_sets.extend(loader.load())
        loader.cleanup()

    return eval_sets


def _initialize_providers(
    providers_config: List[Dict[str, Any]],
    agent_config: Dict[str, Any]
) -> List[BaseProvider]:
    """Initialize providers from configuration

    Args:
        providers_config: List of provider configurations
        agent_config: Agent configuration containing metadata

    Returns:
        List of initialized providers
    """
    registry = get_provider_registry()
    providers = []

    # Extract agent metadata from agent config (exclude execution settings)
    execution_keys = {"num_runs", "parallel_execution", "max_workers", "fail_on_threshold_violation", "validate_config", "log_level"}
    agent_metadata = {
        k: v
        for k, v in agent_config.items()
        if k not in execution_keys
    }

    for provider_config in providers_config:
        provider_type = provider_config.get("type")
        if not provider_type:
            raise ValueError("Provider type is required")

        provider_class = registry.get(provider_type)
        if not provider_class:
            raise ValueError(f"Unknown provider type: {provider_type}")

        # Extract provider configuration
        agent_id = provider_config.get("agent_id")
        agent_config_path = provider_config.get("agent_config_path")

        # All other config items are passed as provider_metadata
        provider_metadata = {
            k: v
            for k, v in provider_config.items()
            if k not in ["type", "agent_id", "agent_config_path"]
        }

        provider = provider_class(
            agent_id=agent_id,
            agent_config_path=agent_config_path,
            agent_metadata=agent_metadata,
            **provider_metadata,
        )

        providers.append(provider)

    return providers


def _initialize_evaluators(evaluators_config: List[Dict[str, Any]]) -> List[BaseEvaluator]:
    """Initialize evaluators from configuration"""
    registry = get_evaluator_registry()
    evaluators = []

    for eval_config in evaluators_config:
        if not eval_config.get("enabled", True):
            continue

        evaluator_type = eval_config.get("type")
        if not evaluator_type:
            raise ValueError("Evaluator type is required")

        # Handle custom evaluators
        if evaluator_type == "custom":
            module_path = eval_config.get("module_path")
            module = eval_config.get("module")
            class_name = eval_config.get("class_name")

            if module_path:
                evaluator_class = registry.load_custom_evaluator(module_path, class_name)
            elif module:
                evaluator_class = registry.load_custom_evaluator_from_module(module, class_name)
            else:
                raise ValueError("Custom evaluator requires module_path or module")
        else:
            evaluator_class = registry.get(evaluator_type)
            if not evaluator_class:
                raise ValueError(f"Unknown evaluator type: {evaluator_type}")

        # Initialize evaluator with config
        evaluator = evaluator_class(config=eval_config.get("config", {}))
        evaluators.append(evaluator)

    return evaluators


def _initialize_reporters(reporters_config: List[Dict[str, Any]]) -> List[BaseReporter]:
    """Initialize reporters from configuration"""
    reporters = []

    for reporter_config in reporters_config:
        reporter_type = reporter_config.get("type")

        if reporter_type == "console":
            reporters.append(ConsoleReporter())
        elif reporter_type == "json":
            output_path = reporter_config.get("output_path", "./report.json")
            reporters.append(JSONReporter(output_path))
        elif reporter_type == "html":
            output_path = reporter_config.get("output_path", "./report.html")
            reporters.append(HTMLReporter(output_path))
        else:
            raise ValueError(f"Unknown reporter type: {reporter_type}")

    return reporters


def _execute_evaluations(
    eval_sets: List[EvalSet],
    providers: List[BaseProvider],
    evaluators: List[BaseEvaluator],
    num_runs: int,
    parallel_execution: bool,
    max_workers: int,
) -> List[ExecutionRun]:
    """Execute all evaluations"""
    logger = get_logger()
    execution_runs = []

    # Create tasks
    tasks = []
    for eval_set in eval_sets:
        for eval_case in eval_set.eval_cases:
            for provider in providers:
                for run_num in range(num_runs):
                    tasks.append((eval_set, eval_case, provider, evaluators, run_num + 1))

    logger.info(f"Total tasks to execute: {len(tasks)}")

    if parallel_execution and len(tasks) > 1:
        logger.info(f"Executing in parallel with {max_workers} workers")
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(_execute_single_task, *task): task for task in tasks
            }

            for future in as_completed(futures):
                try:
                    exec_run = future.result()
                    execution_runs.append(exec_run)
                except Exception as e:
                    logger.error(f"Task failed with error: {e}")
    else:
        logger.info("Executing sequentially")
        for task in tasks:
            try:
                exec_run = _execute_single_task(*task)
                execution_runs.append(exec_run)
            except Exception as e:
                logger.error(f"Task failed with error: {e}")

    return execution_runs


def _execute_single_task(
    eval_set: EvalSet,
    eval_case: EvalCase,
    provider: BaseProvider,
    evaluators: List[BaseEvaluator],
    run_number: int,
) -> ExecutionRun:
    """Execute a single evaluation task"""
    logger = get_logger()
    execution_id = str(uuid.uuid4())

    logger.info(
        f"Executing: eval_case={eval_case.eval_id}, "
        f"provider={provider.get_provider_type()}, run={run_number}"
    )

    # Execute provider
    try:
        provider_result = provider.execute(eval_case)
    except Exception as e:
        logger.error(f"Provider execution failed: {e}")
        provider_result = ProviderResult(
            conversation_history=[],
            success=False,
            error=str(e),
        )

    # Run evaluators
    evaluator_results = []
    for evaluator in evaluators:
        try:
            # Pass per-test-case evaluator config if available
            eval_result = evaluator.evaluate(
                eval_case=eval_case,
                agent_metadata=provider.agent_metadata,
                provider_result=provider_result,
                eval_config=eval_case.evaluator_config if hasattr(eval_case, 'evaluator_config') else None
            )
            evaluator_results.append(eval_result)
        except Exception as e:
            logger.error(f"Evaluator {evaluator.get_evaluator_name()} failed: {e}")

    # Determine overall success
    overall_success = provider_result.success and all(e.passed for e in evaluator_results)

    execution_run = ExecutionRun(
        execution_id=execution_id,
        run_number=run_number,
        eval_set_id=eval_set.eval_set_id,
        eval_case_id=eval_case.eval_id,
        provider_type=provider.get_provider_type(),
        provider_result=provider_result,
        evaluator_results=evaluator_results,
        overall_success=overall_success,
        eval_case=eval_case,  # Include original eval case for expected responses
    )

    logger.debug(f"Execution {execution_id} completed with status: {overall_success}")

    return execution_run


def _generate_report(execution_runs: List[ExecutionRun]) -> EvaluationReport:
    """Generate final evaluation report"""
    total_cost = sum(run.provider_result.cost for run in execution_runs)
    total_time = sum(run.provider_result.time_taken for run in execution_runs)
    success_count = sum(1 for run in execution_runs if run.overall_success)
    success_rate = success_count / len(execution_runs) if execution_runs else 0.0
    overall_success = success_rate == 1.0

    return EvaluationReport(
        execution_runs=execution_runs,
        total_cost=total_cost,
        total_time=total_time,
        success_rate=success_rate,
        overall_success=overall_success,
        summary={
            "total_executions": len(execution_runs),
            "successful_executions": success_count,
            "failed_executions": len(execution_runs) - success_count,
        },
    )
