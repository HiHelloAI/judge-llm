# Judge LLM

A lightweight, extensible Python framework for evaluating and comparing LLM providers.

## Features

- 🚀 **Multiple LLM Providers**: Support for Gemini, OpenAI, Claude, and custom providers
- 📊 **Built-in Evaluators**: Response validation, trajectory checking, cost and latency evaluation
- 🔌 **Extensible**: Easy plugin system for custom evaluators and providers
- 📈 **Multiple Report Formats**: Console, HTML dashboard, and JSON outputs
- ⚡ **Parallel Execution**: Run evaluations concurrently for faster results
- 🎯 **Threshold-Based**: Configure pass/fail thresholds for all metrics
- 🛠️ **Configuration Driven**: YAML config files or programmatic API
- 📝 **Comprehensive Logging**: Configurable log levels for debugging
- ✅ **Config Validation**: Pre-execution validation with clear error messages

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
# Install with specific provider support
pip install judge-llm[gemini]
pip install judge-llm[openai]
pip install judge-llm[anthropic]

# Install with all providers
pip install judge-llm[all]

# Install with dev dependencies
pip install judge-llm[dev]
```

## Quick Start

### 1. CLI Usage

```bash
# Run from config file
judge-llm run --config config.yaml

# Run with CLI arguments
judge-llm run \
  --dataset ./data/eval.json \
  --provider mock \
  --agent-id my_agent \
  --num-runs 3 \
  --parallel \
  --report html \
  --output ./report.html

# Validate config
judge-llm validate --config config.yaml

# List available providers and evaluators
judge-llm list providers
judge-llm list evaluators
```

### 2. Python API

```python
from judge_llm import evaluate

# Option 1: From config file
report = evaluate(config="config.yaml")

# Option 2: Programmatic configuration
report = evaluate(
    dataset_path=["./data/eval.json"],
    providers=[
        {
            "type": "mock",
            "agent_id": "my_agent",
            "model": "mock-model-v1",
        }
    ],
    evaluators=[
        {
            "type": "response_validator",
            "config": {"similarity_threshold": 0.8},
        },
    ],
    num_runs=1,
    parallel_execution=True,
    log_level="INFO",
)

print(f"Success rate: {report.success_rate:.1%}")
print(f"Total cost: ${report.total_cost:.4f}")
```

## Configuration

### Example config.yaml

```yaml
agent:
  log_level: INFO
  num_runs: 3
  parallel_execution: true
  max_workers: 4
  fail_on_threshold_violation: true
  validate_config: true  # Default, can set to false to skip

dataset:
  loader: local_file
  paths:
    - ./data/eval.json

providers:
  - type: gemini
    agent_id: my_agent
    agent_config_path: ./agents/my_agent/
    # Any additional config passed to provider
    model: gemini-2.0-flash
    temperature: 0.7
    api_key: ${GEMINI_API_KEY}

evaluators:
  # Each evaluator has its own config
  - type: response_validator
    enabled: true
    config:
      similarity_threshold: 0.8
      match_type: exact

  - type: trajectory_validator
    enabled: true
    config:
      sequence_match_type: exact

  - type: cost_evaluator
    enabled: true
    config:
      max_cost_per_case: 0.10

  - type: latency_evaluator
    enabled: true
    config:
      max_latency_seconds: 30

  # Custom evaluator
  - type: custom
    module_path: ./evaluators/my_evaluator.py
    class_name: MyEvaluator
    enabled: true
    config:
      custom_threshold: 0.7

reporters:
  - type: console
  - type: html
    output_path: ./report.html
  - type: json
    output_path: ./report.json
```

## Creating Custom Evaluators

```python
from judge_llm.evaluators.base import BaseEvaluator
from judge_llm.core.models import EvalCase, ProviderResult, EvaluatorResult

class MyCustomEvaluator(BaseEvaluator):
    def __init__(self, config=None):
        super().__init__(config)
        self.threshold = self.config.get("threshold", 0.5)

    def evaluate(self, eval_case, agent_metadata, provider_result):
        # Your evaluation logic
        score = self.calculate_score(provider_result)

        return EvaluatorResult(
            evaluator_name=self.get_evaluator_name(),
            evaluator_type=self.get_evaluator_type(),
            success=True,
            score=score,
            threshold=self.threshold,
            passed=score >= self.threshold,
            details={"info": "details here"},
        )
