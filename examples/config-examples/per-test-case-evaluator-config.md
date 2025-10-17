# Per-Test-Case Evaluator Configuration

## Problem

When using the same evaluator for multiple test cases, you might need different configuration for each test case. For example:

- Different thresholds for different test cases
- Different criteria for different scenarios
- Different models or parameters per case

## Solution

Judge LLM supports per-test-case evaluator configuration that overrides the global evaluator config.

## How It Works

### Configuration Precedence

```
1. Global evaluator config (in config.yaml)
2. Per-test-case evaluator config (in evalset.json) ← OVERRIDES global
```

### Example: Different Thresholds Per Test Case

#### 1. Global Configuration (`config.yaml`)

```yaml
evaluators:
  - type: llm_grader
    name: response_quality
    threshold: 0.7  # Default threshold for all tests
    config:
      model: gemini-2.0-flash-exp
      criteria:
        - accuracy
        - completeness
```

#### 2. Per-Test-Case Configuration (`sample.evalset.json`)

```json
{
  "eval_set_id": "mixed_threshold_tests",
  "name": "Tests with Different Requirements",
  "eval_cases": [
    {
      "eval_id": "easy_case_001",
      "conversation": [...],
      "session_input": {...},
      "evaluator_config": {
        "threshold": 0.5,
        "comment": "Lower threshold for this simpler case"
      }
    },
    {
      "eval_id": "hard_case_002",
      "conversation": [...],
      "session_input": {...},
      "evaluator_config": {
        "threshold": 0.9,
        "model": "gemini-pro",
        "criteria": ["accuracy", "completeness", "depth", "clarity"],
        "comment": "Higher threshold and more criteria for complex case"
      }
    },
    {
      "eval_id": "normal_case_003",
      "conversation": [...],
      "session_input": {...}
      // No evaluator_config = uses global config (threshold: 0.7)
    }
  ]
}
```

#### 3. How Evaluators Use It

Evaluators should use `self.get_config(eval_config)` to merge configurations:

```python
from judge_llm.evaluators.base import BaseEvaluator

class MyEvaluator(BaseEvaluator):
    def evaluate(self, eval_case, agent_metadata, provider_result, eval_config=None):
        # Merge per-test-case config with instance config
        config = self.get_config(eval_config)

        # Now use the merged config
        threshold = config.get('threshold', 0.7)
        model = config.get('model', 'default-model')
        criteria = config.get('criteria', [])

        # Perform evaluation...
```

## Use Cases

### 1. Different Thresholds

```json
{
  "eval_id": "test_001",
  "evaluator_config": {
    "threshold": 0.95  // Stricter threshold for this critical test
  }
}
```

### 2. Different Evaluation Criteria

```json
{
  "eval_id": "test_002",
  "evaluator_config": {
    "criteria": ["accuracy", "tone", "brevity"],  // Different criteria
    "comment": "This test focuses on communication style"
  }
}
```

### 3. Different Models for Evaluation

```json
{
  "eval_id": "test_003",
  "evaluator_config": {
    "model": "gemini-pro",  // Use more powerful model for this complex case
    "temperature": 0.1
  }
}
```

### 4. Test-Specific Parameters

```json
{
  "eval_id": "test_004",
  "evaluator_config": {
    "max_score": 100,
    "rubric": "detailed_rubric",
    "allow_partial_credit": true
  }
}
```

## Complete Example

### Config File

```yaml
# config.yaml
evaluators:
  - type: llm_grader
    name: response_quality
    threshold: 0.7  # Default for most tests
    config:
      model: gemini-2.0-flash-exp
      temperature: 0.5
      criteria:
        - accuracy
        - completeness
```

### Eval Set File

```json
{
  "eval_set_id": "example_set",
  "name": "Mixed Difficulty Tests",
  "eval_cases": [
    {
      "eval_id": "beginner_test",
      "conversation": [...],
      "session_input": {...},
      "evaluator_config": {
        "threshold": 0.5,
        "criteria": ["accuracy"]
      }
    },
    {
      "eval_id": "expert_test",
      "conversation": [...],
      "session_input": {...},
      "evaluator_config": {
        "threshold": 0.9,
        "model": "gemini-pro",
        "temperature": 0.1,
        "criteria": ["accuracy", "completeness", "depth", "technical_accuracy"]
      }
    }
  ]
}
```

## Implementation Notes

### For Evaluator Authors

When creating custom evaluators, always use `self.get_config(eval_config)`:

```python
class CustomEvaluator(BaseEvaluator):
    def __init__(self, config=None):
        super().__init__(config)
        # Store default config in self.config

    def evaluate(self, eval_case, agent_metadata, provider_result, eval_config=None):
        # Merge configs: per-test-case overrides instance config
        config = self.get_config(eval_config)

        # Use merged config
        threshold = config.get('threshold', 0.7)
        # ... rest of evaluation logic
```

### Config Merging Behavior

- **Shallow merge**: Dictionary keys from `eval_config` override keys in `self.config`
- **New keys**: Keys only in `eval_config` are added
- **Missing keys**: Keys only in `self.config` are preserved

Example:
```python
# self.config (from constructor)
{
    "threshold": 0.7,
    "model": "gemini-flash",
    "criteria": ["accuracy"]
}

# eval_config (from test case)
{
    "threshold": 0.9,
    "temperature": 0.1
}

# Merged result
{
    "threshold": 0.9,      # Overridden
    "model": "gemini-flash",  # Preserved
    "criteria": ["accuracy"],  # Preserved
    "temperature": 0.1     # Added
}
```

## Benefits

✅ **Reusable evaluators** - One evaluator instance can handle different requirements
✅ **Flexible testing** - Each test case can have unique evaluation criteria
✅ **Clean configuration** - Global defaults with per-case overrides
✅ **Backward compatible** - Test cases without `evaluator_config` use global config
✅ **Type safe** - Config validation happens per evaluation

## Migration Guide

If you have existing evalset files, they will continue to work without changes. To add per-test-case config:

1. Add `evaluator_config` field to specific test cases in your evalset JSON
2. Only override what you need - other values inherit from global config
3. Test cases without `evaluator_config` use global configuration

No changes needed to existing test cases!
