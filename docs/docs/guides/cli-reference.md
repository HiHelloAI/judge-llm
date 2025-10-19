---
sidebar_position: 1
---

# CLI Reference

Complete command-line interface reference for Judge LLM.

## Installation

```bash
pip install judge-llm
```

Verify installation:
```bash
judge-llm --version
```

## Commands

### run

Execute evaluations from a configuration file.

```bash
judge-llm run --config <path> [options]
```

**Arguments:**

| Argument | Short | Description | Required |
|----------|-------|-------------|----------|
| `--config` | `-c` | Path to YAML configuration file | Yes |
| `--report` | `-r` | Reporter type(s) to use | No |
| `--output` | `-o` | Output path for report | No |
| `--db-path` | | Database path (for database reporter) | No |
| `--no-validate` | | Skip configuration validation | No |

**Examples:**

Basic usage:
```bash
judge-llm run --config test.yaml
```

With specific reporter:
```bash
judge-llm run --config test.yaml --report json --output results.json
```

Multiple reporters:
```bash
judge-llm run --config test.yaml \
  --report console \
  --report html --output report.html \
  --report database --db-path results.db
```

Skip validation (faster):
```bash
judge-llm run --config test.yaml --no-validate
```

### list

List available providers, evaluators, or reporters.

```bash
judge-llm list <entity>
```

**Arguments:**

| Argument | Description | Values |
|----------|-------------|--------|
| `entity` | Component type to list | `providers`, `evaluators`, `reporters` |

**Examples:**

List providers:
```bash
judge-llm list providers
```

Output:
```
Available Providers:
  - anthropic
  - gemini
  - openai
```

List evaluators:
```bash
judge-llm list evaluators
```

Output:
```
Available Evaluators:
  - response_evaluator
  - trajectory_evaluator
  - cost_evaluator
  - latency_evaluator
```

List reporters:
```bash
judge-llm list reporters
```

Output:
```
Available Reporters:
  - console
  - database
  - html
  - json
```

### validate

Validate a configuration file without running evaluations.

```bash
judge-llm validate --config <path>
```

**Arguments:**

| Argument | Short | Description | Required |
|----------|-------|-------------|----------|
| `--config` | `-c` | Path to YAML configuration file | Yes |

**Examples:**

```bash
judge-llm validate --config test.yaml
```

Output if valid:
```
✓ Configuration is valid
```

Output if invalid:
```
✗ Configuration validation failed:
  - Missing required field: dataset.loader
  - Invalid provider type: invalid_provider
```

## Global Options

These options work with all commands:

| Option | Short | Description |
|--------|-------|-------------|
| `--help` | `-h` | Show help message |
| `--version` | `-v` | Show version number |
| `--verbose` | | Enable verbose logging |
| `--quiet` | `-q` | Suppress all output except errors |

**Examples:**

```bash
# Show help
judge-llm --help
judge-llm run --help

# Show version
judge-llm --version

# Verbose output
judge-llm run --config test.yaml --verbose

# Quiet mode
judge-llm run --config test.yaml --quiet
```

## Configuration File

The `--config` argument accepts YAML configuration files.

### Basic Structure

```yaml
dataset:
  loader: local_file
  paths:
    - ./tests.json

providers:
  - type: gemini
    agent_id: test_agent

evaluators:
  - type: response_evaluator

reporters:
  - type: console
```

### Environment Variables

Use `${VAR_NAME}` syntax to reference environment variables:

```yaml
providers:
  - type: gemini
    agent_id: ${AGENT_ID}
    api_key: ${GEMINI_API_KEY}

reporters:
  - type: database
    db_path: ${DB_PATH:-./results.db}  # Default value
```

Load from `.env` file:
```bash
# .env
AGENT_ID=my_agent
GEMINI_API_KEY=your_api_key
DB_PATH=./prod_results.db
```

```bash
judge-llm run --config test.yaml
```

### Default Configuration

Create `.judge_llm.defaults.yaml` in your project root or `~/.judge_llm/defaults.yaml` for global defaults:

```yaml
# .judge_llm.defaults.yaml
providers:
  - type: gemini
    model: gemini-2.0-flash-exp
    temperature: 0.0

reporters:
  - type: console
  - type: json
    output_path: ./results/latest.json
```

These settings are merged with your test config.

## Reporter Options

### Console Reporter

```bash
judge-llm run --config test.yaml --report console
```

No additional options needed.

### JSON Reporter

```bash
judge-llm run --config test.yaml \
  --report json \
  --output ./results.json
```

**Options:**
- `--output`: Path to JSON file (required)

### HTML Reporter

```bash
judge-llm run --config test.yaml \
  --report html \
  --output ./report.html
```

