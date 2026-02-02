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
from judge_llm.core.registry import get_provider_registry, get_evaluator_registry, get_reporter_registry
from judge_llm.loaders.base import BaseLoader
from judge_llm.loaders.local_file_loader import LocalFileLoader
from judge_llm.loaders.directory_loader import DirectoryLoader
from judge_llm.providers.base import BaseProvider
from judge_llm.evaluators.base import BaseEvaluator
from judge_llm.reporters.base import BaseReporter
from judge_llm.reporters.console_reporter import ConsoleReporter
from judge_llm.reporters.json_reporter import JSONReporter
from judge_llm.reporters.html_reporter import HTMLReporter
from judge_llm.reporters.database_reporter import DatabaseReporter
from judge_llm.utils.logger import get_logger, set_log_level
from judge_llm.utils.telemetry import (
    trace_span,
    set_span_attributes,
    record_span_event,
    maybe_init_from_config,
    shutdown_telemetry,
    set_openinference_attributes,
)


def _print_configuration_summary(
    agent_config: Dict[str, Any],
    dataset_config: Dict[str, Any],
    providers_config: List[Dict[str, Any]],
    evaluators_config: List[Dict[str, Any]],
    reporters_config: List[Dict[str, Any]],
):
    """Print a detailed summary of the evaluation configuration using Rich"""
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.columns import Columns
    from rich.text import Text

    console = Console()

    # --- Agent / Execution Settings ---
    num_runs = agent_config.get('num_runs', 1)
    parallel = agent_config.get('parallel_execution', False)
    max_workers = agent_config.get('max_workers', 4)
    log_level = agent_config.get('log_level', 'INFO')
    fail_on_threshold = agent_config.get('fail_on_threshold_violation', True)

    exec_table = Table(show_header=False, box=None, padding=(0, 2))
    exec_table.add_column(style="cyan bold")
    exec_table.add_column()
    exec_table.add_row("Runs", str(num_runs))
    exec_table.add_row("Parallel", f"Yes ({max_workers} workers)" if parallel else "No")
    exec_table.add_row("Log Level", log_level)
    exec_table.add_row("Fail on Threshold", "Yes" if fail_on_threshold else "No")

    console.print(Panel(exec_table, title="[bold]Evaluation Configuration[/bold]", border_style="cyan"))

    # --- Providers ---
    prov_table = Table(box=None, padding=(0, 2))
    prov_table.add_column("Agent ID", style="green bold")
    prov_table.add_column("Type")
    prov_table.add_column("Model")
    prov_table.add_column("Extra")
    for p in providers_config:
        agent_id = p.get('agent_id', 'N/A')
        ptype = p.get('type', 'unknown')
        model = p.get('model', '-')
        # Show other notable keys
        skip_keys = {'type', 'agent_id', 'model', 'agent_config_path', 'agent_metadata',
                     'register_as', 'module_path', 'class_name'}
        extras = {k: v for k, v in p.items() if k not in skip_keys}
        extras_str = ", ".join(f"{k}={v}" for k, v in extras.items()) if extras else "-"
        prov_table.add_row(agent_id, ptype, str(model), extras_str)

    console.print(Panel(prov_table, title="[bold]Providers[/bold]", border_style="green"))

    # --- Datasets ---
    paths = dataset_config.get('paths', [])
    loader_type = dataset_config.get('loader', 'local_file')
    ds_table = Table(box=None, padding=(0, 2))
    ds_table.add_column("Loader", style="yellow bold")
    ds_table.add_column("Path")
    for path in paths:
        ds_table.add_row(loader_type, path)
    if not paths:
        ds_table.add_row(loader_type, "(none)")

    console.print(Panel(ds_table, title="[bold]Datasets[/bold]", border_style="yellow"))

    # --- Evaluators ---
    eval_table = Table(box=None, padding=(0, 2))
    eval_table.add_column("Name", style="magenta bold")
    eval_table.add_column("Type")
    eval_table.add_column("Enabled")
    eval_table.add_column("Config")
    for e in evaluators_config:
        name = e.get('name', e.get('type', 'unknown'))
        etype = e.get('type', 'unknown')
        enabled = "Yes" if e.get('enabled', True) else "No"
        cfg = e.get('config', {})
        cfg_str = ", ".join(f"{k}={v}" for k, v in cfg.items()) if cfg else "-"
        eval_table.add_row(name, etype, enabled, cfg_str)

    console.print(Panel(eval_table, title="[bold]Evaluators[/bold]", border_style="magenta"))

    # --- Reporters ---
    rep_table = Table(box=None, padding=(0, 2))
    rep_table.add_column("Type", style="blue bold")
    rep_table.add_column("Config")
    for r in reporters_config:
        rtype = r.get('type', 'unknown')
        skip = {'type'}
        cfg = {k: v for k, v in r.items() if k not in skip}
        cfg_str = ", ".join(f"{k}={v}" for k, v in cfg.items()) if cfg else "-"
        rep_table.add_row(rtype, cfg_str)

    console.print(Panel(rep_table, title="[bold]Reporters[/bold]", border_style="blue"))
    console.print()


