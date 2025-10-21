---
sidebar_position: 1
---

# Examples Overview

Learn by example with comprehensive tutorials covering common Judge LLM use cases. Each example demonstrates specific features and best practices.

## Quick Navigation

| Example | Focus | Difficulty | Key Concepts |
|---------|-------|------------|--------------|
| [Gemini Agent](./gemini-agent) | Basic setup | Beginner | Configuration, providers, evaluators |
| [Default Config](./default-config) | Defaults | Beginner | Default config, config merging |
| [Custom Evaluator](./custom-evaluator) | Custom evaluator | Intermediate | Custom components, registration |
| [Safety Evaluation](./safety-evaluation) | Multi-turn | Advanced | Long conversations, safety, trajectory |
| [Config Override](./config-override) | Config override | Intermediate | Per-test config, thresholds |
| [Database Tracking](./database-tracking) | Database | Intermediate | SQLite, querying, trends |

## By Category

### Getting Started

Perfect for beginners learning Judge LLM basics:

- **[Gemini Agent](./gemini-agent)** - Start here! Basic Gemini agent evaluation
- **[Default Config](./default-config)** - Reusable defaults and configuration merging

### Custom Components

Learn to extend Judge LLM with custom implementations:

- **[Custom Evaluator](./custom-evaluator)** - Build domain-specific evaluators
- **[Safety Evaluation](./safety-evaluation)** - Multi-turn safety checks

### Advanced Configuration

Master configuration patterns and overrides:

- **[Default Config](./default-config)** - Default configuration system
- **[Config Override](./config-override)** - Per-test configuration overrides

### Data & Reporting

Store and analyze evaluation results:

- **[Database Tracking](./database-tracking)** - SQLite storage and querying

## Running Examples

### Prerequisites

All examples require:

1. **Judge LLM installed:**
```bash
pip install judge-llm
```

2. **API keys configured:**
```bash
# Create .env file
echo "GEMINI_API_KEY=your_key" > .env
echo "OPENAI_API_KEY=your_key" >> .env
```

3. **Navigate to example:**
```bash
cd examples/01-gemini-agent
```

### Running an Example

Each example can be run with:

```bash
judge-llm run --config config.yaml
```

Or using the Python API:

```bash
python run_evaluation.py
```

### Expected Output

Typical output looks like:

```
Starting evaluation...

Evaluation Progress:
  test_001: ✓ PASSED (cost: $0.0012, time: 1.2s)
  test_002: ✓ PASSED (cost: $0.0015, time: 1.5s)
  test_003: ✗ FAILED (cost: $0.0010, time: 0.8s)

Summary:
  Total Tests: 3
  Passed: 2
  Failed: 1
  Success Rate: 66.7%
  Total Cost: $0.0037
  Total Time: 3.5s
```

## Example Structure

Each example includes:

```
XX-example-name/
├── README.md              # Detailed explanation
├── config.yaml            # Configuration file
├── sample.evalset.json    # Test cases
├── run.sh                 # Shell script runner
└── run_evaluation.py      # Python API runner
```

## Common Patterns

### Basic Configuration

```yaml
dataset:
  loader: local_file
  paths: [./sample.evalset.json]

providers:
  - type: gemini
    agent_id: my_agent
    model: gemini-2.0-flash-exp

evaluators:
  - type: response_evaluator

reporters:
  - type: console
```

### Using Defaults

```yaml
# .judge_llm.defaults.yaml
providers:
  - type: gemini
    model: gemini-2.0-flash-exp
    temperature: 0.7

evaluators:
  - type: response_evaluator
  - type: cost_evaluator

# test.yaml (overrides defaults)
dataset:
  loader: local_file
  paths: [./tests.json]

providers:
  - type: gemini
    agent_id: my_agent
    # Inherits model and temperature from defaults
```

### Custom Components

```yaml
evaluators:
  - type: custom
    module_path: ./evaluators/safety.py
    class_name: SafetyEvaluator
    config:
      strict_mode: true
```

## Troubleshooting

### API Key Not Found

**Error:** `API key not found for provider: gemini`

**Solution:**
```bash
# Set environment variable
export GEMINI_API_KEY=your_key

# Or create .env file
echo "GEMINI_API_KEY=your_key" > .env
```

### Module Not Found

**Error:** `Module not found: ./evaluators/safety.py`

**Solution:** Ensure you're in the example directory:
```bash
pwd
# Should be: /path/to/examples/XX-example-name
cd examples/XX-example-name
```

### Test File Not Found

**Error:** `Test file not found: ./tests.json`

**Solution:** Check file exists and path is correct:
```bash
ls sample.evalset.json
# Or check config for correct path
cat config.yaml | grep paths
```

### Permission Denied

**Error:** `Permission denied: ./run.sh`

**Solution:** Make script executable:
```bash
chmod +x run.sh
./run.sh
```

## Modifying Examples

To experiment with an example:

1. **Copy the example:**
```bash
cp -r examples/01-gemini-agent my-experiment
cd my-experiment
```

2. **Modify configuration or tests:**
```bash
# Edit test cases
vim sample.evalset.json

# Edit configuration
vim config.yaml
```

3. **Run with changes:**
```bash
judge-llm run --config config.yaml
```

4. **Compare results:**
```bash
diff my-experiment/results.json examples/01-gemini-agent/results.json
```

## Learning Path

### Beginner

1. Start with [Gemini Agent](./gemini-agent) to understand basic setup
2. Learn [Default Config](./default-config) for reusable configurations
3. Try [Database Tracking](./database-tracking) for storing results

### Intermediate

1. Build [Custom Evaluator](./custom-evaluator) for domain-specific checks
2. Master [Config Override](./config-override) for flexible testing
3. Explore [Safety Evaluation](./safety-evaluation) for multi-turn scenarios

### Advanced

1. Combine multiple examples into a comprehensive test suite
2. Create custom providers and reporters
3. Build CI/CD pipelines with Judge LLM

## Next Steps

After completing examples:

- Read [User Guides](../guides/basic-usage) for comprehensive documentation
- Explore [Evaluators](../evaluators/overview) for evaluation options
- Learn about [Reporters](../reporters/overview) for output formats
- Check [Python API](../guides/python-api) for programmatic usage

## Contributing Examples

Want to contribute an example? Follow these steps:

1. **Create directory:**
```bash
mkdir examples/XX-your-example
```

2. **Add required files:**
- `README.md` - Description and instructions
- `config.yaml` - Configuration
- `sample.evalset.json` - Test cases
- `run.sh` - Shell runner
- `run_evaluation.py` - Python runner

3. **Document thoroughly:**
- Explain what the example demonstrates
- List key concepts and learning objectives
- Provide step-by-step instructions
- Include expected output and troubleshooting

4. **Test completely:**
```bash
cd examples/XX-your-example
judge-llm run --config config.yaml
python run_evaluation.py
```

5. **Submit pull request:**
Include the example in documentation updates

## Related Documentation

- [Quick Start](../tutorial-basics/installation)
- [Configuration Guide](../guides/configuration)
- [CLI Reference](../guides/cli-reference)
- [Python API](../guides/python-api)
- [Evalset Format](../guides/evalset-format)
