<div align="center">
  <img src="assets/icon.png" alt="Judge LLM" width="200"/>

  # JUDGE LLM

  A lightweight, extensible Python framework for **evaluating and comparing LLM providers**. Test your AI agents systematically with multi-turn conversations, cost tracking, and comprehensive reporting.

  [Quick Start](#quick-start) • [Features](#features) • [Examples](#testing-examples) • [Reports](#reports--dashboard)
</div>

<div align="center">
  <img src="assets/judge-llm.gif" alt="Judge LLM Demo" width="100%"/>
</div>

## Purpose

JUDGE LLM helps you **evaluate AI agents and LLM providers** by running test cases against your models and measuring:
- **Response quality** (exact matching, semantic similarity, ROUGE scores)
- **Cost & latency** (token usage, execution time, budget compliance)
- **Conversation flow** (tool uses, multi-turn interactions)
- **Safety & custom metrics** (extensible evaluation logic)

Perfect for regression testing, A/B testing providers, and ensuring production-grade quality.

## Features

- **Multiple Providers**: Gemini, Google ADK, Mock, and custom providers with registry-based extensibility
- **Built-in Evaluators**: Response similarity, trajectory validation, cost/latency checks
- **Custom Components**: Create and register custom providers, evaluators, and reporters
- **Registry System**: Register once in defaults, use everywhere by name
- **Rich Reports**: Console tables, interactive HTML dashboard, JSON exports, SQLite database, plus custom reporters
- **Parallel Execution**: Run evaluations concurrently with configurable workers
- **Quality Gates**: Fail CI/CD builds when thresholds are violated (configurable)
- **Config-Driven**: YAML configs with smart defaults or programmatic Python API
- **Default Config**: Reusable configurations with component registration
- **Per-Test Overrides**: Fine-tune evaluator thresholds per test case
- **Environment Variables**: Auto-loads `.env` for secure API key management

## Installation

### From Source

```bash
git clone https://github.com/HiHelloAI/judge-llm.git
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

# Install with Google ADK provider support
pip install judge-llm[google_adk]

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

# Run with inline arguments (supports .json, .yaml, or .yml)
judge-llm run --dataset ./data/eval.yaml --provider mock --agent-id my_agent --report html --output report.html

# Validate configuration
judge-llm validate --config config.yaml

# List available components
judge-llm list providers
judge-llm list evaluators
judge-llm list reporters

# Generate dashboard from database
judge-llm dashboard --db results.db --output dashboard.html
```

### Python API

```python
from judge_llm import evaluate

# From config file
report = evaluate(config="config.yaml")

# Programmatic API (supports .json, .yaml, or .yml datasets)
report = evaluate(
    dataset={"loader": "local_file", "paths": ["./data/eval.yaml"]},
    providers=[{"type": "mock", "agent_id": "my_agent"}],
    evaluators=[{"type": "response_evaluator", "config": {"similarity_threshold": 0.8}}],
    reporters=[{"type": "console"}, {"type": "html", "output_path": "./report.html"}]
)

print(f"Success: {report.success_rate:.1%} | Cost: ${report.total_cost:.4f}")
```

## Configuration

**Minimal config.yaml:**
```yaml
dataset:
  loader: local_file
  paths: [./data/eval.json]  # Supports .json, .yaml, or .yml files

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

**Advanced config with quality gates:**
```yaml
agent:
  fail_on_threshold_violation: true  # Exit with error if evaluations fail (default: true)
  parallel_execution: true            # Run tests in parallel
  max_workers: 4                      # Number of parallel workers
  num_runs: 3                         # Run each test 3 times

dataset:
  loader: local_file
  paths: [./data/eval.yaml]

providers:
  - type: gemini
    agent_id: production_agent
    model: gemini-2.0-flash-exp

evaluators:
  - type: response_evaluator
    config:
      similarity_threshold: 0.85  # Minimum 85% similarity required
  - type: cost_evaluator
    config:
      max_cost_per_case: 0.05      # Maximum $0.05 per test

reporters:
  - type: database
    db_path: ./results.db  # Track results over time
```

**Use in CI/CD:**
```bash
# Fails with exit code 1 if any evaluator thresholds are violated
judge-llm run --config ci-config.yaml

# Or disable failures for monitoring
# Set fail_on_threshold_violation: false in config
```

**Dataset File Formats:**

JUDGE LLM supports both JSON and YAML formats for evaluation datasets. Use whichever format you prefer:

```yaml
# Using JSON dataset
dataset:
  loader: local_file
  paths: [./data/eval.json]

# Using YAML dataset
dataset:
  loader: local_file
  paths: [./data/eval.yaml]

# Using multiple datasets (mixed formats)
dataset:
  loader: local_file
  paths:
    - ./data/eval1.json
    - ./data/eval2.yaml

# Using directory loader with pattern
dataset:
  loader: directory
  paths: [./data]
  pattern: "*.yaml"  # or "*.json" or "*.yml"
```

**Google ADK Provider Configuration:**

For agents built with Google's Agent Development Kit (ADK):

```yaml
providers:
  - type: google_adk
    agent_id: my_adk_agent
    agent_metadata:
      module_path: "tool_agent.agent"  # Path to your agent module
      agent_name: "root_agent"         # Agent variable name (default: "root_agent")
      root_path: "."                   # Root path for imports (optional)
```

The ADK provider automatically:
- Loads your ADK agent from the specified module
- Converts between Judge LLM and ADK formats
- Validates tool usage and conversation flow
- Reports results in standard Judge LLM format

See [examples/09-google-adk-agent/](examples/09-google-adk-agent/) for a complete working example.

See the [examples/](examples/) directory for complete configuration examples including default configs, custom evaluators, and advanced features.

## Custom Component Registration

JUDGE LLM supports registering custom providers, evaluators, and reporters for reuse across projects.

### Method 1: Register in Default Config

Create `.judge_llm.defaults.yaml` in your project root:

```yaml
# Register custom components once
providers:
  - type: custom
    module_path: ./my_providers/anthropic.py
    class_name: AnthropicProvider
    register_as: anthropic  # ← Use this name in test configs

evaluators:
  - type: custom
    module_path: ./my_evaluators/safety.py
    class_name: SafetyEvaluator
    register_as: safety

reporters:
  - type: custom
    module_path: ./my_reporters/slack.py
    class_name: SlackReporter
    register_as: slack
```

Then use them by name in any test config:

```yaml
# test.yaml - clean and simple!
providers:
  - type: anthropic  # ← Uses registered custom provider
    agent_id: claude

evaluators:
  - type: safety  # ← Uses registered custom evaluator

reporters:
  - type: slack  # ← Uses registered custom reporter
    config: {webhook_url: ${SLACK_WEBHOOK}}
```

### Method 2: Programmatic Registration

```python
from judge_llm import evaluate, register_provider, register_evaluator, register_reporter
from my_components import CustomProvider, SafetyEvaluator, SlackReporter

# Register components
register_provider("my_provider", CustomProvider)
register_evaluator("safety", SafetyEvaluator)
register_reporter("slack", SlackReporter)

# Use by name
report = evaluate(
    dataset={"loader": "local_file", "paths": ["./tests.json"]},
    providers=[{"type": "my_provider", "agent_id": "test"}],
    evaluators=[{"type": "safety"}],
    reporters=[{"type": "slack", "config": {"webhook_url": "..."}}]
)
```

**Benefits:**
- ✅ **DRY** - Register once, use everywhere
- ✅ **Team Standardization** - Share defaults across team
- ✅ **Clean Configs** - Test configs reference components by name
- ✅ **Easy Updates** - Change implementation in one place

See [examples/default_config_reporters/](examples/default_config_reporters/) for complete examples.

## Testing Examples

Explore **9 complete examples** in the `examples/` directory, from basic setup to advanced features:

| Example | Description | Key Features |
|---------|-------------|--------------|
| **[01-gemini-agent](examples/01-gemini-agent/)** | Basic Gemini agent evaluation | Simple setup, response evaluation, CLI & Python API usage |
| **[02-default-config](examples/02-default-config/)** | Using default configuration files | Config merging, `.judge_llm.defaults.yaml`, reducing duplication |
| **[03-custom-evaluator](examples/03-custom-evaluator/)** | Creating custom evaluators | Extending `BaseEvaluator`, custom validation logic, registration |
| **[04-safety-long-conversation](examples/04-safety-long-conversation/)** | Multi-turn safety evaluation | Long conversations, PII detection, toxicity analysis, LLM-as-judge |
| **[05-evaluator-config-override](examples/05-evaluator-config-override/)** | Per-test-case evaluator overrides | Fine-grained threshold control, two-level configuration |
| **[06-database-reporter](examples/06-database-reporter/)** | SQLite database reporter | Historical tracking, trend analysis, SQL queries, cost monitoring |
| **[07-custom-reporter](examples/07-custom-reporter/)** | Creating custom reporters | CSV reporter example, config-based & programmatic registration |
| **[08-default-config-reporters](examples/08-default-config-reporters/)** | Registering custom components | Register providers, evaluators, and reporters in defaults |
| **[09-google-adk-agent](examples/09-google-adk-agent/)** | Google ADK agent evaluation | ADK integration, tool usage validation, agent module loading |

### Running Examples

Each example includes configuration files, datasets, and detailed instructions:

```bash
# Navigate to any example
cd examples/01-gemini-agent

# Run via CLI
judge-llm run --config config.yaml

# Or run via Python script
python run_evaluation.py

# Or use the convenience shell script
./run.sh
```

### Example Categories

**Getting Started:**
- Start with **01-gemini-agent** for basic usage
- Use **02-default-config** to learn configuration best practices

**Customization:**
- **03-custom-evaluator** - Build domain-specific evaluation logic
- **07-custom-reporter** - Create custom output formats
- **08-default-config-reporters** - Organize custom components

**Advanced Features:**
- **04-safety-long-conversation** - Production-ready safety evaluation with LLM-as-judge
- **05-evaluator-config-override** - Fine-tune evaluations per test case
- **06-database-reporter** - Track metrics over time with SQL queries
- **09-google-adk-agent** - Evaluate Google ADK agents seamlessly

## Built-in Components

### Providers
- **Gemini** - Google's Gemini models (requires `GOOGLE_API_KEY` in `.env`)
- **Google ADK** - Google's Agent Development Kit for agentic workflows (requires `google-adk` package)
- **Mock** - Built-in test provider, no setup required
- **Custom** - Extend `BaseProvider` for your own LLM providers (OpenAI, Anthropic, etc.)

### Evaluators
- **ResponseEvaluator** - Compare responses (exact, semantic similarity, ROUGE)
- **TrajectoryEvaluator** - Validate tool uses and conversation flow
- **CostEvaluator** - Enforce cost thresholds
- **LatencyEvaluator** - Enforce latency thresholds
- **Custom** - Extend `BaseEvaluator` for custom logic (safety, compliance, etc.)

### Reporters
- **ConsoleReporter** - Rich terminal output with colored tables
- **HTMLReporter** - Interactive HTML dashboard
- **JSONReporter** - Machine-readable JSON export
- **DatabaseReporter** - SQLite database for historical tracking
- **Custom** - Extend `BaseReporter` for custom formats (CSV, Slack, Datadog, etc.)

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