**Options:**
- `--output`: Path to HTML file (required)

### Database Reporter

```bash
judge-llm run --config test.yaml \
  --report database \
  --db-path ./results.db
```

**Options:**
- `--db-path`: Path to SQLite database (required)

### Multiple Reporters

Combine multiple reporters in a single run:

```bash
judge-llm run --config test.yaml \
  --report console \
  --report json --output results.json \
  --report html --output report.html \
  --report database --db-path results.db
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success - all tests passed |
| 1 | Failure - some tests failed or error occurred |
| 2 | Invalid configuration |
| 3 | Missing required arguments |

**Example Usage in Scripts:**

```bash
#!/bin/bash

judge-llm run --config test.yaml
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo "All tests passed!"
    # Deploy or continue
elif [ $EXIT_CODE -eq 1 ]; then
    echo "Tests failed!"
    exit 1
else
    echo "Configuration error!"
    exit 2
fi
```

## CI/CD Integration

### GitHub Actions

```yaml
name: Evaluate LLM

on: [push, pull_request]

jobs:
  evaluate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          pip install judge-llm
      
      - name: Run evaluations
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
        run: |
          judge-llm run --config test.yaml \
            --report console \
            --report html --output report.html
      
      - name: Upload report
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: evaluation-report
          path: report.html
      
      - name: Fail if tests failed
        run: |
          if [ $? -ne 0 ]; then
            echo "Evaluations failed"
            exit 1
          fi
```

### GitLab CI

```yaml
evaluate:
  image: python:3.10
  script:
    - pip install judge-llm
    - judge-llm run --config test.yaml --report json --output results.json
  artifacts:
    paths:
      - results.json
    when: always
  only:
    - main
    - merge_requests
```

### Jenkins

```groovy
pipeline {
    agent any
    
    environment {
        GEMINI_API_KEY = credentials('gemini-api-key')
    }
    
    stages {
        stage('Install') {
            steps {
                sh 'pip install judge-llm'
            }
        }
        
        stage('Evaluate') {
            steps {
                sh '''
                    judge-llm run --config test.yaml \
                      --report console \
                      --report html --output report.html
                '''
            }
        }
    }
    
    post {
        always {
            archiveArtifacts artifacts: 'report.html', allowEmptyArchive: true
        }
    }
}
```

## Advanced Usage

### Custom Reporters via CLI

While you can't register custom reporters directly via CLI, you can specify them in your config:

```yaml
# test.yaml
reporters:
  - type: custom
    module_path: ./reporters/slack_reporter.py
    class_name: SlackReporter
    webhook_url: ${SLACK_WEBHOOK_URL}
```

```bash
judge-llm run --config test.yaml
```

### Combining with Other Tools

**With jq for JSON processing:**
```bash
judge-llm run --config test.yaml --report json --output results.json

# Extract success rate
jq '.success_rate' results.json

# Filter failed tests
jq '.test_cases[] | select(.passed == false)' results.json
```

**With sqlite3 for database queries:**
```bash
judge-llm run --config test.yaml --report database --db-path results.db

# Query results
sqlite3 results.db "SELECT eval_id, passed, cost FROM test_cases ORDER BY cost DESC LIMIT 10"
```

### Batch Processing

Run multiple configurations:
```bash
#!/bin/bash

for config in configs/*.yaml; do
    echo "Running $config..."
    judge-llm run --config "$config" \
      --report json \
      --output "results/$(basename $config .yaml).json"
done
```

### Parallel Execution

```bash
# Run multiple configs in parallel
for config in configs/*.yaml; do
    judge-llm run --config "$config" &
done
wait

echo "All evaluations complete"
```

## Troubleshooting

### Command Not Found

**Issue:** `judge-llm: command not found`

**Solutions:**
- Ensure installed: `pip install judge-llm`
- Check PATH: `which judge-llm`
- Use full path: `python -m judge_llm.cli run --config test.yaml`

### Configuration Not Found

**Issue:** `Configuration file not found: test.yaml`

**Solutions:**
- Use absolute path: `judge-llm run --config /full/path/to/test.yaml`
- Check current directory: `ls test.yaml`

### API Key Not Found

**Issue:** `API key not found for provider: gemini`

**Solutions:**
- Set environment variable: `export GEMINI_API_KEY=your_key`
- Use `.env` file in project root
- Specify in config (not recommended for production)

### Invalid Configuration

**Issue:** Configuration validation errors

**Solution:** Use validate command first:
```bash
judge-llm validate --config test.yaml
```

Fix reported issues, then run again.

## Related Documentation

- [Configuration Guide](./configuration.md)
- [Python API Reference](./python-api.md)
- [Quick Start](../tutorial-basics/quick-start.md)
