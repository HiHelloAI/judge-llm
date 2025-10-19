# Using Custom Reporters in Default Config

This example demonstrates how to **register custom reporters in your default configuration** so they can be used by name in your test configs.

## The Problem This Solves

Without this feature, you'd need to specify the full custom reporter details in every test config:

```yaml
# Every test config needs this verbose configuration
reporters:
  - type: custom
    module_path: ./reporters/csv_reporter.py
    class_name: CSVReporter
    config:
      output_path: ./results.csv
```

With default config registration, you can:
1. **Register once** in your defaults
2. **Use by name** in all test configs

## How It Works

### Step 1: Register in Default Config

In `.judge_llm.defaults.yaml` (project root or `~/.judge_llm/defaults.yaml`):

```yaml
reporters:
  - type: custom
    module_path: ./reporters/csv_reporter.py
    class_name: CSVReporter
    register_as: csv  # ← Register with this name
```

### Step 2: Use by Name in Test Configs

In your test config files:

```yaml
reporters:
  - type: csv  # ← Just use the registered name!
    config:
      output_path: ./my_results.csv
```

## Files in This Example

```
default_config_reporters/
├── .judge_llm.defaults.yaml    # Default config with reporter registrations
├── test_config.yaml             # Test config using registered reporters
├── reporters/
│   ├── csv_reporter.py          # Custom CSV reporter
│   ├── slack_reporter.py        # Custom Slack notification reporter
│   └── metrics_reporter.py      # Custom metrics reporter
└── README.md                    # This file
```

## Running the Example

```bash
cd examples/default_config_reporters

# The defaults will be auto-loaded from .judge_llm.defaults.yaml
judge-llm run --config test_config.yaml
```

## What Happens

1. **Framework loads defaults** from `.judge_llm.defaults.yaml`
2. **Processes `reporters` section** looking for `register_as` fields
3. **Registers custom reporters** with specified names (`csv`, `slack`, `metrics`)
4. **Loads test config** (`test_config.yaml`)
5. **Uses registered reporters** when it sees `type: csv`, `type: slack`, etc.
6. **Generates reports** in all formats

## Benefits

### 1. DRY (Don't Repeat Yourself)
Register once, use everywhere:

```yaml
# defaults.yaml - register once
reporters:
  - type: custom
    module_path: ./reporters/csv_reporter.py
    class_name: CSVReporter
    register_as: csv
```

```yaml
# test1.yaml - use it
reporters:
  - type: csv
    config: {output_path: ./test1.csv}

# test2.yaml - use it again
reporters:
  - type: csv
    config: {output_path: ./test2.csv}

# test3.yaml - use it again
reporters:
  - type: csv
    config: {output_path: ./test3.csv}
```

### 2. Team Standardization

Share default config across team:

```bash
# Everyone uses the same defaults
export JUDGE_LLM_DEFAULTS=/shared/team/defaults.yaml

# Or commit to repo
.judge_llm.defaults.yaml  ← in git
```

### 3. Environment-Specific Reporters

Different reporters for different environments:

```yaml
# Production defaults
reporters:
  - type: custom
    module_path: ./reporters/datadog_reporter.py
    class_name: DatadogReporter
    register_as: metrics
    
# Development defaults  
reporters:
  - type: custom
    module_path: ./reporters/local_metrics.py
    class_name: LocalMetricsReporter
    register_as: metrics
```

Same test config works in both environments!

### 4. Clean Test Configs

Your test configs become clean and focused:

```yaml
# test_config.yaml - clean and simple!
dataset:
  loader: local_file
  paths: [./tests.json]

providers:
  - type: gemini
    agent_id: my_agent

reporters:
  - type: csv
  - type: slack
  - type: metrics
```

## Advanced Usage

### Multiple Reporter Instances

Register once, use multiple times with different configs:

```yaml
# test_config.yaml
reporters:
  - type: csv
    config: {output_path: ./summary.csv}
    
  - type: csv
    config: {output_path: ./detailed.csv}
    
  - type: slack
    config:
      webhook_url: ${SLACK_URL_TEAM_A}
      channel: "#team-a"
      
  - type: slack
    config:
      webhook_url: ${SLACK_URL_TEAM_B}
      channel: "#team-b"
```

### Override Registration

If you need a different implementation for a specific test:

```yaml
reporters:
  # Use the registered version for most reports
  - type: csv
    config: {output_path: ./normal.csv}
  
  # Override with custom implementation for special case
  - type: custom
    module_path: ./special_csv.py
    class_name: SpecialCSVReporter
    config: {output_path: ./special.csv}
```

### Conditional Registration

Use environment variables to control which reporters are registered:

```yaml
# defaults.yaml
reporters:
  - type: custom
    module_path: ./reporters/csv_reporter.py
    class_name: CSVReporter
    register_as: csv
    
  # Only register Slack in production
  - type: custom
    module_path: ./reporters/slack_reporter.py
    class_name: SlackReporter
    register_as: slack
    # Use ${ENABLE_SLACK_REPORTER} to conditionally enable
```

## Default Config Search Order

Judge LLM searches for defaults in this order:

1. **Custom path** (if specified via `--defaults` flag)
2. **Environment variable** `JUDGE_LLM_DEFAULTS`
3. **Project directory** `.judge_llm.defaults.yaml` (current directory)
4. **User home** `~/.judge_llm/defaults.yaml`

## Real-World Use Cases

### Use Case 1: Company-Wide Standards

```yaml
# ~/.judge_llm/defaults.yaml (shared company-wide)
reporters:
  - type: custom
    module_path: /company/shared/reporters/jira.py
    class_name: JiraReporter
    register_as: jira
    
  - type: custom
    module_path: /company/shared/reporters/datadog.py
    class_name: DatadogReporter
    register_as: datadog
```

Every employee's tests automatically use company reporters!

### Use Case 2: CI/CD Pipeline

```yaml
# .judge_llm.defaults.yaml (in repo)
reporters:
  - type: custom
    module_path: ./ci/reporters/junit.py
    class_name: JUnitReporter
    register_as: junit  # For CI test results
    
  - type: custom
    module_path: ./ci/reporters/coverage.py
    class_name: CoverageReporter
    register_as: coverage
```

All CI jobs automatically use the same reporters!

### Use Case 3: Multi-Project Setup

```
company/
├── shared/
│   └── reporters/
│       ├── csv_reporter.py
│       ├── slack_reporter.py
│       └── metrics_reporter.py
├── project-a/
│   ├── .judge_llm.defaults.yaml  ← registers shared reporters
│   └── tests/
└── project-b/
    ├── .judge_llm.defaults.yaml  ← registers shared reporters
    └── tests/
```

## Learn More

- See [Custom Reporter Example](../custom_reporter_example/) for creating custom reporters
- See [Configuration Guide](../../docs/configuration.md) for all default config options
- See [Reporter Documentation](../../docs/reporters.md) for built-in reporters

## Summary

✅ Register custom reporters in defaults
✅ Use them by name in test configs
✅ Share standards across team
✅ Keep test configs clean and focused
✅ Environment-specific configurations
✅ Works with all default config locations
