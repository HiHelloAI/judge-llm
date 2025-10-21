# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

- [1.0.3] - Latest release with CLI fixes
- [1.0.0] - Initial release

## Upgrade Guide

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