```

### Register Custom Evaluator

```python
from judge_llm import register_evaluator
from my_evaluators import MyCustomEvaluator

register_evaluator("my_custom", MyCustomEvaluator)

# Now use it in config or evaluate()
```

## Examples

See the `examples/` directory for complete examples:

- **quickstart/**: Basic usage with console output
- **custom-evaluator/**: Creating and using custom evaluators
- **html-report/**: Generating interactive HTML dashboards

Each example includes:
- Configuration file
- Sample dataset
- Python script
- Shell script (for CLI)
- README with detailed instructions

## Architecture

### Core Components

1. **Loaders**: Load eval sets from files, directories, or custom sources
2. **Providers**: Execute eval cases with LLM providers (Gemini, OpenAI, Claude, etc.)
3. **Evaluators**: Compare expected vs actual results using various metrics
4. **Reporters**: Generate reports in different formats (console, HTML, JSON)

### Design Principles

- **Interface-Driven**: All components implement abstract base classes
- **Singleton Pattern**: Registries, logger, and validator use singletons for efficiency
- **Pydantic Models**: Type-safe data structures throughout
- **Resource Efficient**: Connection pooling, lazy loading, streaming I/O
- **Extensible**: Plugin architecture for custom components

## Dataset Format

Judge LLM uses evaluation sets in JSON format:

```json
{
  "eval_set_id": "my_eval_set",
  "name": "My Eval Set",
  "eval_cases": [
    {
      "eval_id": "case_1",
      "conversation": [
        {
          "invocation_id": "inv_1",
          "user_content": {
            "parts": [{"text": "Hello"}],
            "role": "user"
          },
          "final_response": {
            "parts": [{"text": "Hi there!"}],
            "role": null
          },
          "intermediate_data": {
            "tool_uses": [],
            "intermediate_responses": []
          },
          "creation_timestamp": 1234567890.0
        }
      ],
      "session_input": {
        "app_name": "my_app",
        "user_id": "user",
        "state": {}
      },
      "creation_timestamp": 1234567890.0
    }
  ],
  "creation_timestamp": 1234567890.0
}
```

## Built-in Evaluators

1. **ResponseValidator**: Compare final responses (exact or semantic similarity)
2. **TrajectoryValidator**: Validate tool uses and intermediate responses
3. **CostEvaluator**: Check if cost is within threshold
4. **LatencyEvaluator**: Check if execution time is within threshold

## HTML Reports

Generate interactive HTML dashboards:

- **Left Sidebar**: Summary metrics and execution list
- **Main Panel**: Detailed view with:
  - Execution details (time, cost, tokens, status)
  - Evaluator results (pass/fail, scores, details)
  - Conversation history (expected vs actual)
- **Features**:
  - Click to explore different executions
  - Color-coded status indicators
  - Dark mode support
  - Responsive design
  - Self-contained (no external dependencies)

## Development

### Setup Development Environment

```bash
git clone https://github.com/yourusername/judge-llm.git
cd judge-llm
pip install -e ".[dev]"
```

### Run Tests

```bash
pytest
```

### Code Formatting

```bash
black judge_llm
ruff check judge_llm
```

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Roadmap

- [ ] Add more LLM provider integrations (Gemini, OpenAI, Claude)
- [ ] Add semantic similarity evaluator using embeddings
- [ ] Add support for streaming responses
- [ ] Add caching layer for provider responses
- [ ] Add CI/CD pipeline
- [ ] Add more example use cases
- [ ] Publish to PyPI

## Support

- GitHub Issues: https://github.com/yourusername/judge-llm/issues
- Documentation: https://github.com/yourusername/judge-llm#readme

## Acknowledgments

Built with:
- Pydantic for data validation
- Click for CLI interface
- Jinja2 for HTML templating
- Rich for beautiful console output
