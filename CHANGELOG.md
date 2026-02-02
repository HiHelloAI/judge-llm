# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.20] - 2026-02-02

### Added
- Interactive Rich Live progress display during evaluation execution with real-time updates
- Per-task child progress showing provider execution and individual evaluator status
- Status markers: ▸ in-progress (yellow), ✓ completed (green), ✗ failed (red) for each step
- Evaluator scores shown inline in progress display on completion
- Recently completed tasks shown with overall pass/fail status and duration

### Changed
- Replaced static log messages with Rich-based configuration summary panels (Evaluation Configuration, Providers, Datasets, Evaluators, Reporters)
- Progress display uses `__rich_console__` renderable for thread-safe auto-refresh without deadlocks
- Provider progress shows actual turn count from result on completion
- HTML report: evaluator-first layout with score bars, thresholds, and expandable details
- HTML report: compact conversation history with side-by-side actual vs expected, chat-style markdown rendering
- HTML report: "View Full Response" per turn showing tools with args/results, sub-agents, and expected tools comparison
- HTML report: evaluator summary badges on each conversation turn
- HTML report: simple scalar metadata as inline data points, complex values as expandable JSON blocks

## [1.0.19] - 2026-02-02

### Added
- Recursive directory loading: `DirectoryLoader` now traverses all subdirectories using `rglob()` instead of `glob()`, discovering eval set files in nested folder structures
- `source_path` field on `EvalSet` and `ExecutionRun` models to track the relative file path from the dataset root directory
- Directory-based grouping in all reporters:
  - **HTML report**: sidebar groups executions by directory with folder icons and per-directory pass/fail counts; detail view shows source path
  - **Console reporter**: execution table grouped by source directory with per-group titles and pass/fail summaries; added "Source" column
  - **Database reporter**: `source_path` column in `execution_runs` table with index; auto-migration for existing databases via `ALTER TABLE`
  - **Dashboard (monitor.html)**: executions view groups by directory with folder headers, added "Source" column, source path in detail panel
- Search filter includes `source_path` in HTML report and dashboard

### Changed
- `DirectoryLoader` results are now `sorted()` for deterministic ordering
- Directory loader logs discovered files organized by directory structure

## [1.0.17] - 2026-02-02

### Changed
- HTML report: evaluator "View Details" now includes per-invocation conversation comparison — response text, tools, and sub-agents shown side-by-side with match/missing/unexpected indicators inline with each evaluator
- HTML report: detailed side-by-side comparison per invocation turn — response text, tools, and sub-agents shown with match/missing/unexpected indicators
- HTML report: evaluator "View Details" expansion now renders structured expected vs actual pairs and metrics cards instead of raw JSON
- HTML report: fixed overflow clipping on expanded evaluator detail rows
- HTML report: expandable tool args and sub-agent responses with toggle buttons
- HTML report: turn-level header with turn number badge and evaluator summary on first turn

## [1.0.14] - 2026-02-02

### Fixed
- Fixed `AttributeError: 'Invocation' object has no attribute 'agent_content'` in telemetry spans — changed to correct attribute `final_response`

## [1.0.11] - 2026-02-02

### Fixed
- Custom provider registration via `register_as` now works correctly in a single config file — registration-only entries (`type: custom` with `register_as`) are skipped during provider initialization, preventing "Unknown provider type: custom" errors
- `initial_state` is now passed explicitly in lifecycle callback context for both `on_before_session_create` and `on_after_session_create`

## [1.0.9] - 2026-02-01

### Added
- Lifecycle callbacks on `ADKHTTPProvider` for extensibility via subclassing:
  - `on_before_session_create` — modify payload, headers, or URL before session creation
  - `on_after_session_create` — inspect or act on session creation result
  - `on_before_run` — modify payload, headers, or message before sending to endpoint
  - `on_after_run` — inspect, filter, or augment events returned from a run
- Users can subclass `ADKHTTPProvider`, override only the callbacks they need, and register via config using the existing custom provider registration pattern

### Changed
- Updated README with lifecycle callbacks documentation and usage examples
- Updated version badge in README to 1.0.9

