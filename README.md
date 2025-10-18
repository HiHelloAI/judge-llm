<div align="center">
  <img src="assets/icon.png" alt="Judge LLM" width="200"/>

  # JUDGE LLM

  A lightweight, extensible Python framework for **evaluating and comparing LLM providers**. Test your AI agents systematically with multi-turn conversations, cost tracking, and comprehensive reporting.

  [Quick Start](#quick-start) • [Demo](#demo) • [Features](#features) • [Examples](#testing-examples) • [Reports](#reports--dashboard)
</div>

## Purpose

JUDGE LLM helps you **evaluate AI agents and LLM providers** by running test cases against your models and measuring:
- **Response quality** (exact matching, semantic similarity, ROUGE scores)
- **Cost & latency** (token usage, execution time, budget compliance)
- **Conversation flow** (tool uses, multi-turn interactions)
- **Safety & custom metrics** (extensible evaluation logic)

Perfect for regression testing, A/B testing providers, and ensuring production-grade quality.

## Features

- **Multiple Providers**: Gemini, Mock, and custom providers
- **Built-in Evaluators**: Response similarity, trajectory validation, cost/latency checks
- **Extensible**: Plugin system for custom evaluators and providers
- **Rich Reports**: Console tables, interactive HTML dashboard, JSON exports, SQLite database
- **Parallel Execution**: Run evaluations concurrently with configurable workers
- **Config-Driven**: YAML configs with smart defaults or programmatic Python API
- **Per-Test Overrides**: Fine-tune evaluator thresholds per test case

## Installation

### From Source

```bash
git clone https://github.com/yourusername/judge-llm.git
cd judge-llm
pip install -e .
```

### From PyPI (when published)

```bash
pip install judge-llm
```

### With Optional Dependencies

```bash
# Install with Gemini provider support
pip install judge-llm[gemini]

# Install with dev dependencies
pip install judge-llm[dev]
```

### Setup Environment Variables

JUDGE LLM automatically loads environment variables from a `.env` file:

```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your API keys
nano .env
```

**`.env` file:**
```bash
# Google Gemini API Key
GOOGLE_API_KEY=your-google-api-key-here
```

The `.env` file is automatically loaded when you import the library or run the CLI. **Never commit `.env` to version control** - it's already in `.gitignore`.

## Quick Start

### CLI Usage

```bash
# Run evaluation from config file
judge-llm run --config config.yaml

# Run with inline arguments
judge-llm run --dataset ./data/eval.json --provider mock --agent-id my_agent --report html --output report.html

# Validate configuration
judge-llm validate --config config.yaml

# List available components
judge-llm list providers
judge-llm list evaluators

# Generate dashboard from database
judge-llm dashboard --db results.db --output dashboard.html
```

### Python API

```python
from judge_llm import evaluate

# From config file
report = evaluate(config="config.yaml")

# Programmatic API
report = evaluate(
    dataset={"loader": "local_file", "paths": ["./data/eval.json"]},
    providers=[{"type": "mock", "agent_id": "my_agent"}],
    evaluators=[{"type": "response_evaluator", "config": {"similarity_threshold": 0.8}}],
    reporters=[{"type": "console"}, {"type": "html", "output_path": "./report.html"}]
)

print(f"Success: {report.success_rate:.1%} | Cost: ${report.total_cost:.4f}")
```

## Demo

<div align="center">
  <img src="assets/judge-llm.gif" alt="Judge LLM Demo" width="100%"/>
</div>

## Configuration

**Minimal config.yaml:**
```yaml
dataset:
  loader: local_file
  paths: [./data/eval.json]

providers:
  - type: gemini
    agent_id: my_agent
    model: gemini-2.0-flash-exp

evaluators:
  - type: response_evaluator
    config: {similarity_threshold: 0.8}

reporters:
  - type: console
  - type: html
    output_path: ./report.html
```

See the [examples/](examples/) directory for complete configuration examples including default configs, custom evaluators, and advanced features.

## Testing Examples

Explore **6 complete examples** in the `examples/` directory:

| Example | Description |
|---------|-------------|
| **01-gemini-agent** | Real Gemini API evaluation with response & trajectory checks |
| **02-default-config** | Reusable config patterns with `.judge_llm.defaults.yaml` |
| **03-custom-evaluator** | Build custom evaluators (sentiment analysis example) |
| **04-safety-long-conversation** | Multi-turn safety evaluation (PII, toxicity, hate speech) |
| **05-evaluator-config-override** | Per-test-case threshold overrides |
| **06-database-reporter** | SQLite persistence for historical tracking & trend analysis |

Each example includes config files, datasets, and instructions. Run any example:

```bash
cd examples/01-gemini-agent
judge-llm run --config config.yaml
```

## Built-in Components

### Providers
- **Gemini** - `pip install judge-llm[gemini]` (requires `GOOGLE_API_KEY` in `.env`)
- **Mock** - Built-in, no setup required
- **Custom** - Extend `BaseProvider` for your own LLM providers

### Evaluators
- **ResponseEvaluator** - Compare responses (exact, semantic similarity, ROUGE)
- **TrajectoryEvaluator** - Validate tool uses and conversation flow
- **CostEvaluator** - Enforce cost thresholds
- **LatencyEvaluator** - Enforce latency thresholds
- **Custom** - Extend `BaseEvaluator` for custom logic

## Reports & Dashboard

### HTML Dashboard
Interactive web interface with:
- **Sidebar**: Summary metrics + execution list with color-coded status
- **Main Panel**: Execution details, evaluator scores, conversation history
- **Features**: Dark mode, responsive, self-contained (works offline)

### Console Output
Rich formatted tables with live execution progress

### JSON Export
Machine-readable results for programmatic analysis

### SQLite Database
Persistent storage for:
- Historical trend tracking
- Regression detection
- Cost analysis over time
- SQL-based queries

```bash
# Generate dashboard from database
judge-llm dashboard --db results.db --output dashboard.html
```

## Development

```bash
# Setup
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black judge_llm && ruff check judge_llm
```

Contributions welcome! Fork, create a feature branch, add tests, and submit a PR.

## License

Licensed under **CC BY-NC-SA 4.0** - Free for non-commercial use with attribution. See [LICENSE](LICENSE) for details.

For commercial licensing, contact the maintainers.
