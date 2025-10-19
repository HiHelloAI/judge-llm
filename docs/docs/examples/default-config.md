---
sidebar_position: 3
---

# Default Configuration

Learn how to use `.judge_llm.defaults.yaml` to define reusable defaults and keep your test configurations simple and maintainable.

## Overview

**Location:** `examples/02-default-config/`

**Difficulty:** Beginner

**What You'll Learn:**
- Creating default configuration files
- Configuration merging behavior
- Reducing duplication across multiple tests
- Overriding defaults selectively
- Best practices for maintaining defaults

## Why Use Defaults?

### Problem: Repetitive Configuration

Without defaults, every test needs full configuration:

```yaml
# test1.yaml
providers:
  - type: gemini
    model: gemini-2.0-flash-exp
    temperature: 0.0
    agent_id: test1

evaluators:
  - type: response_evaluator
  - type: cost_evaluator
    max_cost: 0.05

reporters:
  - type: console

# test2.yaml (same configuration repeated)
providers:
  - type: gemini
    model: gemini-2.0-flash-exp
    temperature: 0.0
    agent_id: test2
# ... repeated configuration
```

### Solution: Default Configuration

With defaults, tests only specify what's unique:

```yaml
# .judge_llm.defaults.yaml (shared)
providers:
  - type: gemini
    model: gemini-2.0-flash-exp
    temperature: 0.0

evaluators:
  - type: response_evaluator
  - type: cost_evaluator
    max_cost: 0.05

# test1.yaml (simple!)
dataset:
  loader: local_file
  paths: [./test1.json]

providers:
  - agent_id: test1

# test2.yaml (simple!)
dataset:
  loader: local_file
  paths: [./test2.json]

providers:
  - agent_id: test2
```

## Files

```
02-default-config/
├── .judge_llm.defaults.yaml   # Shared defaults
├── config.yaml                # Test-specific config
├── sample.evalset.json        # Test cases
├── run.sh                     # Runner script
├── run_evaluation.py          # Python runner
└── README.md                  # Instructions
```

## Configuration

### .judge_llm.defaults.yaml

```yaml
# Default provider: Gemini Flash for cost efficiency
providers:
  - type: gemini
    model: gemini-2.0-flash-exp
    temperature: 0.0  # Deterministic responses

# Standard evaluation criteria
evaluators:
  - type: response_evaluator
    llm_provider: gemini
    config:
      similarity_threshold: 0.7

  - type: cost_evaluator
    config:
      max_cost_per_case: 0.05  # Max $0.05 per test

# Default output
reporters:
  - type: console
```

**Key Points:**
- Defines common settings for all tests
- Should be generic and reusable
- Version controlled with your project
- Can be overridden by test configs

### config.yaml

```yaml
dataset:
  loader: local_file
  paths:
    - ./sample.evalset.json

providers:
  - agent_id: test_agent
    # type, model, temperature inherited from defaults
```

**Much simpler!** Only specifies:
- What test data to use
- Agent identifier

Everything else comes from defaults.

## How Configuration Merging Works

Judge LLM merges configuration from three sources (in order):

1. **Global defaults** (`~/.judge_llm/defaults.yaml`)
2. **Project defaults** (`.judge_llm.defaults.yaml`)
3. **Test config** (`config.yaml`)

Later values override earlier ones.

### Merge Example

**Defaults:**
```yaml
providers:
  - type: gemini
    model: gemini-2.0-flash-exp
    temperature: 0.0

evaluators:
  - type: response_evaluator
```

**Test Config:**
```yaml
providers:
  - agent_id: my_agent
    temperature: 0.5  # Override

evaluators:
  - type: cost_evaluator  # Add
```

**Merged Result:**
```yaml
providers:
  - type: gemini              # From defaults
    model: gemini-2.0-flash-exp  # From defaults
    temperature: 0.5          # From test (overridden)
    agent_id: my_agent        # From test

evaluators:
  - type: response_evaluator  # From defaults
  - type: cost_evaluator      # From test
```

### Merge Rules

1. **Scalar values** (strings, numbers, booleans): Test overrides defaults
2. **Lists**: Merged (defaults + test items)
3. **Dictionaries**: Deep merge (recursive)

## Running the Example