## [1.0.7] - 2026-02-01

### Added
- OpenInference semantic convention support for Arize Phoenix session and I/O visibility
- `set_openinference_attributes()` helper in `telemetry.py` for Phoenix-compatible span attributes
- Full request/response payload capture on ADK HTTP spans (`http.request.body`, `http.response.body`, `http.request.headers`, `http.response.headers`)
- `session.id` attribute on all task and provider spans for Phoenix session grouping
- `input.value` / `output.value` attributes showing actual user messages and agent responses
- `openinference.span.kind` classification: `CHAIN`, `LLM`, `TOOL`, `EVALUATOR`
- `llm.model_name` and `llm.token_count.*` via OpenInference conventions for Phoenix LLM view
- `openinference-semantic-conventions` added to `phoenix` optional dependency group

### Changed
- Enhanced `evaluate.py` spans with OpenInference attributes (session ID, input/output text, span kinds)
- Enhanced `adk_http_provider.py` spans with HTTP request/response bodies, headers, and agent response extraction
- Updated README telemetry section with Phoenix session/I/O features
- Updated version badge in README to 1.0.7

## [1.0.6] - 2026-02-01

### Added
- Optional OpenTelemetry (OTEL) instrumentation for deep observability into evaluation runs
- New `judge_llm/utils/telemetry.py` module with no-op fallback when OTEL is not installed
- Support for three telemetry exporters: Console, OTLP, and Arize Phoenix
- `--telemetry` / `-t` CLI flag to enable tracing
- `--telemetry-exporter` CLI option to select exporter (`console`, `otlp`, `phoenix`)
- YAML config support via `agent.telemetry.enabled`, `agent.telemetry.exporter`, `agent.telemetry.endpoint`
- Environment variable support: `JUDGE_LLM_TELEMETRY`, `OTEL_EXPORTER_TYPE`, `PHOENIX_COLLECTOR_ENDPOINT`
- Span instrumentation across the full evaluation lifecycle:
  - `judge_llm.evaluate` (root span with summary metrics)
  - `judge_llm.execute_task` (per eval case/provider/run)
  - `judge_llm.provider.execute` (provider calls with cost/token tracking)
  - `judge_llm.evaluator.evaluate` (evaluator results with scores)
  - `judge_llm.reporter.generate` (report generation)
  - `judge_llm.adk_http.create_session` and `judge_llm.adk_http.send_and_collect` (HTTP-level detail with retry tracking)
- New optional dependency groups in `pyproject.toml`: `telemetry` and `phoenix`
- Comprehensive telemetry documentation: `docs/docs/guides/telemetry.md`

### Changed
- Updated `judge_llm/core/evaluate.py` with telemetry span instrumentation
- Updated `judge_llm/providers/adk_http_provider.py` with HTTP-level span instrumentation
- Updated `judge_llm/cli.py` with telemetry CLI options
- Updated README.md with telemetry section, installation instructions, and feature listing
- Updated CLI reference docs with telemetry flags and examples
- Updated configuration guide with telemetry YAML config section
- Updated environment variables guide with telemetry variables
- Updated docs sidebar to include telemetry guide

## [1.0.3] - 2025-10-21

### Added
- `judge_llm/__main__.py` to enable CLI execution via `python -m judge_llm`
- `CLI_INSTALL_GUIDE.md` - Comprehensive CLI installation and troubleshooting guide
- `README_CLI.md` - Quick CLI usage reference
- `TROUBLESHOOTING.md` - Common issues and solutions guide
- `RELEASE_NOTES_1.0.3.md` - Detailed release notes for this version

### Changed
- Updated all CLI examples in README.md to use `python -m judge_llm` as the primary method
- Synchronized version numbers across all files to 1.0.3
  - `pyproject.toml`
  - `judge_llm/__init__.py`
  - `judge_llm/cli.py`

### Fixed
- CLI "command not found: judge-llm" issue by providing module execution alternative
- Version number inconsistencies across package files
- Improved user experience for installations where scripts directory is not in PATH

