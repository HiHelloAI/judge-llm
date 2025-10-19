---
sidebar_position: 6
---

# Environment Variables

Comprehensive guide to using environment variables for configuration in Judge LLM.

## Overview

Environment variables allow you to:
- Keep sensitive data (API keys) out of version control
- Configure different settings per environment (dev, staging, prod)
- Override configuration values at runtime
- Share configurations across team members safely

## Quick Start

### 1. Create .env File

Create a `.env` file in your project root:

```bash
# .env
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

### 2. Reference in Configuration

Use `${VARIABLE_NAME}` syntax in your YAML config:

```yaml
# test.yaml
providers:
  - type: gemini
    agent_id: test_agent
    api_key: ${GEMINI_API_KEY}
```

### 3. Run Evaluation

Judge LLM automatically loads `.env` files:

```bash
judge-llm run --config test.yaml
```

## Syntax

### Basic Reference

```yaml
api_key: ${API_KEY}
```

### With Default Value

Use `:-` for default values:

```yaml
model: ${MODEL:-gemini-2.0-flash-exp}
temperature: ${TEMPERATURE:-0.0}
```

If `MODEL` is not set, it defaults to `gemini-2.0-flash-exp`.

### Required Variables

Variables without defaults will cause an error if not set:

```yaml
api_key: ${API_KEY}  # Error if API_KEY not set
```

## Configuration Examples

### Provider Configuration

```yaml
providers:
  - type: ${PROVIDER_TYPE:-gemini}
    agent_id: ${AGENT_ID:-default_agent}
    model: ${MODEL:-gemini-2.0-flash-exp}
    temperature: ${TEMPERATURE:-0.0}
    max_tokens: ${MAX_TOKENS:-1024}
    api_key: ${GEMINI_API_KEY}
```

### Multiple Providers

```yaml
providers:
  - type: gemini
    agent_id: gemini_agent
    api_key: ${GEMINI_API_KEY}
    
  - type: openai
    agent_id: openai_agent
    api_key: ${OPENAI_API_KEY}
    
  - type: anthropic
    agent_id: claude_agent
    api_key: ${ANTHROPIC_API_KEY}
```

### Reporter Configuration

```yaml
reporters:
  - type: json
    output_path: ${OUTPUT_PATH:-./results.json}
    
  - type: database
    db_path: ${DB_PATH:-./results.db}
```

### Complete Configuration

```yaml
dataset:
  loader: ${LOADER:-local_file}
  paths:
    - ${TEST_FILE:-./tests.json}

providers:
  - type: ${PROVIDER:-gemini}
    agent_id: ${AGENT_ID:-test}
    api_key: ${GEMINI_API_KEY}
    model: ${MODEL:-gemini-2.0-flash-exp}

evaluators:
  - type: response_evaluator
  - type: cost_evaluator
    max_cost: ${MAX_COST:-0.01}
  - type: latency_evaluator
    max_latency: ${MAX_LATENCY:-5.0}

reporters:
  - type: console
  - type: ${REPORTER:-json}
    output_path: ${OUTPUT_PATH:-./results.json}
```

## .env File Format

### Basic Format

```bash
# Comments start with #
GEMINI_API_KEY=your_key_here
OPENAI_API_KEY=another_key

# Quotes are optional for simple values
MODEL=gemini-2.0-flash-exp
MODEL="gemini-2.0-flash-exp"  # Same as above

# Use quotes for values with spaces
DESCRIPTION="My test configuration"
```

### Multi-line Values

```bash
# Use quotes for multi-line values
SYSTEM_PROMPT="You are a helpful assistant.
Always be polite and professional.
Provide accurate information."
```

### Special Characters

```bash
# Escape special characters
PASSWORD="p@ssw0rd\$123"
URL="https://api.example.com?key=value&other=123"
```

## Environment-Specific Configuration

### Development Environment

```bash
# .env.dev
ENVIRONMENT=development
GEMINI_API_KEY=dev_key_here
MODEL=gemini-2.0-flash-exp
MAX_COST=0.1
DB_PATH=./dev_results.db
```

### Staging Environment

```bash
# .env.staging
ENVIRONMENT=staging
GEMINI_API_KEY=staging_key_here
MODEL=gemini-2.0-flash-exp
MAX_COST=0.05
DB_PATH=./staging_results.db
```

### Production Environment

```bash
# .env.prod
ENVIRONMENT=production
GEMINI_API_KEY=prod_key_here
MODEL=gemini-2.0-flash-exp
MAX_COST=0.01
DB_PATH=./prod_results.db
```

### Loading Specific Env File

```bash
# Load specific environment
cp .env.dev .env
judge-llm run --config test.yaml

# Or export directly
export $(cat .env.prod | xargs)
judge-llm run --config test.yaml
```

## Setting Environment Variables

### Method 1: .env File (Recommended)

Create `.env` file:

```bash
GEMINI_API_KEY=your_key
```

Judge LLM automatically loads it.

### Method 2: Export Command

```bash
export GEMINI_API_KEY=your_key
export OPENAI_API_KEY=your_key
judge-llm run --config test.yaml
```

### Method 3: Inline

```bash
GEMINI_API_KEY=your_key judge-llm run --config test.yaml
```

### Method 4: Shell RC File

Add to `~/.bashrc` or `~/.zshrc`:

```bash
export GEMINI_API_KEY=your_key
export OPENAI_API_KEY=your_key
```

Then:

```bash
source ~/.bashrc
judge-llm run --config test.yaml
```

## Python API Usage

### Loading from .env

```python
from judge_llm import evaluate
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Variables are automatically available
report = evaluate(
    dataset={"loader": "local_file", "paths": ["./tests.json"]},
    providers=[{"type": "gemini", "agent_id": "test"}],
    evaluators=[{"type": "response_evaluator"}]
)
```

### Manual Environment Variables

```python
import os
from judge_llm import evaluate

