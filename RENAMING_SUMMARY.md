# Evaluator Naming Consistency Fix

## Summary

Fixed naming inconsistency where evaluators were called "Validators" instead of "Evaluators" to match the consistent naming convention.

## Changes Made

### 1. File Renames

| Old Name | New Name |
|----------|----------|
| `response_validator.py` | `response_evaluator.py` |
| `trajectory_validator.py` | `trajectory_evaluator.py` |

### 2. Class Renames

| Old Class Name | New Class Name |
|----------------|----------------|
| `ResponseValidator` | `ResponseEvaluator` |
| `TrajectoryValidator` | `TrajectoryEvaluator` |

### 3. Type Registration Updates

**In `judge_llm/evaluators/__init__.py`:**

| Old Type | New Type |
|----------|----------|
| `response_validator` | `response_evaluator` |
| `trajectory_validator` | `trajectory_evaluator` |

### 4. Config File Updates

All example config.yaml files updated:

```yaml
# OLD
evaluators:
  - type: response_validator
  - type: trajectory_validator

# NEW
evaluators:
  - type: response_evaluator
  - type: trajectory_evaluator
```

### 5. Evalset File Updates

All `evaluator_config` references updated:

```json
{
  "evaluator_config": {
    "ResponseEvaluator": {...},
    "TrajectoryEvaluator": {...}
  }
}
```

## Naming Convention Now Consistent

| Evaluator | File | Class | Type (in config.yaml) | Class Name (in evalset evaluator_config) |
|-----------|------|-------|------------|------------------------------------------|
| Response | `response_evaluator.py` | `ResponseEvaluator` | `response_evaluator` | `ResponseEvaluator` |
| Trajectory | `trajectory_evaluator.py` | `TrajectoryEvaluator` | `trajectory_evaluator` | `TrajectoryEvaluator` |
| Cost | `cost_evaluator.py` | `CostEvaluator` | `cost_evaluator` | `CostEvaluator` |
| Latency | `latency_evaluator.py` | `LatencyEvaluator` | `latency_evaluator` | `LatencyEvaluator` |

## Files Updated

### Core Files
- ✅ `judge_llm/evaluators/response_evaluator.py` (renamed + class name + log messages)
- ✅ `judge_llm/evaluators/trajectory_evaluator.py` (renamed + class name + log messages)
- ✅ `judge_llm/evaluators/__init__.py` (imports + registrations)
- ✅ `judge_llm/core/evaluate.py` (docstring examples)
- ✅ `judge_llm/cli.py` (CLI default evaluators)

### Example Configs
- ✅ `examples/01-gemini-agent/config.yaml`
- ✅ `examples/01-gemini-agent/run_evaluation.py`
- ✅ `examples/02-default-config/config.yaml`
- ✅ `examples/02-default-config/run_evaluation.py`
- ✅ `examples/04-safety-long-conversation/config.yaml`
- ✅ `examples/04-safety-long-conversation/run_evaluation.py`
- ✅ `examples/05-evaluator-config-override/config.yaml`
- ✅ `examples/05-evaluator-config-override/test_cases.evalset.json`

### Default Configuration
- ✅ `.judge_llm.defaults.yaml`

### Documentation
- ✅ `README.md`
- ✅ `EVALUATOR_CONFIG_GUIDE.md`
- ✅ `EVALUATOR_CONFIG_STATUS.md`
- ✅ `examples/*/README.md`

## Migration Guide

If you have existing code using the old names:

### In Python Code

```python
# OLD
from judge_llm.evaluators import ResponseValidator, TrajectoryValidator

# NEW
from judge_llm.evaluators import ResponseEvaluator, TrajectoryEvaluator
```

### In config.yaml

```yaml
# OLD
evaluators:
  - type: response_validator
  - type: trajectory_validator

# NEW
evaluators:
  - type: response_evaluator
  - type: trajectory_evaluator
```

### In evalset.json (evaluator_config)

```json
{
  "evaluator_config": {
    "ResponseEvaluator": {...},
    "TrajectoryEvaluator": {...}
  }
}
```

## Backwards Compatibility

⚠️ **Breaking Change**: The old names (`response_validator`, `trajectory_validator`) are no longer registered and will not work.

Users must update:
1. Config files (`type: response_evaluator`)
2. Evalset files (`"ResponseEvaluator"` in evaluator_config)
3. Python imports (if importing directly)

## Verification

All changes verified:
- ✅ Files renamed
- ✅ Classes renamed
- ✅ Registrations updated
- ✅ All config files updated
- ✅ All evalset files updated
- ✅ All documentation updated

## Why This Change?

Consistency with naming convention:
- All other evaluators use `*Evaluator` naming
- "Validator" is a subset of "Evaluator" - evaluators can do more than just validate
- Maintains consistency across the codebase