```bash
cd examples/02-default-config
judge-llm run --config config.yaml
```

The evaluator:
1. Finds `.judge_llm.defaults.yaml` in current or parent directory
2. Merges it with `config.yaml`
3. Runs evaluation with merged configuration

## Expected Output

```
Starting evaluation...

Using defaults from: .judge_llm.defaults.yaml

Evaluation Progress:
  test_001: ✓ PASSED (cost: $0.0012, time: 1.2s)
    Response: ✓ PASSED (similarity: 0.85)
    Cost: ✓ PASSED ($0.0012 < $0.05)

  test_002: ✓ PASSED (cost: $0.0015, time: 1.4s)
    Response: ✓ PASSED (similarity: 0.91)
    Cost: ✓ PASSED ($0.0015 < $0.05)

Summary:
  Total Tests: 2
  Passed: 2
  Failed: 0
  Success Rate: 100.0%
  Total Cost: $0.0027
  Total Time: 2.6s
```

## Benefits of Using Defaults

### 1. DRY (Don't Repeat Yourself)

Define common settings once, use everywhere.

**Before:**
- 10 test files × 50 lines = 500 lines of configuration

**After:**
- 1 defaults file (50 lines) + 10 test files (5 lines each) = 100 lines total

**Result:** 80% reduction in configuration code!

### 2. Consistency

All tests use the same:
- Model versions
- Temperature settings
- Evaluation criteria
- Reporting formats

### 3. Easy Updates

**Change model globally:**
```yaml
# Edit .judge_llm.defaults.yaml once
providers:
  - type: gemini
    model: gemini-2.0-flash-exp  # Change this
```

All tests automatically use the new model!

### 4. Environment-Specific Defaults

```yaml
# .judge_llm.defaults.yaml
providers:
  - type: gemini
    model: ${MODEL:-gemini-2.0-flash-exp}
```

```bash
# Development: fast, cheap model
export MODEL=gemini-1.5-flash
judge-llm run --config test.yaml

# Production: best model
export MODEL=gemini-1.5-pro
judge-llm run --config test.yaml
```

## Overriding Defaults

Test configs can override any default value.

### Override Provider Settings

```yaml
# config.yaml
providers:
  - agent_id: my_agent
    temperature: 1.0  # Override default 0.0
    model: gemini-1.5-pro  # Override default model
```

### Override Evaluator Settings

```yaml
# config.yaml
evaluators:
  - type: cost_evaluator
    config:
      max_cost_per_case: 0.01  # Stricter than default 0.05
```

### Add Additional Components

```yaml
# config.yaml
reporters:
  # Console from defaults
  - type: json  # Add JSON reporter
    output_path: ./results.json
  - type: html  # Add HTML reporter
    output_path: ./report.html
```

### Disable Default Components

```yaml
# config.yaml
evaluators:
  - type: response_evaluator
    enabled: false  # Disable from defaults
  - type: trajectory_evaluator  # Add different evaluator
```

## Advanced Patterns

### Environment-Specific Defaults

```yaml
# .judge_llm.defaults.dev.yaml (development)
providers:
  - type: gemini
    model: gemini-1.5-flash
    temperature: 0.0

reporters:
  - type: console

# .judge_llm.defaults.prod.yaml (production)
providers:
  - type: gemini
    model: gemini-1.5-pro
    temperature: 0.0

reporters:
  - type: database
    db_path: /var/lib/judge_llm/results.db
```

```bash
# Use different defaults
judge-llm run --config test.yaml --defaults .judge_llm.defaults.dev.yaml
judge-llm run --config test.yaml --defaults .judge_llm.defaults.prod.yaml
```

### Team Defaults

```yaml
# .judge_llm.defaults.yaml (team defaults)
providers:
  - type: gemini
    model: ${TEAM_MODEL:-gemini-2.0-flash-exp}

evaluators:
  - type: response_evaluator
  - type: cost_evaluator
    config:
      max_cost_per_case: ${MAX_COST:-0.05}
```

Each team member can customize via environment variables.

### Custom Component Registration

```yaml
# .judge_llm.defaults.yaml
evaluators:
  - type: custom
    module_path: ./evaluators/safety.py
    class_name: SafetyEvaluator
    register_as: safety  # Register globally
    config:
      strict_mode: true
```

