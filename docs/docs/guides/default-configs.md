---
sidebar_position: 7
---

# Default Configurations

Learn how to use default configuration files to define reusable settings and custom component registrations.

## Overview

Default configuration files allow you to:
- Define common settings once, use everywhere
- Register custom components globally
- Reduce duplication across test configs
- Maintain consistent configuration across projects
- Share team-wide defaults

## Configuration Hierarchy

Judge LLM merges configuration from three sources (in order of precedence):

1. **Global defaults** (`~/.judge_llm/defaults.yaml`) - User-wide settings
2. **Project defaults** (`.judge_llm.defaults.yaml`) - Project-specific settings
3. **Test config** (`test.yaml`) - Test-specific settings

Values in later files override earlier ones.

## Quick Start

### 1. Create Default Config

Create `.judge_llm.defaults.yaml` in your project root:

```yaml
# .judge_llm.defaults.yaml
providers:
  - type: gemini
    model: gemini-2.0-flash-exp
    temperature: 0.0

evaluators:
  - type: response_evaluator
    llm_provider: gemini
  - type: cost_evaluator
    max_cost: 0.05

reporters:
  - type: console
```

### 2. Create Simple Test Config

Your test configs become much simpler:

```yaml
# test.yaml
dataset:
  loader: local_file
  paths:
    - ./tests.json

providers:
  - agent_id: my_test  # Other settings from defaults
```

### 3. Run Evaluation

```bash
judge-llm run --config test.yaml
```

The configuration is merged automatically!

## Project Defaults

Place `.judge_llm.defaults.yaml` in your project root.

### Basic Defaults

```yaml
# .judge_llm.defaults.yaml

# Default provider settings
providers:
  - type: gemini
    model: gemini-2.0-flash-exp
    temperature: 0.0
    max_tokens: 1024

# Default evaluators
evaluators:
  - type: response_evaluator
    llm_provider: gemini
  - type: cost_evaluator
    max_cost: 0.05
  - type: latency_evaluator
    max_latency: 5.0

# Default reporters
reporters:
  - type: console
  - type: json
    output_path: ./results/latest.json
```

### Using Defaults in Tests

```yaml
# test.yaml
dataset:
  loader: local_file
  paths: [./tests.json]

providers:
  - agent_id: test_agent  # Inherits type, model, temperature from defaults
```

Merged result:

```yaml
dataset:
  loader: local_file
  paths: [./tests.json]

providers:
  - type: gemini              # From defaults
    model: gemini-2.0-flash-exp  # From defaults
    temperature: 0.0          # From defaults
    max_tokens: 1024          # From defaults
    agent_id: test_agent      # From test config

evaluators:                   # From defaults
  - type: response_evaluator
    llm_provider: gemini
  - type: cost_evaluator
    max_cost: 0.05
  - type: latency_evaluator
    max_latency: 5.0

reporters:                    # From defaults
  - type: console
  - type: json
    output_path: ./results/latest.json
```

## Global Defaults

Place `defaults.yaml` in `~/.judge_llm/` for user-wide settings.

### Setup

```bash
mkdir -p ~/.judge_llm
vim ~/.judge_llm/defaults.yaml
```

### Example Global Defaults

```yaml
# ~/.judge_llm/defaults.yaml

# API keys (if not using .env)
providers:
  - type: gemini
    api_key: ${GEMINI_API_KEY}
    temperature: 0.0
  - type: openai
    api_key: ${OPENAI_API_KEY}
    temperature: 0.0
  - type: anthropic
    api_key: ${ANTHROPIC_API_KEY}
    temperature: 0.0

# Always use console output
reporters:
  - type: console
```

## Overriding Defaults

Test configs can override any default value.

### Override Provider Model

```yaml
# .judge_llm.defaults.yaml
providers:
  - type: gemini
    model: gemini-2.0-flash-exp
    temperature: 0.0
```

```yaml
# test.yaml
providers:
  - agent_id: test
    model: gemini-pro  # Override default model
```

### Override Evaluators

```yaml
# .judge_llm.defaults.yaml
evaluators:
  - type: cost_evaluator
    max_cost: 0.05
```

```yaml
# test.yaml
evaluators:
  - type: cost_evaluator
    max_cost: 0.01  # Stricter cost limit for this test
```

