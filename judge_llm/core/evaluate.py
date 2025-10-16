"""Main evaluate function for Judge LLM framework"""

import uuid
import yaml
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from judge_llm.core.models import (
    EvalSet,
    EvalCase,
    ExecutionRun,
    EvaluationReport,
    ProviderResult,
)
from judge_llm.core.config_validator import get_validator
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


def evaluate(
    config: Optional[Union[str, Dict[str, Any]]] = None,
    dataset_path: Optional[Union[str, List[str]]] = None,
    loader: Optional[Union[BaseLoader, str]] = None,
    providers: Optional[List[Union[BaseProvider, Dict[str, Any]]]] = None,
    evaluators: Optional[List[Union[BaseEvaluator, Dict[str, Any]]]] = None,
    agent_id: Optional[str] = None,
    agent_config_path: Optional[str] = None,
    agent_metadata: Optional[Dict[str, Any]] = None,
    num_runs: int = 1,
    parallel_execution: bool = False,
    max_workers: int = 4,
    reporters: Optional[List[Union[BaseReporter, Dict[str, Any]]]] = None,
    log_level: str = "INFO",
    validate_config: bool = True,
    **provider_metadata,
) -> EvaluationReport:
    """Main evaluation function

    Args:
        config: Configuration file path or dictionary
        dataset_path: Path(s) to dataset files
        loader: Loader instance or type string
        providers: List of provider instances or config dicts
        evaluators: List of evaluator instances or config dicts
        agent_id: Agent identifier
        agent_config_path: Path to agent configuration
        agent_metadata: Agent metadata dictionary
        num_runs: Number of runs per eval case
        parallel_execution: Enable parallel execution
        max_workers: Maximum worker threads for parallel execution
        reporters: List of reporter instances or config dicts
        log_level: Logging level
        validate_config: Validate configuration before execution
        **provider_metadata: Additional provider metadata

    Returns:
        EvaluationReport with all results
    """
    logger = get_logger()
    set_log_level(log_level)

    logger.info("Starting Judge LLM evaluation")

    # Load configuration if provided
    if config is not None:
        config_dict = _load_config(config)
        return _evaluate_from_config(config_dict, validate_config)

    # Build configuration from arguments
    config_dict = _build_config_from_args(
        dataset_path=dataset_path,
        loader=loader,
        providers=providers,
        evaluators=evaluators,
        agent_id=agent_id,
        agent_config_path=agent_config_path,
        agent_metadata=agent_metadata,
        num_runs=num_runs,
        parallel_execution=parallel_execution,
        max_workers=max_workers,
        reporters=reporters,
        log_level=log_level,
        provider_metadata=provider_metadata,
    )

    return _evaluate_from_config(config_dict, validate_config)


def _load_config(config: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
    """Load configuration from file or use provided dict"""
    logger = get_logger()

    if isinstance(config, dict):
        return config

    config_path = Path(config).expanduser().resolve()
    logger.info(f"Loading configuration from {config_path}")

    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def _build_config_from_args(**kwargs) -> Dict[str, Any]:
    """Build configuration dictionary from function arguments"""
    config = {
        "agent": {
            "log_level": kwargs.get("log_level", "INFO"),
            "num_runs": kwargs.get("num_runs", 1),
            "parallel_execution": kwargs.get("parallel_execution", False),
            "max_workers": kwargs.get("max_workers", 4),
        },
        "dataset": {
            "loader": kwargs.get("loader") or "local_file",
            "paths": kwargs.get("dataset_path") or [],
        },
        "providers": kwargs.get("providers") or [],
        "evaluators": kwargs.get("evaluators") or [],
        "reporters": kwargs.get("reporters") or [],
    }

    return config


def _evaluate_from_config(config: Dict[str, Any], validate: bool = True) -> EvaluationReport:
    """Execute evaluation from configuration dictionary"""
    logger = get_logger()

    # Validate configuration
    if validate:
        validator = get_validator()
        is_valid, errors = validator.validate(config)

        if not is_valid:
            error_msg = "Configuration validation failed:\n" + "\n".join(f"  - {e}" for e in errors)
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

    # Load datasets
    logger.info("Loading datasets")
    eval_sets = _load_datasets(dataset_config)
    logger.info(f"Loaded {len(eval_sets)} eval set(s)")

    # Initialize providers
    logger.info("Initializing providers")
    providers = _initialize_providers(providers_config)
    logger.info(f"Initialized {len(providers)} provider(s)")

    # Initialize evaluators
    logger.info("Initializing evaluators")
    evaluators = _initialize_evaluators(evaluators_config)
    logger.info(f"Initialized {len(evaluators)} evaluator(s)")

    # Execute evaluations
    logger.info("Executing evaluations")
    execution_runs = _execute_evaluations(
        eval_sets=eval_sets,
        providers=providers,
        evaluators=evaluators,
        num_runs=agent_config.get("num_runs", 1),
        parallel_execution=agent_config.get("parallel_execution", False),
        max_workers=agent_config.get("max_workers", 4),
    )

    # Generate report
    logger.info("Generating evaluation report")
    report = _generate_report(execution_runs)

    # Generate reports via reporters
    logger.info("Generating reports via reporters")
    reporters = _initialize_reporters(reporters_config)
    for reporter in reporters:
        reporter.generate_report(report)
        reporter.cleanup()

    # Cleanup resources
    logger.info("Cleaning up resources")
    for provider in providers:
        provider.cleanup()

    logger.info("Evaluation completed")

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


def _initialize_providers(providers_config: List[Dict[str, Any]]) -> List[BaseProvider]:
    """Initialize providers from configuration"""
    registry = get_provider_registry()
    providers = []

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
            eval_result = evaluator.evaluate(
                eval_case=eval_case,
                agent_metadata=provider.agent_metadata,
                provider_result=provider_result,
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
