# Register Custom Components in Default Config

This example demonstrates how to **register custom providers, evaluators, and reporters** in your default configuration so they can be used by name in your test configs.

## Overview

Judge LLM supports registering custom components in three categories:
- **Providers** - Custom LLM providers
- **Evaluators** - Custom evaluation logic
- **Reporters** - Custom report formats

All three use the same `register_as` pattern!

## How It Works

### Step 1: Register in Default Config

In `.judge_llm.defaults.yaml`:

```yaml
# Register custom provider
providers:
  - type: custom
    module_path: ./providers/my_provider.py
    class_name: MyProvider
    register_as: my_provider  # ← Register with this name

# Register custom evaluator
evaluators:
  - type: custom
    module_path: ./evaluators/safety.py
    class_name: SafetyEvaluator
    register_as: safety  # ← Register with this name

# Register custom reporter
reporters:
  - type: custom
    module_path: ./reporters/csv_reporter.py
    class_name: CSVReporter
    register_as: csv  # ← Register with this name
```

### Step 2: Use by Name in Test Configs

In your test config files:

```yaml
providers:
  - type: my_provider  # ← Use registered provider
    agent_id: test

evaluators:
  - type: safety  # ← Use registered evaluator
    config:
      severity: high

reporters:
  - type: csv  # ← Use registered reporter
    config:
      output_path: ./results.csv
```

## Complete Example

This example includes:

```
default_config_reporters/
├── .judge_llm.defaults.yaml    # Registers all custom components
├── test_config.yaml             # Uses registered components by name
├── reporters/
│   ├── csv_reporter.py
│   ├── slack_reporter.py
│   └── metrics_reporter.py
└── README.md
```

## Running the Example

```bash
cd examples/default_config_reporters

# Defaults auto-loaded, registered components available
judge-llm run --config test_config.yaml
```

## Registration Patterns

### Pattern 1: Providers

```yaml
# defaults.yaml
providers:
  - type: custom
    module_path: ./providers/anthropic_provider.py
    class_name: AnthropicProvider
    register_as: anthropic
```

```yaml
# test.yaml
providers:
  - type: anthropic
    agent_id: claude_agent
    config:
      model: claude-3-opus
      api_key: ${ANTHROPIC_API_KEY}
```

### Pattern 2: Evaluators

```yaml
# defaults.yaml
evaluators:
  - type: custom
    module_path: ./evaluators/safety_evaluator.py
    class_name: SafetyEvaluator
    register_as: safety
    
  - type: custom
    module_path: ./evaluators/compliance_evaluator.py
    class_name: ComplianceEvaluator
    register_as: compliance
```

```yaml
# test.yaml
evaluators:
  - type: safety
    config:
      check_pii: true
      check_toxicity: true
      
  - type: compliance
    config:
      regulations: [GDPR, HIPAA]
```

### Pattern 3: Reporters

```yaml
# defaults.yaml
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

```yaml
# test.yaml
reporters:
  - type: csv
    config: {output_path: ./results.csv}
    
  - type: slack
    config:
      webhook_url: ${SLACK_WEBHOOK}
      channel: "#evals"
```

## Benefits

### ✅ DRY Principle
Register once, use everywhere:

```yaml
# defaults.yaml - ONE registration
reporters:
  - type: custom
    module_path: ./my_csv.py
    class_name: CSVReporter
    register_as: csv
```

```yaml
# test1.yaml, test2.yaml, test3.yaml... - just use it!
reporters:
  - type: csv
```

### ✅ Team Standardization

Everyone uses the same components:

```bash
# Set team defaults
export JUDGE_LLM_DEFAULTS=/team/shared/defaults.yaml
```

Or commit to repo:
```
.judge_llm.defaults.yaml  ← everyone uses it automatically
```

### ✅ Clean Test Configs

Test configs become simple:

```yaml
dataset:
  paths: [./tests.json]

providers:
  - type: anthropic
    agent_id: claude

evaluators:
  - type: safety
  - type: compliance

reporters:
  - type: csv
  - type: slack
```

### ✅ Easy Updates

Change implementation in one place:

```yaml
# defaults.yaml - update once
reporters:
  - type: custom
    module_path: ./reporters/csv_v2.py  # ← Updated implementation
    class_name: CSVReporterV2
    register_as: csv
```

All test configs automatically use new version!

## Real-World Use Cases

### Use Case 1: Company-Wide Standards

```yaml
# ~/.judge_llm/defaults.yaml
providers:
  - type: custom
    module_path: /company/providers/company_llm.py
    class_name: CompanyLLM
    register_as: company_llm

evaluators:
  - type: custom
    module_path: /company/evaluators/compliance.py
    class_name: ComplianceEvaluator
    register_as: compliance

reporters:
  - type: custom
    module_path: /company/reporters/jira.py
    class_name: JiraReporter
    register_as: jira
```

Every employee automatically uses company components!

### Use Case 2: Multi-Environment Setup

```yaml
# Production defaults
reporters:
  - type: custom
    module_path: ./reporters/datadog.py
    class_name: DatadogReporter
    register_as: metrics

# Dev defaults
reporters:
  - type: custom
    module_path: ./reporters/console_metrics.py
    class_name: ConsoleMetrics
    register_as: metrics
```

Same test configs work in both environments!

### Use Case 3: CI/CD Pipeline

```yaml
# .judge_llm.defaults.yaml (in repo)
evaluators:
  - type: response_evaluator
  - type: cost_evaluator
  
  # Custom evaluators for CI
  - type: custom
    module_path: ./ci/evaluators/regression.py
    class_name: RegressionEvaluator
    register_as: regression

reporters:
  - type: custom
    module_path: ./ci/reporters/junit.py
    class_name: JUnitReporter
    register_as: junit
```

All CI jobs use the same setup!

## Advanced: Register All Three Together

```yaml
# Complete defaults example
providers:
  - type: custom
    module_path: ./providers/custom_llm.py
    class_name: CustomLLM
    register_as: custom_llm

evaluators:
  - type: response_evaluator
  - type: cost_evaluator
  - type: custom
    module_path: ./evaluators/safety.py
    class_name: SafetyEvaluator
    register_as: safety

reporters:
  - type: custom
    module_path: ./reporters/csv.py
    class_name: CSVReporter
    register_as: csv
  - type: custom
    module_path: ./reporters/slack.py
    class_name: SlackReporter
    register_as: slack
```

Then in test config:

```yaml
providers:
  - type: custom_llm
    agent_id: my_agent

evaluators:
  - type: safety

reporters:
  - type: csv
  - type: slack
```

Clean and simple!

## Default Config Search Order

Judge LLM searches for defaults in this order:

1. **Custom path** (`--defaults` flag)
2. **Environment variable** `JUDGE_LLM_DEFAULTS`
3. **Project directory** `.judge_llm.defaults.yaml`
4. **User home** `~/.judge_llm/defaults.yaml`

## Summary

**Question:** Can I register custom components in default config?

**Answer:** YES for all three! ✅

**Syntax:**
```yaml
# In defaults - add register_as field
providers/evaluators/reporters:
  - type: custom
    module_path: ./path/to/file.py
    class_name: MyClass
    register_as: my_name  # ← Magic happens here!
```

```yaml
# In test configs - just use the name!
providers/evaluators/reporters:
  - type: my_name
    config: {param: value}
```

**Benefits:**
- ✅ DRY - register once, use everywhere
- ✅ Team standardization
- ✅ Clean test configs
- ✅ Easy updates
- ✅ Works for providers, evaluators, AND reporters

Perfect for managing custom components at scale! 🎉