### Add to Defaults

```yaml
# .judge_llm.defaults.yaml
reporters:
  - type: console
```

```yaml
# test.yaml
reporters:
  - type: console
  - type: html  # Add HTML reporter to defaults
    output_path: ./report.html
```

## Custom Component Registration

Register custom components in defaults to use them by name across all tests.

### Registering Custom Providers

```yaml
# .judge_llm.defaults.yaml
providers:
  - type: custom
    module_path: ./providers/my_provider.py
    class_name: MyCustomProvider
    register_as: my_provider  # ← Register globally
```

Use by name:

```yaml
# test.yaml
providers:
  - type: my_provider  # ← Use by name
    agent_id: test
```

### Registering Custom Evaluators

```yaml
# .judge_llm.defaults.yaml
evaluators:
  - type: custom
    module_path: ./evaluators/safety.py
    class_name: SafetyEvaluator
    register_as: safety
```

Use by name:

```yaml
# test.yaml
evaluators:
  - type: safety
  - type: response_evaluator
```

### Registering Custom Reporters

```yaml
# .judge_llm.defaults.yaml
reporters:
  - type: custom
    module_path: ./reporters/slack.py
    class_name: SlackReporter
    register_as: slack
```

Use by name:

```yaml
# test.yaml
reporters:
  - type: slack
    webhook_url: ${SLACK_WEBHOOK_URL}
```

### Complete Registration Example

```yaml
# .judge_llm.defaults.yaml

# Register custom provider
providers:
  - type: custom
    module_path: ./providers/custom_provider.py
    class_name: CustomProvider
    register_as: custom_provider

# Register custom evaluator
evaluators:
  - type: custom
    module_path: ./evaluators/safety.py
    class_name: SafetyEvaluator
    register_as: safety
  
  - type: custom
    module_path: ./evaluators/tone.py
    class_name: ToneEvaluator
    register_as: tone

# Register custom reporter
reporters:
  - type: custom
    module_path: ./reporters/csv_reporter.py
    class_name: CSVReporter
    register_as: csv
  
  - type: custom
    module_path: ./reporters/slack_reporter.py
    class_name: SlackReporter
    register_as: slack
```

Use everywhere:

```yaml
# test.yaml
dataset:
  loader: local_file
  paths: [./tests.json]

providers:
  - type: custom_provider  # Registered name
    agent_id: test

evaluators:
  - type: safety  # Registered name
  - type: tone    # Registered name

reporters:
  - type: csv     # Registered name
    output_path: ./results.csv
  - type: slack   # Registered name
    webhook_url: ${SLACK_WEBHOOK_URL}
```

## Environment-Specific Defaults

### Development Defaults

```yaml
# .judge_llm.defaults.yaml (development)
providers:
  - type: gemini
    model: gemini-2.0-flash-exp
    temperature: 0.0

evaluators:
  - type: response_evaluator
  - type: cost_evaluator
    max_cost: 0.1  # More lenient for dev

reporters:
  - type: console
```

### Production Defaults

```yaml
# .judge_llm.defaults.yaml (production)
providers:
  - type: gemini
    model: gemini-2.0-flash-exp
    temperature: 0.0

evaluators:
  - type: response_evaluator
  - type: trajectory_evaluator
  - type: cost_evaluator
    max_cost: 0.01  # Stricter for prod
  - type: latency_evaluator
    max_latency: 3.0

reporters:
  - type: console
  - type: database
    db_path: ./prod_results.db
  - type: json
    output_path: ./results/prod-${date}.json
```

### Managing Multiple Environments

```bash
# Use different default files
cp .judge_llm.defaults.dev.yaml .judge_llm.defaults.yaml
judge-llm run --config test.yaml

cp .judge_llm.defaults.prod.yaml .judge_llm.defaults.yaml
judge-llm run --config test.yaml
```

Or use environment variable:

```bash
# Set environment
export JUDGE_LLM_ENV=production

# Load environment-specific defaults in Python
import os
from pathlib import Path

env = os.getenv('JUDGE_LLM_ENV', 'development')
defaults_file = f'.judge_llm.defaults.{env}.yaml'

# Your evaluation code...
```

## Best Practices

### 1. Keep Defaults Generic

