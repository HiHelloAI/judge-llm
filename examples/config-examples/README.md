# Configuration Examples

This directory demonstrates different ways to configure Judge LLM evaluations.

## Overview

Judge LLM supports two approaches for configuration:

1. **Using Defaults** - Minimal config that leverages default values
2. **Full Configuration** - Explicit configuration with all settings

## Examples

### 1. Minimal Config with Defaults (`config-with-defaults.yaml`)

This approach uses the default configuration file (`.judge_llm.defaults.yaml`) and only specifies what's different:

```yaml
# Minimal configuration - uses defaults for most settings
dataset:
  loader: json
  paths:
    - sample.evalset.json

providers:
  - type: gemini
    agent_id: news_agent
    agent_config_path: agent_config.json

evaluators:
  - type: llm_grader
    name: response_quality

reporters:
  - type: console
  - type: html
    output_path: reports/report.html
```

**Benefits:**
- ✅ Concise and easy to read
- ✅ Automatically inherits sensible defaults
- ✅ Only specify what you need to change
- ✅ Defaults can be updated centrally

**How it works:**
The system automatically merges your config with `.judge_llm.defaults.yaml`, so you inherit:
- Default log level (INFO)
- Default num_runs (1)
- Default parallel_execution (false)
- Default evaluator thresholds
- And more...

### 2. Full Configuration (`config-full.yaml`)

This approach explicitly specifies all configuration values:

```yaml
# Full configuration - all settings explicitly defined
agent:
  num_runs: 1
  parallel_execution: false
  max_workers: 4
  fail_on_threshold_violation: true
  validate_config: true
  log_level: INFO

dataset:
  loader: json
  paths:
    - sample.evalset.json

providers:
  - type: gemini
    agent_id: news_agent
    agent_config_path: agent_config.json

evaluators:
  - type: llm_grader
    name: response_quality
    threshold: 0.7
    enabled: true
    config:
      model: gemini-2.0-flash-exp
      criteria:
        - accuracy
        - completeness
        - clarity

reporters:
  - type: console
  - type: html
    output_path: reports/report.html
  - type: json
    output_path: reports/report.json
```

**Benefits:**
- ✅ Full control over all settings
- ✅ Self-documenting (all options visible)
- ✅ No hidden defaults
- ✅ Easier to understand exact behavior

### 3. Custom Defaults (`config-custom-defaults.yaml`)

You can also provide your own custom defaults file:

```python
from judge_llm import evaluate

# Use custom defaults file
result = evaluate(
    config="config.yaml",
    use_defaults=True,
    defaults="my-custom-defaults.yaml"
)
```

## When to Use Which Approach

### Use Defaults When:
- 🎯 You're getting started quickly
- 🎯 You want consistent settings across projects
- 🎯 Your config only differs slightly from defaults
- 🎯 You want cleaner, more maintainable configs

### Use Full Config When:
- 🎯 You need complete control
- 🎯 You want self-contained configurations
- 🎯 You're sharing configs with others
- 🎯 You don't want dependency on external defaults

## Running the Examples

### 1. Basic Examples

**With Defaults:**
```bash
cd examples/config-examples
python run_with_defaults.py
```

**Without Defaults (Full Config):**
```bash
cd examples/config-examples
python run_full_config.py
```

**Compare Both Approaches:**
```bash
cd examples/config-examples
python compare_configs.py
```

### 2. Understanding Config Merging

**Visualize How Configs Are Merged:**
```bash
python show_config_merging.py
```
This shows step-by-step how your config is merged with defaults.

**Visual Side-by-Side Comparison:**
```bash
python visualize_merge.py
```
This displays a color-coded table showing which values come from defaults vs your config.

**Debug Config Loading:**
```bash
python debug_config_loading.py
```
This runs evaluation with DEBUG logging to see the internal config loading process.

### 3. Programmatic Usage

**Disable Defaults Programmatically:**
```python
from judge_llm import evaluate

# Explicitly disable defaults
result = evaluate(
    config="config-full.yaml",
    use_defaults=False  # Don't merge with defaults
)
```

## Default Configuration File Location

The default configuration file is located at:
```
.judge_llm.defaults.yaml
```

You can view the default configuration to see all available options and their default values.

## Configuration Precedence

When using defaults, the merge order is:

1. **Default values** (from `.judge_llm.defaults.yaml`)
2. **Your config** (overrides defaults)
3. **Command-line arguments** (highest priority)

Example:
```yaml
# .judge_llm.defaults.yaml
agent:
  log_level: INFO
  num_runs: 1

# your-config.yaml
agent:
  log_level: DEBUG  # Overrides default INFO

# Result: log_level=DEBUG, num_runs=1 (inherited)
```

## Tips

1. **Start with defaults** for rapid development
2. **Use full config** for production/shared configs
3. **Check merged config** by enabling DEBUG logging
4. **Override selectively** - only specify what changes
5. **Document overrides** - add comments explaining why you override defaults
