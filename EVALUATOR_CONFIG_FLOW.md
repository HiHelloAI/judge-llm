# Evaluator Config Override Flow

## Overview

This document explains how per-test-case evaluator configuration overrides work in the Judge LLM framework.

## Architecture

### 1. Data Flow

```
evalset.json (evaluator_config)
    ↓
EvalCase.evaluator_config (Dict[str, Dict[str, Any]])
    ↓
evaluate.py extracts evaluator-specific config
    ↓
BaseEvaluator.evaluate(eval_config=...)
    ↓
BaseEvaluator.get_config(eval_config) merges with global config
    ↓
Evaluator uses merged configuration
```

### 2. Configuration Levels

There are **two levels** of evaluator configuration:

1. **Global Config** (config.yaml): Applies to all test cases
2. **Per-Test-Case Config** (evalset.json): Overrides global for specific tests

## Implementation Details

### evalset.json Structure

```json
{
  "eval_cases": [
    {
      "eval_id": "test_001",
      "conversation": [...],
      "evaluator_config": {
        "ResponseEvaluator": {
          "similarity_threshold": 0.9,
          "match_type": "exact"
        },
        "LatencyEvaluator": {
          "max_latency_seconds": 5
        }
      }
    }
  ]
}
```

**Key Points:**
- `evaluator_config` is a **nested dict**
- Top-level keys are **evaluator class names** (e.g., "ResponseEvaluator")
- Each evaluator has its own configuration dict

### EvalCase Model

```python
class EvalCase(BaseModel):
    eval_id: str
    conversation: List[Invocation]
    session_input: SessionInput
    creation_timestamp: float
    evaluator_config: Optional[Dict[str, Any]] = Field(default_factory=dict)
```

The `evaluator_config` field stores the nested configuration structure.

### Config Extraction (evaluate.py)

```python
# Run evaluators
for evaluator in evaluators:
    # Extract per-test-case config for this specific evaluator
    evaluator_specific_config = None
    if hasattr(eval_case, 'evaluator_config') and eval_case.evaluator_config:
        evaluator_name = evaluator.get_evaluator_name()  # e.g., "ResponseEvaluator"
        evaluator_specific_config = eval_case.evaluator_config.get(evaluator_name, None)

    # Pass evaluator-specific config
    eval_result = evaluator.evaluate(
        eval_case=eval_case,
        agent_metadata=provider.agent_metadata,
        provider_result=provider_result,
        eval_config=evaluator_specific_config  # Only this evaluator's config
    )
```

**Important:**
- Each evaluator receives **only its own configuration**
- Uses `get_evaluator_name()` to extract the right config from the nested structure
- If no override exists for an evaluator, `eval_config=None`

### Config Merging (BaseEvaluator)

```python
class BaseEvaluator(ABC):
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}  # Global config from config.yaml

    def get_config(self, eval_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Merge per-test-case config over global config"""
        if eval_config is None:
            return self.config.copy()

        # Per-test-case config takes precedence
        merged = self.config.copy()
        merged.update(eval_config)
        return merged
```

**Merge Rules:**
- Start with global config (from `__init__`)
- Override with per-test-case config (if provided)
- Per-test-case values **completely replace** global values (not deep merge)

### Usage in Evaluators

```python
class ResponseEvaluator(BaseEvaluator):
    def evaluate(self, eval_case, agent_metadata, provider_result, eval_config=None):
        # Get merged config
        config = self.get_config(eval_config)

        # Extract configuration values
        similarity_threshold = config.get("similarity_threshold", 0.8)
        match_type = config.get("match_type", "semantic")

        # Use configuration in evaluation logic
        ...
```

## Example Scenarios

### Scenario 1: No Override

**config.yaml:**
```yaml
evaluators:
  - type: response_evaluator
    config:
      similarity_threshold: 0.8
      match_type: semantic
```

**evalset.json:**
```json
{
  "eval_id": "test_001",
  "conversation": [...],
  // No evaluator_config field
}
```

**Result:**
- `eval_config = None`
- `get_config(None)` returns global config: `{similarity_threshold: 0.8, match_type: "semantic"}`

### Scenario 2: Partial Override

**config.yaml:**
```yaml
evaluators:
  - type: response_evaluator
    config:
      similarity_threshold: 0.8
      match_type: semantic
      case_sensitive: false
```

**evalset.json:**
```json
{
  "eval_id": "test_002",
  "evaluator_config": {
    "ResponseEvaluator": {
      "similarity_threshold": 1.0
    }
  }
}
```

**Result:**
- `eval_config = {similarity_threshold: 1.0}`
- Merged config: `{similarity_threshold: 1.0, match_type: "semantic", case_sensitive: false}`
- Only `similarity_threshold` is overridden, other values retained

