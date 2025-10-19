---
sidebar_position: 5
---

# Evalset Format

Complete guide to the dataset format used by Judge LLM for evaluations.

## Overview

Judge LLM supports both **JSON and YAML** formats for defining evaluation datasets. Each file contains an evaluation set with test cases, conversation history, and configuration.

### Supported Formats

- **JSON** (`.json`) - Traditional structured format
- **YAML** (`.yaml`, `.yml`) - Human-readable alternative

Both formats use the same data structure - choose whichever format you prefer for your workflow.

## Basic Structure

An evaluation dataset consists of:
- **EvalSet**: Container with metadata and test cases
- **EvalCases**: Individual test scenarios
- **Invocations**: Conversation turns with user/model exchanges
- **SessionInput**: Configuration for each test case

### JSON Format

```json
{
  "eval_set_id": "my_test_set_v1",
  "name": "My Test Set",
  "description": "Description of this evaluation set",
  "creation_timestamp": 1704067000.0,
  "eval_cases": [
    {
      "eval_id": "test_001",
      "conversation": [],
      "session_input": {
        "app_name": "math_tutor",
        "user_id": "test_user"
      },
      "creation_timestamp": 1704067200.0
    }
  ]
}
```

### YAML Format

```yaml
eval_set_id: my_test_set_v1
name: My Test Set
description: Description of this evaluation set
creation_timestamp: 1704067000.0
eval_cases:
  - eval_id: test_001
    conversation: []
    session_input:
      app_name: math_tutor
      user_id: test_user
    creation_timestamp: 1704067200.0
```

## Loading Datasets

### Single File

**JSON:**
```yaml
dataset:
  loader: local_file
  paths:
    - ./tests/math.json
```

**YAML:**
```yaml
dataset:
  loader: local_file
  paths:
    - ./tests/math.yaml
```

### Multiple Files (Mixed Formats)

```yaml
dataset:
  loader: local_file
  paths:
    - ./tests/math.json
    - ./tests/science.yaml
    - ./tests/history.yml
```

### Directory Loading

Load all JSON files:
```yaml
dataset:
  loader: directory
  paths: [./tests]
  pattern: "*.json"
```

Load all YAML files:
```yaml
dataset:
  loader: directory
  paths: [./tests]
  pattern: "*.yaml"
```

## Best Practices

### Choose Your Format

**Use YAML when:**
- Writing datasets by hand
- You want readability and comments
- Working with multi-line text

**Use JSON when:**
- Generating datasets programmatically
- Strict schema validation is needed

### Examples

See [examples/01-gemini-agent/](https://github.com/yourusername/judge-llm/tree/main/examples/01-gemini-agent) for complete examples in both JSON and YAML formats.

## Validation

Validate your configuration and dataset:

```bash
judge-llm validate --config config.yaml
```

## Related Documentation

- [Basic Usage](./basic-usage)
- [Configuration Guide](./configuration)
- [Examples](../examples/overview)