Now all tests can use `type: safety` without specifying module_path!

## Best Practices

### 1. Keep Defaults Generic

**Good:**
```yaml
providers:
  - type: gemini
    model: gemini-2.0-flash-exp
    temperature: 0.0
```

**Bad:**
```yaml
providers:
  - type: gemini
    agent_id: specific_test_123  # Too specific!
```

### 2. Document Your Defaults

```yaml
# .judge_llm.defaults.yaml

# Default provider configuration
# Using Gemini Flash for cost-effectiveness
# Temperature 0.0 for deterministic results
providers:
  - type: gemini
    model: gemini-2.0-flash-exp
    temperature: 0.0

# Standard evaluation criteria
# Response quality + cost monitoring
evaluators:
  - type: response_evaluator
    config:
      similarity_threshold: 0.7  # 70% similarity required

  - type: cost_evaluator
    config:
      max_cost_per_case: 0.05  # Alert if test > $0.05
```

### 3. Version Control Defaults

```bash
git add .judge_llm.defaults.yaml
git commit -m "Add project-wide evaluation defaults"
```

Team members get consistent settings when they clone.

### 4. Use Environment Variables

```yaml
providers:
  - type: gemini
    model: ${MODEL:-gemini-2.0-flash-exp}
    temperature: ${TEMPERATURE:-0.0}
```

Allows customization without editing files.

### 5. Separate by Environment

```
project/
├── .judge_llm.defaults.yaml          # Base defaults
├── .judge_llm.defaults.dev.yaml      # Dev overrides
├── .judge_llm.defaults.prod.yaml     # Prod overrides
└── .judge_llm.defaults.ci.yaml       # CI overrides
```

### 6. Test Your Defaults

```bash
# Verify merged configuration
judge-llm run --config test.yaml --dry-run --verbose
```

Shows the final merged configuration before running.

## Troubleshooting

### Defaults Not Found

**Error:** `Defaults file not found: .judge_llm.defaults.yaml`

**Solution:**
```bash
# Check current directory
ls -la .judge_llm.defaults.yaml

# Check parent directories
find . -name ".judge_llm.defaults.yaml"

# Specify explicitly
judge-llm run --config test.yaml --defaults path/to/defaults.yaml
```

### Unexpected Merging

**Problem:** Test config not overriding defaults

**Debug:**
```bash
# Show merged config
judge-llm run --config test.yaml --show-config

# Show where each value comes from
judge-llm run --config test.yaml --trace-config
```

### Environment Variables Not Resolved

**Error:** `API key not found: ${GEMINI_API_KEY}`

**Solution:**
```bash
# Set environment variable
export GEMINI_API_KEY=your_key

# Or use .env file
echo "GEMINI_API_KEY=your_key" > .env
```

## Examples

### Multiple Tests, One Default

```yaml
# .judge_llm.defaults.yaml
providers:
  - type: gemini
    model: gemini-2.0-flash-exp

evaluators:
  - type: response_evaluator
  - type: cost_evaluator

# test_accuracy.yaml
dataset:
  loader: local_file
  paths: [./accuracy_tests.json]
providers:
  - agent_id: accuracy_test

# test_performance.yaml
dataset:
  loader: local_file
  paths: [./performance_tests.json]
providers:
  - agent_id: performance_test
evaluators:
  - type: latency_evaluator  # Additional evaluator

# test_cost.yaml
dataset:
  loader: local_file
  paths: [./cost_tests.json]
providers:
  - agent_id: cost_test
evaluators:
  - type: cost_evaluator
    config:
      max_cost_per_case: 0.01  # Stricter
```

All three tests share common config but customize as needed.

## Next Steps

After mastering defaults:

1. **[Config Override](./config-override)** - Per-test evaluator overrides
2. **[Custom Evaluator](./custom-evaluator)** - Register custom components
3. **[Safety Evaluation](./safety-evaluation)** - Complex multi-test setups

## Related Documentation

- [Default Configurations Guide](../guides/default-configs)
- [Configuration Guide](../guides/configuration)
- [Environment Variables](../guides/environment-variables)
- [CLI Reference](../guides/cli-reference)
