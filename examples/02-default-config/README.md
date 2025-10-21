# Example 02: Using Default Configuration

This example demonstrates how to use `.judge_llm.defaults.yaml` to define reusable defaults and keep test configs simple.

## What You'll Learn

- Creating default configuration files
- Config merging behavior
- Reducing duplication across tests
- Best practices for defaults

## Files

- `.judge_llm.defaults.yaml` - Default configuration
- `config.yaml` - Simple test configuration
- `sample.evalset.json` - Test cases
- `README.md` - This file

## Prerequisites

```bash
pip install judge-llm
export GEMINI_API_KEY=your_key
```

## Configuration

### .judge_llm.defaults.yaml

```yaml
# Default provider settings
providers:
  - type: gemini
    model: gemini-2.0-flash-exp
    temperature: 0.0

# Default evaluators
evaluators:
  - type: response_evaluator
    llm_provider: gemini
  - type: cost_evaluator
    max_cost: 0.05

# Default reporters
reporters:
  - type: console
```

This file defines common settings used across all tests.

### config.yaml

```yaml
dataset:
  loader: local_file
  paths:
    - ./sample.evalset.json

providers:
  - agent_id: test_agent  # Only specify agent_id, rest from defaults
```

Much simpler! The configuration is automatically merged with defaults.

## How It Works

Judge LLM merges configuration from:

1. Global defaults (`~/.judge_llm/defaults.yaml`)
2. Project defaults (`.judge_llm.defaults.yaml`)
3. Test config (`config.yaml`)

Values in later files override earlier ones.

**Merged Result:**

```yaml
dataset:
  loader: local_file
  paths: [./sample.evalset.json]

providers:
  - type: gemini              # From defaults
    model: gemini-2.0-flash-exp  # From defaults
    temperature: 0.0          # From defaults
    agent_id: test_agent      # From test config

evaluators:                   # From defaults
  - type: response_evaluator
    llm_provider: gemini
  - type: cost_evaluator
    max_cost: 0.05

reporters:                    # From defaults
  - type: console
```

## Running the Example

```bash
cd examples/02-default-config
judge-llm run --config config.yaml
```

## Expected Output

```
Starting evaluation...

Evaluation Progress:
  test_001: ✓ PASSED (cost: $0.0012, time: 1.2s)
  test_002: ✓ PASSED (cost: $0.0015, time: 1.4s)

Summary:
  Total Tests: 2
  Passed: 2
  Failed: 0
  Success Rate: 100.0%
  Total Cost: $0.0027
  Total Time: 2.6s
```

## Benefits of Defaults

### 1. DRY (Don't Repeat Yourself)

**Without defaults:**
```yaml
# test1.yaml
providers:
  - type: gemini
    model: gemini-2.0-flash-exp
    temperature: 0.0
    agent_id: test1

# test2.yaml
providers:
  - type: gemini
    model: gemini-2.0-flash-exp
    temperature: 0.0
    agent_id: test2
```

**With defaults:**
```yaml
# test1.yaml
providers:
  - agent_id: test1

# test2.yaml
providers:
  - agent_id: test2
```

### 2. Consistency

All tests use the same model, temperature, and evaluators.

### 3. Easy Updates

Change model once in defaults, applies to all tests.

## Overriding Defaults

You can override any default value in your test config:

```yaml
# config.yaml
dataset:
  loader: local_file
  paths: [./sample.evalset.json]

providers:
  - agent_id: test_agent
    model: gemini-pro  # Override default model

evaluators:
  - type: cost_evaluator
    max_cost: 0.01  # Stricter than default
```

## Best Practices

### 1. Keep Defaults Generic

```yaml
# Good
providers:
  - type: gemini
    model: gemini-2.0-flash-exp

# Bad
providers:
  - type: gemini
    agent_id: specific_test  # Too specific
```

### 2. Document Your Defaults

```yaml
# .judge_llm.defaults.yaml

# Default provider: Gemini Flash for cost efficiency
providers:
  - type: gemini
    model: gemini-2.0-flash-exp
    temperature: 0.0  # Deterministic

# Standard evaluation criteria
evaluators:
  - type: response_evaluator
  - type: cost_evaluator
    max_cost: 0.05  # Max $0.05 per test
```

### 3. Version Control Defaults

```bash
git add .judge_llm.defaults.yaml
git commit -m "Add project defaults"
```

## Next Steps

- Try modifying defaults
- Create multiple test configs using same defaults
- Experiment with overriding specific values
- Set up global defaults in `~/.judge_llm/defaults.yaml`

## Related Examples

- [05-evaluator-config-override](../05-evaluator-config-override/) - Overriding evaluator configs
- [default_config_reporters](../default_config_reporters/) - Registering custom components

## Related Documentation

- [Default Configurations Guide](../../docs/docs/guides/default-configs.md)
- [Configuration Guide](../../docs/docs/guides/configuration.md)