```yaml
# Good - Generic defaults
providers:
  - type: gemini
    model: gemini-2.0-flash-exp
    temperature: 0.0

# Bad - Test-specific in defaults
providers:
  - type: gemini
    agent_id: specific_test_agent  # Too specific
```

### 2. Use Test Configs for Specifics

```yaml
# .judge_llm.defaults.yaml - Generic
providers:
  - type: gemini
    model: gemini-2.0-flash-exp

# test.yaml - Specific
providers:
  - agent_id: math_test_agent
  - agent_id: language_test_agent
```

### 3. Document Your Defaults

```yaml
# .judge_llm.defaults.yaml

# Default provider configuration
# Uses Gemini Flash for cost efficiency
providers:
  - type: gemini
    model: gemini-2.0-flash-exp
    temperature: 0.0  # Deterministic for testing

# Standard evaluation criteria
evaluators:
  - type: response_evaluator
  - type: cost_evaluator
    max_cost: 0.05  # Maximum $0.05 per test case

# Always output to console for immediate feedback
reporters:
  - type: console
```

### 4. Version Control Defaults

```bash
git add .judge_llm.defaults.yaml
git commit -m "Add project defaults"
```

### 5. Separate Custom Components

```
project/
├── .judge_llm.defaults.yaml  # References custom components
├── providers/
│   └── custom_provider.py
├── evaluators/
│   ├── safety.py
│   └── tone.py
└── reporters/
    ├── csv_reporter.py
    └── slack_reporter.py
```

## Common Patterns

### Shared Team Defaults

```yaml
# .judge_llm.defaults.yaml (checked into git)

# Team-wide provider settings
providers:
  - type: gemini
    model: gemini-2.0-flash-exp
    temperature: 0.0
    api_key: ${GEMINI_API_KEY}  # Each dev sets their own

# Consistent evaluation criteria
evaluators:
  - type: response_evaluator
  - type: cost_evaluator
    max_cost: 0.05

# Standard reporting
reporters:
  - type: console
  - type: database
    db_path: ${DB_PATH:-./results.db}
```

### Personal Global Defaults

```yaml
# ~/.judge_llm/defaults.yaml (personal machine)

# Personal API keys
providers:
  - type: gemini
    api_key: ${GEMINI_API_KEY}
  - type: openai
    api_key: ${OPENAI_API_KEY}

# Always include console output
reporters:
  - type: console
```

### CI/CD Defaults

```yaml
# .judge_llm.defaults.yaml (for CI/CD)

providers:
  - type: gemini
    model: gemini-2.0-flash-exp
    temperature: 0.0
    api_key: ${GEMINI_API_KEY}  # From CI secrets

evaluators:
  - type: response_evaluator
  - type: cost_evaluator
    max_cost: 0.01
  - type: latency_evaluator
    max_latency: 5.0

reporters:
  - type: console
  - type: json
    output_path: ./ci_results.json
  - type: html
    output_path: ./ci_report.html
```

## Troubleshooting

### Defaults Not Loading

**Issue:** Defaults file exists but not being applied

**Solutions:**
1. Check filename: `.judge_llm.defaults.yaml` (note the leading dot)
2. Verify file location (project root or `~/.judge_llm/`)
3. Check YAML syntax: `yamllint .judge_llm.defaults.yaml`

### Unexpected Values

**Issue:** Getting unexpected configuration values

**Solution:** Remember precedence order:
1. Global defaults (lowest precedence)
2. Project defaults
3. Test config (highest precedence)

Check each file to see where value is defined.

### Custom Component Not Found

**Issue:** `Module not found: ./providers/custom.py`

**Solutions:**
1. Verify `module_path` is correct relative to project root
2. Ensure file exists: `ls ./providers/custom.py`
3. Check Python path if using absolute imports

### Registration Not Working

**Issue:** Custom component not available by registered name

**Solutions:**
1. Ensure `register_as` field is present
2. Check registration happens in defaults file
3. Verify component registration before use

## Related Documentation

- [Configuration Guide](./configuration.md)
- [Environment Variables](./environment-variables.md)
- [Custom Evaluators](../evaluators/custom-evaluators.md)
- [Custom Reporters](../reporters/custom-reporters.md)
- [Examples](../examples.md)
