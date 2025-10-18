# Evaluator Config Guide

## What is `evaluator_config`?

`evaluator_config` is a **per-test-case configuration** that allows you to override evaluator settings for individual test cases in your evalset files.

## Two Levels of Configuration

### 1. Global Configuration (in config.yaml)

This applies to **all test cases** by default:

```yaml
evaluators:
  - type: response_validator
    enabled: true
    config:
      similarity_threshold: 0.6
      match_type: semantic
```

### 2. Per-Test-Case Configuration (in evalset.json)

This **overrides** the global config for a **specific test case**:

```json
{
  "eval_id": "special_case_001",
  "conversation": [...],
  "session_input": {...},
  "evaluator_config": {
    "ResponseValidator": {
      "similarity_threshold": 0.8,
      "match_type": "rouge"
    }
  }
}
```

## How It Works

### Data Model

Defined in [judge_llm/core/models.py:84](judge_llm/core/models.py#L84):

```python
class EvalCase(BaseModel):
    eval_id: str
    conversation: List[Invocation]
    session_input: SessionInput
    creation_timestamp: float
    evaluator_config: Optional[Dict[str, Any]] = Field(default_factory=dict)
```

### Flow

1. **Global config** is set when evaluators are initialized from `config.yaml`
2. **Per-test-case config** is loaded from `evaluator_config` field in evalset JSON
3. **Merge happens** in [evaluate.py:523](judge_llm/core/evaluate.py#L523):

```python
eval_result = evaluator.evaluate(
    eval_case=eval_case,
    agent_metadata=provider.agent_metadata,
    provider_result=provider_result,
    eval_config=eval_case.evaluator_config.get(evaluator_name)
)
```

4. **BaseEvaluator merges** the configs in [base.py:40-55](judge_llm/evaluators/base.py#L40-L55):

```python
def get_config(self, eval_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Merge per-test-case config over instance config"""
    if eval_config is None:
        return self.config.copy()

    merged = self.config.copy()
    merged.update(eval_config)  # Per-test overrides global
    return merged
```

## Real-World Examples

### Example 1: Different Thresholds for Different Test Cases

**config.yaml** (global):
```yaml
evaluators:
  - type: response_validator
    config:
      similarity_threshold: 0.6  # Default for most tests
```

**evalset.json** (specific test):
```json
{
  "eval_id": "strict_test_001",
  "evaluator_config": {
    "ResponseValidator": {
      "similarity_threshold": 0.9  // This test requires 90% match
    }
  }
}
```

### Example 2: Safety Checks (from your example 04)

**Global (config.yaml)**:
```yaml
evaluators:
  - type: custom
    module_path: ./evaluators/safety_evaluator.py
    class_name: SafetyEvaluator
    config:
      check_toxicity: true
      check_pii: true
      check_harmful_instructions: true
      check_hate_speech: true
```

**Per-test-case override**:
```json
{
  "eval_id": "safety_001_pii_leak",
  "evaluator_config": {
    "SafetyEvaluator": {
      "check_pii": true,           // Focus on PII only
      "check_toxicity": false,      // Disable other checks
      "check_harmful_instructions": false,
      "check_hate_speech": false,
      "allowed_safety_issues": 0
    }
  }
}
```

### Example 3: Different Match Types

```json
{
  "eval_id": "exact_match_test",
  "evaluator_config": {
    "ResponseValidator": {
      "match_type": "exact",
      "similarity_threshold": 1.0,
      "case_sensitive": true
    }
  }
},
{
  "eval_id": "lenient_test",
  "evaluator_config": {
    "ResponseValidator": {
      "match_type": "recall",
      "similarity_threshold": 0.5
    }
  }
}
```

## Key Structure

```
evaluator_config: {
  "<EvaluatorClassName>": {
    "<setting1>": value1,
    "<setting2>": value2
  }
}
```

**Important**: The key must be the **evaluator class name**, not the type:
- ✅ `"ResponseValidator"` (class name)
- ❌ `"response_validator"` (type name)

## Usage in Custom Evaluators

When building your own evaluator, use `get_config()` to access merged settings:

```python
class MyEvaluator(BaseEvaluator):
    def evaluate(self, eval_case, agent_metadata, provider_result, eval_config=None):
        # Get merged config (per-test overrides instance)
        config = self.get_config(eval_config)

        # Use the merged config
        threshold = config.get("my_threshold", 0.5)
        strict_mode = config.get("strict_mode", False)

        # ... your evaluation logic
```

## Benefits

1. **Flexibility**: Different tests can have different requirements
2. **No Code Changes**: Just update JSON files to adjust test behavior
3. **Granular Control**: Override only what you need, inherit the rest
4. **Test-Specific Logic**: Enable/disable specific checks per test case

## Common Use Cases

1. **Varying strictness**: Some tests need exact matches, others allow flexibility
2. **Feature-specific checks**: Enable specific safety checks only for relevant tests
3. **Different metrics**: Use ROUGE for some tests, recall for others
4. **Threshold tuning**: Lower threshold for creative tests, higher for factual tests
5. **Debug mode**: Enable verbose logging for specific failing tests

## Complete Example

**evalset.json**:
```json
{
  "eval_set_id": "mixed_tests",
  "eval_cases": [
    {
      "eval_id": "test_001_exact",
      "conversation": [...],
      "evaluator_config": {
        "ResponseValidator": {
          "match_type": "exact",
          "similarity_threshold": 1.0
        }
      }
    },
    {
      "eval_id": "test_002_semantic",
      "conversation": [...],
      "evaluator_config": {
        "ResponseValidator": {
          "match_type": "semantic",
          "similarity_threshold": 0.7
        }
      }
    },
    {
      "eval_id": "test_003_default",
      "conversation": [...]
      // No evaluator_config - uses global config
    }
  ]
}
```

**Result**:
- `test_001_exact`: Uses exact matching with 100% threshold
- `test_002_semantic`: Uses semantic matching with 70% threshold
- `test_003_default`: Uses whatever is in config.yaml

## Summary

`evaluator_config` gives you **per-test-case control** over how evaluators behave, allowing you to create sophisticated test suites with varying requirements without changing code!
