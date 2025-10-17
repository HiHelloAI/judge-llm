# Default Configuration System

Judge LLM supports a default configuration system that allows you to define common settings once and reuse them across multiple test configurations.

## Overview

Instead of repeating the same providers, evaluators, and reporters in every test config, you can:
1. Define them once in a defaults file
2. Keep test configs minimal (only specify what's unique)
3. Override defaults when needed

## Benefits

- **Less repetition**: Define common settings once
- **Easier maintenance**: Change defaults in one place
- **Cleaner test configs**: Only specify what's different
- **Flexible overrides**: Merge, append, or replace defaults as needed
- **Environment-aware**: Different defaults per project or user

## Default File Locations

Judge LLM searches for defaults in this order:

1. **Custom path** (if specified via `--defaults` or `defaults` parameter)
2. **Environment variable**: `$JUDGE_LLM_DEFAULTS`
3. **Project directory**: `./.judge_llm.defaults.yaml`
4. **User home**: `~/.judge_llm/defaults.yaml`

The first file found is used. If no defaults file is found, the framework continues without defaults.

## Basic Example

### Default Configuration

Create `.judge_llm.defaults.yaml` in your project root:

```yaml
agent:
  log_level: INFO
  num_runs: 1
  parallel_execution: false
  max_workers: 4

providers:
  - type: mock
    agent_id: default_agent
    model: mock-model-v1

evaluators:
  - type: response_validator
    enabled: true
    config:
      similarity_threshold: 0.8

  - type: cost_evaluator
    enabled: true
    config:
      max_cost_per_case: 0.10

reporters:
  - type: console
```

### Test Configuration (Minimal!)

Create `config.yaml` for your test:

```yaml
# Only specify what's unique to this test
dataset:
  loader: local_file
  paths:
    - ./my-test.evalset.json

# Override agent_id from default provider
providers:
  - agent_id: my_test_agent
```

That's it! The test will automatically use:
- Default agent settings (log_level, num_runs, etc.)
- Default provider (mock) with custom agent_id
- Default evaluators (response_validator, cost_evaluator)
- Default reporter (console)

## Merge Strategies

### Agent Settings (Dictionary Merge)

Test config values override defaults:

```yaml
# Defaults
agent:
  log_level: INFO
  num_runs: 1
  parallel_execution: false

# Test config
agent:
  num_runs: 3
  parallel_execution: true

# Result: log_level stays INFO, others are overridden
agent:
  log_level: INFO        # From defaults
  num_runs: 3            # Overridden
  parallel_execution: true  # Overridden
```

### Providers (Index Merge)

Providers merge by index (first with first, second with second, etc.):

```yaml
# Defaults
providers:
  - type: mock
    agent_id: default
    model: mock-v1

# Test config (merges with first default provider)
providers:
  - agent_id: custom_agent
    temperature: 0.9

# Result
providers:
  - type: mock           # From defaults
    agent_id: custom_agent  # Overridden
    model: mock-v1       # From defaults
    temperature: 0.9     # Added
```

To replace all default providers:

```yaml
providers:
  _merge_mode: replace
  - type: gemini
    agent_id: new_agent
```

### Evaluators (Type-Based Merge)

Evaluators merge by type. You can:

**Disable specific evaluators:**

```yaml
evaluators:
  - type: cost_evaluator
    enabled: false  # Disables this evaluator
```

**Override specific evaluator config:**

```yaml
evaluators:
  - type: response_validator
    config:
      similarity_threshold: 0.9  # Override threshold
```

**Disable all defaults:**

```yaml
evaluators: []  # Empty list = no evaluators
```

**Replace all defaults:**

```yaml
evaluators:
  _merge_mode: replace
  - type: custom
    module_path: ./my_eval.py
    class_name: MyEvaluator
```

**Add to defaults:**

```yaml
evaluators:
  _merge_mode: append
  - type: custom
    module_path: ./extra_eval.py
    class_name: ExtraEvaluator
```

### Reporters (Replace by Default)

By default, test config reporters replace default reporters:

```yaml
# Defaults
reporters:
  - type: console

# Test config (replaces defaults)
reporters:
  - type: html
    output_path: ./report.html

# Result: only HTML reporter (console is gone)
```

To append instead:

```yaml
reporters:
  _merge_mode: append
  - type: html
    output_path: ./report.html

# Result: both console (from defaults) and HTML
```

### Dataset (Required in Test Config)

The `dataset` section is always required in your test config and is never merged from defaults.

## Usage Examples

### 1. Using Default Config

```python
from judge_llm import evaluate

# Uses defaults automatically
report = evaluate(config="config.yaml")
```

### 2. Skipping Defaults

```python
# Don't use defaults
report = evaluate(config="config.yaml", use_defaults=False)
```

```bash
# CLI
judge-llm run --config config.yaml --no-defaults
```

### 3. Custom Defaults File

```python
# Use specific defaults file
report = evaluate(
    config="config.yaml",
    defaults="./my-custom-defaults.yaml"
)
```

```bash
# CLI
judge-llm run --config config.yaml --defaults ./my-defaults.yaml
```

### 4. Environment Variable

```bash
export JUDGE_LLM_DEFAULTS=/path/to/defaults.yaml
judge-llm run --config config.yaml
```

### 5. Defaults Path in Config

```yaml
# config.yaml
defaults: /path/to/custom/defaults.yaml

dataset:
  loader: local_file
  paths: [./data.json]
```

## Best Practices

### 1. Project Defaults

Create `.judge_llm.defaults.yaml` in your project root for team-wide defaults:

```yaml
# .judge_llm.defaults.yaml
agent:
  log_level: INFO
  parallel_execution: true
  max_workers: 8

providers:
  - type: gemini
    model: gemini-2.0-flash
    temperature: 0.7

evaluators:
  - type: response_validator
    config: {similarity_threshold: 0.85}
  - type: trajectory_validator
    config: {sequence_match_type: exact}
  - type: cost_evaluator
    config: {max_cost_per_case: 0.05}
```

### 2. User Defaults

Create `~/.judge_llm/defaults.yaml` for personal preferences:

```yaml
# ~/.judge_llm/defaults.yaml
agent:
  log_level: DEBUG  # I like more logging

reporters:
  - type: console
  - type: html
    output_path: ~/judge_llm_reports/report.html
```

### 3. Environment-Specific Defaults

```bash
# Development
export JUDGE_LLM_DEFAULTS=./defaults-dev.yaml

# Production
export JUDGE_LLM_DEFAULTS=./defaults-prod.yaml
```

### 4. Test Suites

Structure for test suites:

```
project/
├── .judge_llm.defaults.yaml  # Common defaults
├── tests/
│   ├── smoke/
│   │   └── config.yaml        # Minimal, uses defaults
│   ├── integration/
│   │   └── config.yaml        # Override num_runs
│   └── performance/
│       └── config.yaml        # Override evaluators
```

## Migration Guide

### Before (Repetitive)

```yaml
# test1/config.yaml
agent: {log_level: INFO, num_runs: 1}
providers: [{type: mock, agent_id: test1, model: mock-v1}]
evaluators: [{type: response_validator, config: {...}}]
reporters: [{type: console}]
dataset: {loader: local_file, paths: [./test1.json]}

# test2/config.yaml
agent: {log_level: INFO, num_runs: 1}  # Same as test1
providers: [{type: mock, agent_id: test2, model: mock-v1}]  # Almost same
evaluators: [{type: response_validator, config: {...}}]  # Same
reporters: [{type: console}]  # Same
dataset: {loader: local_file, paths: [./test2.json]}
```

### After (Clean)

```yaml
# .judge_llm.defaults.yaml (once)
agent: {log_level: INFO, num_runs: 1}
providers: [{type: mock, model: mock-v1}]
evaluators: [{type: response_validator, config: {...}}]
reporters: [{type: console}]

# test1/config.yaml (minimal)
dataset: {loader: local_file, paths: [./test1.json]}
providers: [{agent_id: test1}]

# test2/config.yaml (minimal)
dataset: {loader: local_file, paths: [./test2.json]}
providers: [{agent_id: test2}]
```

## Troubleshooting

### Check if Defaults are Loaded

Enable debug logging to see which defaults file is used:

```bash
judge-llm run --config config.yaml --log-level DEBUG
```

Look for: `Loading default configuration from ...`

### Validate Merged Configuration

The merged configuration is validated before execution. Any errors will be reported clearly.

### Test Without Defaults

To test if an issue is related to defaults:

```bash
judge-llm run --config config.yaml --no-defaults
```

## Special Keys

- `_merge_mode: append` - Add to defaults instead of replacing
- `_merge_mode: replace` - Replace all defaults (explicit)
- `enabled: false` - Disable a specific evaluator from defaults
- `defaults: /path/to/file` - Specify defaults path in config

## Example Scenarios

### Scenario 1: Different Providers, Same Evaluators

```yaml
# .judge_llm.defaults.yaml
evaluators:
  - type: response_validator
    config: {similarity_threshold: 0.8}
  - type: trajectory_validator
    config: {sequence_match_type: exact}

# gemini-test/config.yaml
dataset: {loader: local_file, paths: [./data.json]}
providers: [{type: gemini, agent_id: gemini_agent}]

# openai-test/config.yaml
dataset: {loader: local_file, paths: [./data.json]}
providers: [{type: openai, agent_id: openai_agent}]

# Both use the same evaluators from defaults!
```

### Scenario 2: Same Provider, Different Thresholds

```yaml
# .judge_llm.defaults.yaml
providers: [{type: mock, agent_id: default}]
evaluators:
  - type: cost_evaluator
    config: {max_cost_per_case: 0.10}

# strict-test/config.yaml
dataset: {loader: local_file, paths: [./data.json]}
evaluators:
  - type: cost_evaluator
    config: {max_cost_per_case: 0.01}  # Stricter

# lenient-test/config.yaml
dataset: {loader: local_file, paths: [./data.json]}
evaluators:
  - type: cost_evaluator
    config: {max_cost_per_case: 1.00}  # More lenient
```

### Scenario 3: Custom Evaluators with Defaults

```yaml
# .judge_llm.defaults.yaml
evaluators:
  - type: response_validator
    config: {similarity_threshold: 0.8}

# custom-test/config.yaml
dataset: {loader: local_file, paths: [./data.json]}
evaluators:
  _merge_mode: append  # Keep defaults and add custom
  - type: custom
    module_path: ./my_evaluator.py
    class_name: MyEvaluator

# Result: response_validator (from defaults) + MyEvaluator
```

## Summary

The default configuration system makes Judge LLM more maintainable and user-friendly by:

- Reducing config duplication
- Making test configs cleaner and more focused
- Providing flexible override mechanisms
- Supporting multiple levels of defaults (user, project, custom)
- Maintaining backward compatibility (works without defaults)

Start using defaults today to simplify your evaluation workflows!
