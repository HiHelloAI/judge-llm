---
sidebar_position: 1
---

# Reporters Overview

Reporters generate output from evaluation results in various formats. They transform raw evaluation data into human-readable reports, machine-readable exports, or persistent storage.

## What are Reporters?

A **Reporter** is a component that:
- Receives the final `EvaluationReport` after all tests complete
- Formats and outputs results in a specific format
- Can write to files, databases, APIs, or terminal
- Supports custom output destinations

## Available Reporters

### Built-in Reporters

| Reporter | Output | Best For |
|----------|--------|----------|
| **[Console](./console-reporter)** | Terminal | Real-time monitoring, development |
| **[HTML](./html-reporter)** | Interactive web page | Sharing results, detailed analysis |
| **[JSON](./json-reporter)** | Machine-readable file | Programmatic analysis, CI/CD |
| **[Database](./database-reporter)** | SQLite database | Historical tracking, trend analysis |

### Custom Reporters

Create [custom reporters](./custom-reporters) for:
- CSV exports for spreadsheet analysis
- Slack/email notifications
- Datadog/metrics integration
- Custom dashboards
- Team-specific formats

## Configuration

### Basic Configuration

```yaml
reporters:
  - type: console
```

### Multiple Reporters

Generate multiple output formats simultaneously:

```yaml
reporters:
  - type: console              # Watch progress in terminal
  - type: html                 # Generate shareable report
    output_path: ./report.html
  - type: json                 # Export for analysis
    output_path: ./results.json
  - type: database             # Store in database
    db_path: ./results.db
```

### Custom Reporter

```yaml
reporters:
  - type: custom
    module_path: ./my_reporters/slack.py
    class_name: SlackReporter
    config:
      webhook_url: ${SLACK_WEBHOOK}
      channel: "#llm-evals"
```

## Reporter Selection Guide

### Console Reporter

**Use when:**
- Monitoring evaluation progress in real-time
- Development and debugging
- Quick validation runs
- CI/CD pipeline logs

**Output:** Rich terminal tables with colored status indicators

### HTML Reporter

**Use when:**
- Sharing results with team members
- Detailed analysis with drill-down
- Archiving evaluation results
- Creating presentation materials

**Output:** Self-contained HTML file with interactive UI

### JSON Reporter

**Use when:**
- Integrating with other tools
- Programmatic result analysis
- Data pipeline processing
- Version control of results

**Output:** Structured JSON with all evaluation data

### Database Reporter

**Use when:**
- Tracking evaluations over time
- Comparing historical results
- Regression detection
- Cost/performance trending

**Output:** SQLite database with queryable tables

## How Reporters Work

### Execution Flow

```
Evaluation Complete → EvaluationReport Object → Reporters → Outputs
                                                    ├─ Console
                                                    ├─ HTML file
                                                    ├─ JSON file
                                                    └─ Database
```

### Report Data Structure

Each reporter receives an `EvaluationReport` with:

```python
{
  "execution_runs": [...],           # All test executions
  "total_cost": 0.0234,              # Total API cost
  "total_time": 12.45,               # Total execution time
  "success_rate": 0.85,              # Pass rate (0.0-1.0)
  "overall_success": True/False,     # All tests passed?
  "summary": {
    "total_executions": 10,
    "successful_executions": 8,
    "failed_executions": 2
  }
}
```

Each execution run contains:
- Test case details (eval_id, inputs, expected outputs)
- Provider results (responses, cost, latency, tokens)
- Evaluator results (pass/fail, scores, feedback)
- Metadata (timestamps, agent_id, provider_type)

## Best Practices

### 1. Use Multiple Reporters

Combine reporters for different purposes:

```yaml
reporters:
  - type: console     # Monitor progress
  - type: database    # Track history
  - type: html        # Share with team
```

### 2. Configure Output Paths

Organize output files:

```yaml
reporters:
  - type: html
    output_path: ./reports/eval-{{timestamp}}.html
  
  - type: json
    output_path: ./results/{{date}}/results.json
  
  - type: database
    db_path: ./data/evaluations.db
```

### 3. Custom Reporters for Integration

Integrate with your tools:

```yaml
reporters:
  - type: console
  
  # Notify on Slack
  - type: custom
    module_path: ./reporters/slack.py
    class_name: SlackReporter
    register_as: slack
  
  # Send to Datadog
  - type: custom
    module_path: ./reporters/datadog.py
    class_name: DatadogReporter
    register_as: datadog
```

### 4. Environment-Specific Reporters

Different outputs for different environments:

```yaml
# Production defaults
reporters:
  - type: database
  - type: custom
    module_path: ./reporters/pagerduty.py
    class_name: PagerDutyReporter
    register_as: alerts

# Development defaults
reporters:
  - type: console
  - type: html
```

## Common Patterns

### Pattern 1: Development Workflow

```yaml
# Quick feedback during development
reporters:
  - type: console
  - type: html
    output_path: ./dev-report.html
```

### Pattern 2: CI/CD Pipeline

```yaml
# Structured output for automation
reporters:
  - type: json
    output_path: ./results.json
  - type: database
    db_path: ./ci-results.db
```

### Pattern 3: Production Monitoring

```yaml
# Persistent storage + notifications
reporters:
  - type: database
    db_path: ./prod-evals.db
  - type: custom
    module_path: ./reporters/monitoring.py
    class_name: MonitoringReporter
```

### Pattern 4: Team Sharing

```yaml
# Multiple formats for different audiences
reporters:
  - type: html
    output_path: ./reports/latest.html
  - type: json
    output_path: ./data/results.json
  - type: custom
    module_path: ./reporters/slack.py
    class_name: SlackReporter
```

## Troubleshooting

### Reporter Not Generating Output

**Issue:** Reporter runs but no output appears

**Solutions:**
- Check file permissions for output path
- Verify output directory exists
- Check reporter configuration
- Look for errors in logs

### Multiple Reporters, One Fails

**Issue:** One reporter fails, others succeed

**Behavior:** Evaluation continues, failing reporter logged as warning

**Solutions:**
- Check specific reporter configuration
- Verify required dependencies installed
- Check disk space for file reporters
- Validate network connectivity for API reporters

### Database Locked Error

**Issue:** `database is locked` error with Database reporter

**Cause:** Another process has database open

**Solutions:**
- Close database viewer/browser
- Use different database file
- Implement retry logic in custom reporters

## Next Steps

- [Console Reporter](./console-reporter) - Terminal output
- [HTML Reporter](./html-reporter) - Interactive web reports
- [JSON Reporter](./json-reporter) - Machine-readable export
- [Database Reporter](./database-reporter) - SQLite persistence
- [Custom Reporters](./custom-reporters) - Build your own

## API Reference

For implementation details, see the [BaseReporter API Reference](../guides/python-api).