### Documentation
- Enhanced README.md with clear CLI usage instructions
- Added note about using `python -m judge_llm` when PATH is not configured
- Created comprehensive troubleshooting documentation for common installation issues

## [1.0.0] - 2025-10-20

### Added
- Initial release of Judge LLM framework
- Multi-provider support (Gemini, Google ADK, Mock)
- Built-in evaluators (Response, Trajectory, Cost, Latency)
- Multiple reporter types (Console, HTML, JSON, Database)
- Registry system for extensible components
- Config-driven evaluation with YAML support
- Parallel execution support
- Quality gates with configurable thresholds
- CLI interface with commands: run, validate, list, dashboard
- Python API for programmatic usage
- Environment variable support via `.env` files
- Default configuration system
- Per-test evaluator overrides
- Interactive HTML dashboard
- SQLite database reporter for persistent storage

### Features
- **Providers**:
  - Google Gemini provider with function calling
  - Google ADK provider for agent evaluation
  - Mock provider for testing
  - Custom provider registration

- **Evaluators**:
  - Response evaluator (exact match, semantic similarity, ROUGE scores)
  - Trajectory evaluator (tool usage validation)
  - Cost evaluator (token usage and cost tracking)
  - Latency evaluator (response time monitoring)
  - Custom evaluator support

- **Reporters**:
  - Console reporter with rich tables
  - HTML reporter with interactive dashboard
  - JSON reporter for machine-readable output
  - Database reporter with SQLite storage
  - Custom reporter registration

- **CLI Commands**:
  - `run` - Execute evaluations
  - `validate` - Validate configuration files
  - `list` - List available providers, evaluators, reporters
  - `dashboard` - Generate and launch evaluation dashboard

### Developer Features
- Registry-based component system
- Default configuration inheritance
- Configuration validation
- Comprehensive logging
- Type hints with Pydantic models
- Extensible architecture

---

## Release Links

- [1.0.19] - Recursive directory loading, source path tracking, directory-based report grouping
- [1.0.17] - Per-invocation comparison in evaluator View Details
- [1.0.16] - Enhanced HTML report comparison views
- [1.0.14] - Telemetry attribute fix
- [1.0.11] - Custom provider registration fix
- [1.0.9] - ADK HTTP lifecycle callbacks for extensibility
- [1.0.7] - Phoenix sessions, I/O visibility, and OpenInference support
- [1.0.6] - OpenTelemetry observability
- [1.0.3] - CLI fixes
- [1.0.0] - Initial release

## Upgrade Guide

### From 1.0.9 to 1.0.11

No breaking changes. Fixes custom provider registration when `register_as` and usage are in the same config file.

```bash
pip install --upgrade judge-llm
```

### From 1.0.7 to 1.0.9

No breaking changes. The four lifecycle callbacks (`on_before_session_create`, `on_after_session_create`, `on_before_run`, `on_after_run`) are no-ops by default. Existing code is unaffected.

```bash
pip install --upgrade judge-llm
```

### From 1.0.6 to 1.0.7

No breaking changes. Reinstall Phoenix extras to get OpenInference support:

```bash
pip install --upgrade judge-llm
pip install judge-llm[phoenix]  # now includes openinference-semantic-conventions
```

Phoenix will now show sessions, input/output content, and LLM metadata automatically.

### From 1.0.3 to 1.0.6

No breaking changes. Telemetry is disabled by default with zero overhead.

```bash
pip install --upgrade judge-llm

# Optional: install telemetry support
pip install judge-llm[telemetry]

# Optional: install Arize Phoenix support
pip install judge-llm[phoenix]
```

### From 1.0.0 to 1.0.3

No breaking changes. Simply upgrade:

```bash
pip install --upgrade judge-llm
```

If you experience "command not found: judge-llm", use:

```bash
python -m judge_llm --help
```

See [CLI_INSTALL_GUIDE.md](CLI_INSTALL_GUIDE.md) for details.

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for information on how to contribute to this project.

## Support

- **Issues**: https://github.com/HiHelloAI/judge-llm/issues
- **Documentation**: https://github.com/HiHelloAI/judge-llm#readme