### Scenario 3: Multiple Evaluators

**evalset.json:**
```json
{
  "eval_id": "test_003",
  "evaluator_config": {
    "ResponseEvaluator": {
      "similarity_threshold": 0.9,
      "match_type": "exact"
    },
    "LatencyEvaluator": {
      "max_latency_seconds": 5
    }
  }
}
```

**Result:**
- ResponseEvaluator receives: `{similarity_threshold: 0.9, match_type: "exact"}`
- LatencyEvaluator receives: `{max_latency_seconds: 5}`
- Each evaluator gets only its own config

## Best Practices

### 1. Use Evaluator Class Names

Always use the **exact class name** as the key:
```json
"ResponseEvaluator"  // ✓ Correct
"response_evaluator"  // ✗ Wrong - this is the registry type, not class name
```

### 2. Provide Sensible Defaults

Global config should have sensible defaults for most test cases:
```yaml
evaluators:
  - type: response_evaluator
    config:
      similarity_threshold: 0.6  # Lenient default
      match_type: semantic
```

Override only when specific tests need different behavior:
```json
{
  "eval_id": "exact_match_test",
  "evaluator_config": {
    "ResponseEvaluator": {
      "similarity_threshold": 1.0,
      "match_type": "exact"
    }
  }
}
```

### 3. Document Why Overrides Are Needed

In example files, explain why each test case needs different config:
```json
{
  "eval_id": "test_creative_writing",
  "evaluator_config": {
    "ResponseEvaluator": {
      "match_type": "recall",
      "similarity_threshold": 0.3
      // Using recall metric because creative responses may be longer
      // but should contain key concepts from expected response
    }
  }
}
```

### 4. Keep Overrides Minimal

Only override what's necessary:
```json
// Good - only override what changes
{
  "ResponseEvaluator": {
    "similarity_threshold": 0.9
  }
}

// Avoid - don't repeat unchanged values
{
  "ResponseEvaluator": {
    "similarity_threshold": 0.9,
    "match_type": "semantic",  // Already the global default
    "case_sensitive": false    // Already the global default
  }
}
```

## Debugging

### Check What Config an Evaluator Receives

Add debug logging in your evaluator:

```python
def evaluate(self, eval_case, agent_metadata, provider_result, eval_config=None):
    config = self.get_config(eval_config)
    self.logger.debug(f"Evaluating {eval_case.eval_id} with config: {config}")
    ...
```

### Verify evaluator_config Structure

Use Python to validate your evalset.json:

```python
import json
from judge_llm.loaders import LocalFileLoader

loader = LocalFileLoader(file_path="test_cases.evalset.json")
eval_sets = loader.load()

for eval_set in eval_sets:
    for case in eval_set.eval_cases:
        print(f"\n{case.eval_id}:")
        print(f"  evaluator_config: {case.evaluator_config}")
```

## Common Issues

### Issue 1: Config Not Applied

**Symptom:** Evaluator uses global config even though override is specified

**Causes:**
1. Wrong evaluator name in JSON (use class name, not registry type)
2. Typo in evaluator name
3. JSON syntax error preventing parsing

**Solution:** Verify evaluator class name matches exactly:
```python
evaluator = ResponseEvaluator()
print(evaluator.get_evaluator_name())  # Should print: "ResponseEvaluator"
```

### Issue 2: Invalid JSON

**Symptom:** `JSONDecodeError` when loading evalset

**Causes:**
1. JavaScript-style comments (`//`) in JSON
2. Trailing commas
3. Missing quotes around keys

**Solution:** Validate JSON:
```bash
python -m json.tool test_cases.evalset.json
```

### Issue 3: Config Not Merged Correctly

**Symptom:** Global config values disappear when override is applied

**Cause:** Using `=` instead of `.update()` in custom evaluator

**Solution:** Always use `self.get_config(eval_config)` from BaseEvaluator:
```python
# Correct
config = self.get_config(eval_config)

# Wrong - breaks merging
config = eval_config or self.config
```

## Related Files

- [judge_llm/core/evaluate.py](judge_llm/core/evaluate.py:518-530) - Config extraction logic
- [judge_llm/evaluators/base.py](judge_llm/evaluators/base.py:40-55) - Config merging logic
- [judge_llm/core/models.py](judge_llm/core/models.py:84) - EvalCase.evaluator_config field
- [examples/05-evaluator-config-override/](examples/05-evaluator-config-override/) - Complete working example
- [EVALUATOR_CONFIG_GUIDE.md](EVALUATOR_CONFIG_GUIDE.md) - User-facing documentation