# Set programmatically
os.environ['GEMINI_API_KEY'] = 'your_key'

# Or read from config
api_key = os.getenv('GEMINI_API_KEY')

report = evaluate(
    dataset={"loader": "local_file", "paths": ["./tests.json"]},
    providers=[{
        "type": "gemini",
        "agent_id": "test",
        "api_key": api_key
    }],
    evaluators=[{"type": "response_evaluator"}]
)
```

### Environment-Specific Loading

```python
import os
from dotenv import load_dotenv

# Load environment-specific file
env = os.getenv('ENVIRONMENT', 'development')
dotenv_file = f'.env.{env}'

if os.path.exists(dotenv_file):
    load_dotenv(dotenv_file)
else:
    load_dotenv()  # Fallback to .env

from judge_llm import evaluate

report = evaluate(...)
```

## CI/CD Integration

### GitHub Actions

```yaml
# .github/workflows/eval.yml
name: LLM Evaluation

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
        run: pip install judge-llm

      - name: Run evaluation
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          MODEL: gemini-2.0-flash-exp
          MAX_COST: 0.01
        run: judge-llm run --config test.yaml
```

### GitLab CI

```yaml
# .gitlab-ci.yml
evaluate:
  image: python:3.10
  variables:
    MODEL: "gemini-2.0-flash-exp"
    MAX_COST: "0.01"
  script:
    - pip install judge-llm
    - judge-llm run --config test.yaml
  only:
    - main
    - merge_requests
```

Set secrets in GitLab CI/CD settings:
- `GEMINI_API_KEY`
- `OPENAI_API_KEY`

### Jenkins

```groovy
pipeline {
    agent any
    
    environment {
        GEMINI_API_KEY = credentials('gemini-api-key')
        OPENAI_API_KEY = credentials('openai-api-key')
        MODEL = 'gemini-2.0-flash-exp'
        MAX_COST = '0.01'
    }
    
    stages {
        stage('Evaluate') {
            steps {
                sh '''
                    pip install judge-llm
                    judge-llm run --config test.yaml
                '''
            }
        }
    }
}
```

## Security Best Practices

### 1. Never Commit Secrets

**Add .env to .gitignore:**

```bash
# .gitignore
.env
.env.*
!.env.example
```

### 2. Use .env.example

Create `.env.example` as template:

```bash
# .env.example
GEMINI_API_KEY=your_gemini_key_here
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here

# Optional settings
MODEL=gemini-2.0-flash-exp
TEMPERATURE=0.0
MAX_COST=0.01
```

Commit this file, not `.env`.

### 3. Rotate Keys Regularly

```bash
# Generate new keys periodically
# Update .env and CI/CD secrets
```

### 4. Use Different Keys Per Environment

```bash
# .env.dev
GEMINI_API_KEY=dev_key_with_limits

# .env.prod
GEMINI_API_KEY=prod_key_with_monitoring
```

### 5. Restrict Permissions

```bash
chmod 600 .env
```

### 6. Use Secret Management

For production, use proper secret management:

- AWS Secrets Manager
- Google Secret Manager
- HashiCorp Vault
- Azure Key Vault

Example with AWS Secrets Manager:

```python
import boto3
import json
from judge_llm import evaluate

# Fetch from Secrets Manager
client = boto3.client('secretsmanager')
response = client.get_secret_value(SecretId='judge-llm/api-keys')
secrets = json.loads(response['SecretString'])

# Use secrets
report = evaluate(
    dataset={"loader": "local_file", "paths": ["./tests.json"]},
    providers=[{
        "type": "gemini",
        "agent_id": "prod",
        "api_key": secrets['GEMINI_API_KEY']
    }],
    evaluators=[{"type": "response_evaluator"}]
)
```

## Common Variables

### Provider API Keys

```bash
GEMINI_API_KEY=your_gemini_key
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
```

### Model Configuration

```bash
MODEL=gemini-2.0-flash-exp
TEMPERATURE=0.0
MAX_TOKENS=1024
```

### Evaluation Settings

```bash
MAX_COST=0.01
MAX_LATENCY=5.0
```

### File Paths

```bash
TEST_FILE=./tests.json
OUTPUT_PATH=./results.json
DB_PATH=./results.db
```

### Environment Identification

```bash
ENVIRONMENT=production
VERSION=1.0.0
```

## Troubleshooting

### Variable Not Found

**Error:** `API key not found for provider: gemini`

**Solutions:**
1. Check `.env` file exists
2. Verify variable name matches
3. Ensure no typos in variable reference
4. Check file permissions

### Variable Not Expanding

**Error:** Config shows `${GEMINI_API_KEY}` instead of actual value

**Solutions:**
1. Ensure using correct syntax: `${VAR_NAME}`
2. Check variable is set: `echo $GEMINI_API_KEY`
3. Reload environment: `source .env`

### Wrong Environment Loaded

**Issue:** Using development keys in production

**Solutions:**
1. Explicitly load correct file
2. Use environment variable to select: `ENVIRONMENT=prod`
3. Separate .env files per environment

### Permission Denied

**Error:** Cannot read `.env` file

**Solution:**
```bash
chmod 644 .env
```

## Related Documentation

- [Configuration Guide](./configuration.md)
- [Basic Usage](./basic-usage.md)
- [CLI Reference](./cli-reference.md)