def evaluate(
    config: Optional[Union[str, Dict[str, Any]]] = None,
    agent: Optional[Dict[str, Any]] = None,
    dataset: Optional[Dict[str, Any]] = None,
    providers: Optional[List[Dict[str, Any]]] = None,
    evaluators: Optional[List[Dict[str, Any]]] = None,
    reporters: Optional[List[Dict[str, Any]]] = None,
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
                "fail_on_threshold_violation": True
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

    # Initialize telemetry from config if enabled
    maybe_init_from_config(config_dict.get("agent", {}))

    try:
        return _evaluate_from_config(config_dict)
    finally:
        shutdown_telemetry()


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


def _evaluate_from_config(config: Dict[str, Any]) -> EvaluationReport:
    """Execute evaluation from configuration dictionary"""
    logger = get_logger()

    # Register custom components from config (if any)
    _process_provider_registrations(config)
    _process_evaluator_registrations(config)
    _process_reporter_registrations(config)

    # Validate configuration (always required for consistency)
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
    with trace_span("judge_llm.evaluate", attributes={
        "judge_llm.num_providers": len(providers),
        "judge_llm.num_evaluators": len(evaluators),
        "judge_llm.num_eval_sets": len(eval_sets),
        "judge_llm.num_runs": agent_config.get("num_runs", 1),
        "judge_llm.parallel": agent_config.get("parallel_execution", False),
    }) as root_span:
        if root_span:
            set_openinference_attributes(
                root_span,
                span_kind="CHAIN",
                input_value=f"Evaluating {len(eval_sets)} eval set(s) with {len(providers)} provider(s)",
            )

        execution_runs, wall_clock_time = _execute_evaluations(
            eval_sets=eval_sets,
            providers=providers,
            evaluators=evaluators,
            num_runs=agent_config.get("num_runs", 1),
            parallel_execution=agent_config.get("parallel_execution", False),
            max_workers=agent_config.get("max_workers", 4),
        )

        # Generate report
        logger.debug("Generating evaluation report")
        report = _generate_report(execution_runs, wall_clock_time)

        if root_span:
            set_span_attributes(root_span, {
                "judge_llm.total_executions": len(execution_runs),
                "judge_llm.success_rate": report.success_rate,
                "judge_llm.total_cost": report.total_cost,
                "judge_llm.total_time": report.total_time,
            })

        # Generate reports via reporters
        logger.debug("Generating reports via reporters")
        reporters = _initialize_reporters(reporters_config)
        for reporter in reporters:
            with trace_span("judge_llm.reporter.generate", attributes={
                "judge_llm.reporter.type": reporter.__class__.__name__,
            }):
                reporter.generate_report(report)
                reporter.cleanup()

    # Cleanup resources
    logger.debug("Cleaning up resources")
    for provider in providers:
        provider.cleanup()

    # Check for threshold violations if fail_on_threshold_violation is enabled
    fail_on_threshold_violation = agent_config.get("fail_on_threshold_violation", True)
    if fail_on_threshold_violation and not report.overall_success:
        failed_count = report.summary.get("failed_executions", 0)
        total_count = report.summary.get("total_executions", 0)
        error_msg = (
            f"\n{'='*80}\n"
            f"  THRESHOLD VIOLATION DETECTED\n"
            f"{'='*80}\n\n"
            f"❌ {failed_count}/{total_count} evaluation(s) failed to meet thresholds\n"
            f"Success rate: {report.success_rate:.1%} (100% required)\n\n"
            f"Failed evaluation cases:\n"
        )

        # List failed cases
        for run in execution_runs:
            if not run.overall_success:
                error_msg += f"  • {run.eval_case_id} (run {run.run_number})"

                # Show which evaluators failed
                failed_evaluators = [e for e in run.evaluator_results if not e.passed]
                if failed_evaluators:
                    eval_names = ", ".join([e.evaluator_type for e in failed_evaluators])
                    error_msg += f" - Failed: {eval_names}"
                error_msg += "\n"

        error_msg += (
            f"\n{'='*80}\n"
            f"💡 TIP: Set 'fail_on_threshold_violation: false' in agent config to continue\n"
            f"        despite threshold violations (useful for monitoring/testing)\n"
            f"{'='*80}\n"
        )

        logger.error(error_msg)
        raise ValueError(error_msg)

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
    execution_keys = {"num_runs", "parallel_execution", "max_workers", "fail_on_threshold_violation", "log_level"}
    agent_metadata = {
        k: v
        for k, v in agent_config.items()
        if k not in execution_keys
    }

    for provider_config in providers_config:
        provider_type = provider_config.get("type")
        if not provider_type:
            raise ValueError("Provider type is required")

        # Skip registration-only entries (no agent_id = not meant to be instantiated)
        if "register_as" in provider_config and not provider_config.get("agent_id"):
            continue

        provider_class = registry.get(provider_type)
        if not provider_class:
            raise ValueError(f"Unknown provider type: {provider_type}")

        # Extract provider configuration
        agent_id = provider_config.get("agent_id")
        agent_config_path = provider_config.get("agent_config_path")

        # All other config items are passed as provider_metadata
        # Exclude agent_metadata as it's passed separately
        provider_metadata = {
            k: v
            for k, v in provider_config.items()
            if k not in ["type", "agent_id", "agent_config_path", "agent_metadata", "register_as", "module_path", "class_name"]
        }

        # Use provider-specific agent_metadata if provided, otherwise use global agent_metadata
        provider_agent_metadata = provider_config.get("agent_metadata", agent_metadata)

        provider = provider_class(
            agent_id=agent_id,
            agent_config_path=agent_config_path,
            agent_metadata=provider_agent_metadata,
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
    logger = get_logger()
    reporters = []
    reporter_registry = get_reporter_registry()

    for reporter_config in reporters_config:
        reporter_type = reporter_config.get("type")
        
        # Check for custom reporter
        if reporter_type == "custom":
            module_path = reporter_config.get("module_path")
            class_name = reporter_config.get("class_name")
            
            if not module_path or not class_name:
                raise ValueError(
                    "Custom reporter requires 'module_path' and 'class_name' in configuration"
                )
            
            # Load custom reporter
            reporter_class = reporter_registry.load_custom_reporter(module_path, class_name)
        else:
            # Get reporter from registry
            reporter_class = reporter_registry.get(reporter_type)
            
            if not reporter_class:
                raise ValueError(f"Unknown reporter type: {reporter_type}")
        
        # Initialize reporter based on type
        if reporter_type == "console":
            reporter = reporter_class()
        elif reporter_type == "json":
            output_path = reporter_config.get("output_path", "./report.json")
            reporter = reporter_class(output_path)
        elif reporter_type == "html":
            output_path = reporter_config.get("output_path", "./report.html")
            reporter = reporter_class(output_path)
        elif reporter_type == "database":
            db_path = reporter_config.get("db_path", "./judge_llm_results.db")
            reporter = reporter_class(db_path)
        elif reporter_type == "custom":
            # Custom reporters should accept config dict
            reporter = reporter_class(config=reporter_config.get("config", {}))
        else:
            raise ValueError(f"Unknown reporter type: {reporter_type}")
        
        reporters.append(reporter)

    return reporters


def _execute_evaluations(
    eval_sets: List[EvalSet],
    providers: List[BaseProvider],
    evaluators: List[BaseEvaluator],
    num_runs: int,
    parallel_execution: bool,
    max_workers: int,
) -> tuple[List[ExecutionRun], float]:
    """Execute all evaluations.

    Returns:
        Tuple of (execution_runs, wall_clock_time_seconds)
    """
    from rich.console import Console
    from rich.live import Live
    from rich.text import Text

    logger = get_logger()
    console = Console()
    execution_runs = []

    # Create tasks
    tasks = []
    for eval_set in eval_sets:
        for eval_case in eval_set.eval_cases:
            for provider in providers:
                for run_num in range(num_runs):
                    tasks.append((eval_set, eval_case, provider, evaluators, run_num + 1))

    total = len(tasks)
    logger.debug(f"Total tasks to execute: {total}")

    # Track wall-clock time for the entire execution
    import time
    start_time = time.time()
    completed = 0

    def _make_status(phase: str, detail: str = "") -> Text:
        elapsed = time.time() - start_time
        parts = Text()
        parts.append(f"  [{completed}/{total}] ", style="bold cyan")
        parts.append(f"{phase}", style="bold")
        if detail:
            parts.append(f" {detail}", style="dim")
        parts.append(f"  ({elapsed:.1f}s)", style="dim")
        return parts

    with Live(_make_status("Starting evaluation..."), console=console, refresh_per_second=4, transient=True) as live:
        if parallel_execution and len(tasks) > 1:
            logger.debug(f"Executing in parallel with {max_workers} workers")
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = {}
                for task in tasks:
                    _, eval_case, provider, _, run_num = task
                    futures[executor.submit(_execute_single_task, *task)] = (
                        eval_case.eval_id, provider.get_provider_type(), run_num
                    )
                live.update(_make_status("Running evaluations in parallel...", f"({max_workers} workers)"))

                for future in as_completed(futures):
                    eval_id, prov_type, run_num = futures[future]
                    success = False
                    try:
                        exec_run = future.result()
                        execution_runs.append(exec_run)
                        success = exec_run.overall_success
                    except Exception as e:
                        logger.error(f"Task failed with error: {e}")
                    completed += 1
                    status = "✓" if success else "✗"
                    live.update(_make_status(
                        f"{status} {eval_id}",
                        f"provider={prov_type} run={run_num}"
                    ))
        else:
            logger.debug("Executing sequentially")
            for task in tasks:
                _, eval_case, provider, _, run_num = task
                live.update(_make_status(
                    f"▶ {eval_case.eval_id}",
                    f"provider={provider.get_provider_type()} run={run_num}"
                ))
                success = False
                try:
                    exec_run = _execute_single_task(*task)
                    execution_runs.append(exec_run)
                    success = exec_run.overall_success
                except Exception as e:
                    logger.error(f"Task failed with error: {e}")
                completed += 1
                status = "✓" if success else "✗"
                live.update(_make_status(
                    f"{status} {eval_case.eval_id}",
                    f"provider={provider.get_provider_type()} run={run_num}"
                ))

    wall_clock_time = time.time() - start_time
    console.print(f"  [bold green]✓[/bold green] Completed {total} evaluation(s) in {wall_clock_time:.1f}s")

    return execution_runs, wall_clock_time


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

    logger.debug(
        f"Executing: eval_case={eval_case.eval_id}, "
        f"provider={provider.get_provider_type()}, run={run_number}"
    )

    # Extract input text from conversation for telemetry
    input_texts = []
    for inv in eval_case.conversation:
        for part in inv.user_content.parts:
            if part.text:
                input_texts.append(part.text)
    input_summary = " | ".join(input_texts) if input_texts else ""

    # Session ID for Phoenix session grouping
    session_id = getattr(eval_case.session_input, 'session_id', None) or eval_case.eval_id

    with trace_span("judge_llm.execute_task", attributes={
        "judge_llm.eval_case_id": eval_case.eval_id,
        "judge_llm.eval_set_id": eval_set.eval_set_id,
        "judge_llm.provider_type": provider.get_provider_type(),
        "judge_llm.run_number": run_number,
    }) as task_span:
        if task_span:
            set_openinference_attributes(
                task_span,
                span_kind="CHAIN",
                session_id=session_id,
                input_value=input_summary,
            )

        # Execute provider (track time at framework level)
        import time
        start_time = time.time()

        with trace_span("judge_llm.provider.execute", attributes={
            "judge_llm.provider_type": provider.get_provider_type(),
            "judge_llm.agent_id": provider.agent_id,
        }) as provider_span:
            if provider_span:
                set_openinference_attributes(
                    provider_span,
                    span_kind="LLM",
                    session_id=session_id,
                    input_value=input_summary,
                    model_name=getattr(provider, 'model', provider.get_provider_type()),
                )
            try:
                provider_result = provider.execute(eval_case)
            except Exception as e:
                logger.error(f"Provider execution failed: {e}")
                provider_result = ProviderResult(
                    conversation_history=[],
                    success=False,
                    error=str(e),
                )

            if provider_span:
                set_span_attributes(provider_span, {
                    "judge_llm.provider.success": provider_result.success,
                    "judge_llm.provider.cost": provider_result.cost,
                    "judge_llm.provider.token_usage.total": provider_result.token_usage.get("total_tokens", 0),
                })
                # Extract response text for Phoenix visibility
                output_texts = []
                for inv in provider_result.conversation_history:
                    if inv.final_response:
                        for part in inv.final_response.parts:
                            if part.text:
                                output_texts.append(part.text)
                output_summary = " | ".join(output_texts) if output_texts else ""
                set_openinference_attributes(
                    provider_span,
                    output_value=output_summary,
                    token_count_prompt=provider_result.token_usage.get("prompt_tokens"),
                    token_count_completion=provider_result.token_usage.get("completion_tokens"),
                    token_count_total=provider_result.token_usage.get("total_tokens"),
                )
                if provider_result.error:
                    record_span_event(provider_span, "provider_error", {
                        "error": provider_result.error,
                    })

        # Set time_taken at framework level if provider didn't set it
        execution_time = time.time() - start_time
        if provider_result.time_taken == 0:
            provider_result = ProviderResult(
                conversation_history=provider_result.conversation_history,
                cost=provider_result.cost,
                time_taken=execution_time,
                token_usage=provider_result.token_usage,
                metadata=provider_result.metadata,
                success=provider_result.success,
                error=provider_result.error,
            )

        # Run evaluators
        evaluator_results = []
        for evaluator in evaluators:
            with trace_span("judge_llm.evaluator.evaluate", attributes={
                "judge_llm.evaluator.name": evaluator.get_evaluator_name(),
            }) as eval_span:
                try:
                    evaluator_specific_config = None
                    if hasattr(eval_case, 'evaluator_config') and eval_case.evaluator_config:
                        evaluator_name = evaluator.get_evaluator_name()
                        evaluator_specific_config = eval_case.evaluator_config.get(evaluator_name, None)

                    eval_result = evaluator.evaluate(
                        eval_case=eval_case,
                        agent_metadata=provider.agent_metadata,
                        provider_result=provider_result,
                        eval_config=evaluator_specific_config
                    )
                    evaluator_results.append(eval_result)

                    if eval_span:
                        set_span_attributes(eval_span, {
                            "judge_llm.evaluator.passed": eval_result.passed,
                            "judge_llm.evaluator.score": eval_result.score if eval_result.score is not None else -1,
                        })
                        eval_output = f"passed={eval_result.passed}, score={eval_result.score}"
                        if hasattr(eval_result, 'details') and eval_result.details:
                            eval_output += f", details={eval_result.details}"
                        set_openinference_attributes(
                            eval_span,
                            span_kind="EVALUATOR",
                            output_value=eval_output,
                        )
                except Exception as e:
                    logger.error(f"Evaluator {evaluator.get_evaluator_name()} failed: {e}")

        # Determine overall success
        overall_success = provider_result.success and all(e.passed for e in evaluator_results)

        if task_span:
            set_span_attributes(task_span, {
                "judge_llm.task.success": overall_success,
            })
            # Set output on the task span for Phoenix
            task_output_parts = []
            for inv in provider_result.conversation_history:
                if inv.final_response:
                    for part in inv.final_response.parts:
                        if part.text:
                            task_output_parts.append(part.text)
            set_openinference_attributes(
                task_span,
                output_value=" | ".join(task_output_parts) if task_output_parts else f"success={overall_success}",
            )

        execution_run = ExecutionRun(
            execution_id=execution_id,
            run_number=run_number,
            eval_set_id=eval_set.eval_set_id,
            eval_case_id=eval_case.eval_id,
            provider_type=provider.get_provider_type(),
            provider_result=provider_result,
            evaluator_results=evaluator_results,
            overall_success=overall_success,
            eval_case=eval_case,
            source_path=eval_set.source_path,
        )

        logger.debug(f"Execution {execution_id} completed with status: {overall_success}")

        return execution_run


def _generate_report(execution_runs: List[ExecutionRun], wall_clock_time: float = None) -> EvaluationReport:
    """Generate final evaluation report.

    Args:
        execution_runs: List of execution runs
        wall_clock_time: Actual wall-clock time for all executions (for parallel runs)
                        If None, will sum individual execution times (for sequential)
    """
    total_cost = sum(run.provider_result.cost for run in execution_runs)

    # Use wall-clock time if provided (parallel execution), otherwise sum individual times (sequential)
    if wall_clock_time is not None:
        total_time = wall_clock_time
    else:
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


def _process_reporter_registrations(config: Dict[str, Any]):
    """Process reporter registrations from config
    
    This allows registering custom reporters in default config that can be
    referenced by name in actual configs.
    
    In default config:
        reporters:
          - type: custom
            module_path: ./my_reporters/csv_reporter.py
            class_name: CSVReporter
            register_as: csv  # Register this reporter globally
            
    In actual config:
        reporters:
          - type: csv  # Use the registered reporter
            config:
              output_path: ./results.csv
    
    Args:
        config: Configuration dictionary
    """
    logger = get_logger()
    reporter_registry = get_reporter_registry()
    
    reporters_config = config.get("reporters", [])
    
    for reporter_config in reporters_config:
        # Check if this is a custom reporter that should be registered
        if reporter_config.get("type") == "custom" and "register_as" in reporter_config:
            register_as = reporter_config.get("register_as")
            module_path = reporter_config.get("module_path")
            class_name = reporter_config.get("class_name")
            
            if not module_path or not class_name:
                logger.warning(
                    f"Cannot register reporter '{register_as}': missing module_path or class_name"
                )
                continue
            
            # Check if already registered
            if reporter_registry.has(register_as):
                logger.debug(f"Reporter '{register_as}' already registered, skipping")
                continue
            
            try:
                # Load the custom reporter class
                reporter_class = reporter_registry.load_custom_reporter(module_path, class_name)
                
                # Register it with the specified name
                reporter_registry.register(register_as, reporter_class)
                
                logger.info(f"✓ Registered custom reporter '{register_as}' from {module_path}")
                
            except Exception as e:
                logger.warning(f"Failed to register reporter '{register_as}': {e}")


def _process_evaluator_registrations(config: Dict[str, Any]):
    """Process evaluator registrations from config
    
    This allows registering custom evaluators in default config that can be
    referenced by name in actual configs.
    
    In default config:
        evaluators:
          - type: custom
            module_path: ./my_evaluators/safety.py
            class_name: SafetyEvaluator
            register_as: safety  # Register this evaluator globally
            
    In actual config:
        evaluators:
          - type: safety  # Use the registered evaluator
            config:
              severity_threshold: high
    
    Args:
        config: Configuration dictionary
    """
    logger = get_logger()
    evaluator_registry = get_evaluator_registry()
    
    evaluators_config = config.get("evaluators", [])
    
    for evaluator_config in evaluators_config:
        # Check if this is a custom evaluator that should be registered
        if evaluator_config.get("type") == "custom" and "register_as" in evaluator_config:
            register_as = evaluator_config.get("register_as")
            module_path = evaluator_config.get("module_path")
            class_name = evaluator_config.get("class_name")
            
            if not module_path or not class_name:
                logger.warning(
                    f"Cannot register evaluator '{register_as}': missing module_path or class_name"
                )
                continue
            
            # Check if already registered
            if evaluator_registry.has(register_as):
                logger.debug(f"Evaluator '{register_as}' already registered, skipping")
                continue
            
            try:
                # Load the custom evaluator class
                evaluator_class = evaluator_registry.load_custom_evaluator(module_path, class_name)
                
                # Register it with the specified name
                evaluator_registry.register(register_as, evaluator_class)
                
                logger.info(f"✓ Registered custom evaluator '{register_as}' from {module_path}")
                
            except Exception as e:
                logger.warning(f"Failed to register evaluator '{register_as}': {e}")


def _process_provider_registrations(config: Dict[str, Any]):
    """Process provider registrations from config
    
    This allows registering custom providers in default config that can be
    referenced by name in actual configs.
    
    In default config:
        providers:
          - type: custom
            module_path: ./my_providers/custom_llm.py
            class_name: CustomLLMProvider
            register_as: custom_llm  # Register this provider globally
            
    In actual config:
        providers:
          - type: custom_llm  # Use the registered provider
            agent_id: my_agent
            config:
              api_key: ${MY_API_KEY}
    
    Args:
        config: Configuration dictionary
    """
    logger = get_logger()
    provider_registry = get_provider_registry()
    
    providers_config = config.get("providers", [])
    
    for provider_config in providers_config:
        # Check if this is a custom provider that should be registered
        # Support both: type=custom with register_as, and merged configs where
        # register_as + module_path + class_name survive from defaults even if type was overwritten
        if "register_as" in provider_config and "module_path" in provider_config and "class_name" in provider_config:
            register_as = provider_config.get("register_as")
            module_path = provider_config.get("module_path")
            class_name = provider_config.get("class_name")
            
            if not module_path or not class_name:
                logger.warning(
                    f"Cannot register provider '{register_as}': missing module_path or class_name"
                )
                continue
            
            # Check if already registered
            if provider_registry.has(register_as):
                logger.debug(f"Provider '{register_as}' already registered, skipping")
                continue
            
            try:
                # Load the custom provider class
                # For providers, we need to use importlib directly since there's no load_custom_provider method
                from pathlib import Path
                import importlib.util
                import sys
                
                path = Path(module_path).expanduser().resolve()
                
                if not path.exists():
                    raise FileNotFoundError(f"Module file not found: {module_path}")
                
                # Create a unique module name
                module_name = f"custom_provider_{path.stem}_{id(path)}"
                
                # Load the module
                spec = importlib.util.spec_from_file_location(module_name, path)
                if spec is None or spec.loader is None:
                    raise ImportError(f"Cannot load module from {module_path}")
                
                module = importlib.util.module_from_spec(spec)
                sys.modules[module_name] = module
                spec.loader.exec_module(module)
                
                # Get the class
                if not hasattr(module, class_name):
                    raise AttributeError(f"Class {class_name} not found in {module_path}")
                
                provider_class = getattr(module, class_name)
                
                # Validate that it inherits from BaseProvider
                from judge_llm.providers.base import BaseProvider
                if not issubclass(provider_class, BaseProvider):
                    raise TypeError(f"Class {class_name} must inherit from BaseProvider")
                
                # Register it with the specified name
                provider_registry.register(register_as, provider_class)
                
                logger.info(f"✓ Registered custom provider '{register_as}' from {module_path}")
                
            except Exception as e:
                logger.warning(f"Failed to register provider '{register_as}': {e}")
