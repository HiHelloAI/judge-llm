---
sidebar_position: 6
---

# Evaluator Config Override

Master per-test-case configuration overrides to fine-tune evaluation criteria for different scenarios.

## Overview

**Location:** `examples/05-evaluator-config-override/`

**Difficulty:** Intermediate

**What You'll Learn:**
- Two-level configuration system (global + per-test)
- Overriding evaluator settings per test case
- Configuration merging behavior
- Use cases for different override strategies

## The Problem

Different tests have different requirements:

- **Exact commands**: "Say 'Hello World'" needs 100% match
- **Creative content**: Essay writing allows variation
- **Simple queries**: Should be fast (&lt;5s)
- **Complex analysis**: Needs more time and cost budget

One global configuration can't handle all scenarios!

## Solution: Two-Level Configuration

1. **Global Config** (`config.yaml`) - Defaults for all tests
2. **Per-Test Config** (`evalset.json` → `evaluator_config`) - Override for specific tests

Per-test settings **override** global settings with deep merging.

## Files

```
05-evaluator-config-override/
├── config.yaml              # Global defaults
├── test_cases.evalset.json  # Tests with overrides
├── run.sh                   # Runner script
├── run_evaluation.py        # Python runner
└── README.md                # Instructions
```

## Global Configuration

`config.yaml` sets defaults for **all** tests:

```yaml
evaluators:
  - type: response_evaluator
    enabled: true
    config:
      similarity_threshold: 0.6    # Default: 60% similarity
      match_type: semantic          # Default: semantic matching
      case_sensitive: false         # Default: ignore case
      normalize_whitespace: true

  - type: latency_evaluator
    enabled: true
    config:
      max_latency_seconds: 30      # Default: max 30 seconds
      warn_threshold_seconds: 10

  - type: cost_evaluator
    enabled: true
    config:
      max_cost_per_case: 0.10      # Default: max $0.10
```

## Per-Test Overrides

### Test 1: Uses Global Defaults

```json
{
  "eval_id": "test_001_uses_defaults",
  "conversation": [...],
  // NO evaluator_config field
  // Uses all global defaults
}
```

**Effective Config:**
- Threshold: 0.6 (from global)
- Match type: semantic (from global)
- Max latency: 30s (from global)
- Max cost: $0.10 (from global)

---

### Test 2: Strict Exact Match

```json
{
  "eval_id": "test_002_strict_exact_match",
  "conversation": [...],
  "evaluator_config": {
    "ResponseEvaluator": {
      "match_type": "exact",
      "similarity_threshold": 1.0,
      "case_sensitive": true,
      "normalize_whitespace": false
    }
  }
}
```

**Effective Config:**
- ✅ Threshold: **1.0** (overridden - requires 100% match)
- ✅ Match type: **exact** (overridden)
- ✅ Case sensitive: **true** (overridden)
- ❌ Max latency: 30s (inherited from global)

**Use Case:** Commands that must be exact: "Say 'Hello World'"

---

### Test 3: Lenient Creative Content

```json
{
  "eval_id": "test_003_lenient_creative",
  "conversation": [...],
  "evaluator_config": {
    "ResponseEvaluator": {
      "match_type": "recall",
      "similarity_threshold": 0.3
    }
  }
}
```

**Effective Config:**
- ✅ Threshold: **0.3** (overridden - only 30% match needed)
- ✅ Match type: **recall** (overridden - doesn't penalize extra content)
- ❌ Case sensitive: false (inherited)

**Use Case:** Creative writing, essays, brainstorming

---

### Test 4: High Precision Factual

```json
{
  "eval_id": "test_004_high_precision_factual",
  "conversation": [...],
  "evaluator_config": {
    "ResponseEvaluator": {
      "match_type": "rouge",
      "similarity_threshold": 0.85
    }
  }
}
```

**Effective Config:**
- ✅ Threshold: **0.85** (overridden - high precision)
- ✅ Match type: **rouge** (overridden - ROUGE-1 metric)

**Use Case:** Factual Q&A, knowledge retrieval

---

### Test 5: Override Multiple Evaluators

```json
{
  "eval_id": "test_005_fast_latency_required",
  "conversation": [...],
  "evaluator_config": {
    "LatencyEvaluator": {
      "max_latency_seconds": 5,
      "warn_threshold_seconds": 2
    },
    "ResponseEvaluator": {
      "match_type": "exact",
      "similarity_threshold": 1.0
    }
  }
}
```

**Effective Config:**
- ✅ Max latency: **5s** (overridden from 30s)
- ✅ Warn threshold: **2s** (overridden from 10s)
- ✅ Match type: **exact** (overridden)
- ✅ Threshold: **1.0** (overridden)

**Use Case:** Simple queries requiring fast, exact responses

---

### Test 6: Complex Operation

```json
{
  "eval_id": "test_006_expensive_operation_allowed",
  "conversation": [...],
  "evaluator_config": {
    "CostEvaluator": {
      "max_cost_per_case": 0.50
    },
    "LatencyEvaluator": {
      "max_latency_seconds": 120,
      "warn_threshold_seconds": 60
    }
  }
}
```

**Effective Config:**
- ✅ Max cost: **$0.50** (overridden from $0.10)
- ✅ Max latency: **120s** (overridden from 30s)

**Use Case:** Complex analysis, research tasks, code generation

## How Configuration Merging Works

### Merge Algorithm

```python
def get_config(self, eval_config: Optional[Dict] = None) -> Dict:
    if eval_config is None:
        return self.config.copy()  # Use global only

    # Deep merge: per-test overrides global
    merged = self.config.copy()
    merged.update(eval_config)  # Per-test wins
    return merged
```

### Merge Example

**Global:**
```python
{
  "similarity_threshold": 0.6,
  "match_type": "semantic",
  "case_sensitive": false,
  "normalize_whitespace": true
}
```

**Per-Test:**
```python
{
  "match_type": "exact",
  "similarity_threshold": 1.0
}
```

**Merged Result:**
```python
{
  "similarity_threshold": 1.0,     # ✅ Overridden
  "match_type": "exact",            # ✅ Overridden
  "case_sensitive": false,          # ❌ Inherited from global
  "normalize_whitespace": true      # ❌ Inherited from global
}
```

## Important: Evaluator Name vs Type

**In global config (YAML):**
```yaml
evaluators:
  - type: response_evaluator  # Use type name
```

**In per-test override (JSON):**
```json
{
  "evaluator_config": {
    "ResponseEvaluator": {  // Use class name!
      "similarity_threshold": 0.9
    }
  }
}
```

**Evaluator Name Mapping:**
- `type: response_evaluator` → `ResponseEvaluator`
- `type: cost_evaluator` → `CostEvaluator`
- `type: latency_evaluator` → `LatencyEvaluator`
- `type: trajectory_evaluator` → `TrajectoryEvaluator`
- Custom evaluators → Use your class name

## Running the Example

```bash
cd examples/05-evaluator-config-override
judge-llm run --config config.yaml
```

## Expected Output

```
Starting evaluation...

test_001_uses_defaults:
  ResponseEvaluator: threshold=0.6, match_type=semantic (global defaults)
  ✓ PASSED

test_002_strict_exact_match:
  ResponseEvaluator: threshold=1.0, match_type=exact (overridden)
  ✓ PASSED

test_003_lenient_creative:
  ResponseEvaluator: threshold=0.3, match_type=recall (overridden)
  ✓ PASSED

test_004_high_precision_factual:
  ResponseEvaluator: threshold=0.85, match_type=rouge (overridden)
  ✓ PASSED

test_005_fast_latency_required:
  ResponseEvaluator: threshold=1.0, match_type=exact (overridden)
  LatencyEvaluator: max=5s (overridden)
  ✓ PASSED

test_006_expensive_operation_allowed:
  CostEvaluator: max=$0.50 (overridden)
  LatencyEvaluator: max=120s (overridden)
  ✓ PASSED

Summary:
  Total: 6
  Passed: 6
  Failed: 0
  Success Rate: 100%
```

## Use Cases by Test Type

| Test Type | Override Strategy | Configuration |
|-----------|------------------|---------------|
| **Exact commands** | 100% match required | `match_type: exact, threshold: 1.0` |
| **Creative content** | Allow variation | `match_type: recall, threshold: 0.3` |
| **Factual Q&A** | High precision | `match_type: rouge, threshold: 0.85` |
| **Simple queries** | Fast response | Low latency limits |
| **Complex tasks** | More resources | Higher cost/latency limits |
| **Safety-critical** | Specific checks | Custom evaluator config |

## Common Override Patterns

### Pattern 1: Strict Validation

```json
{
  "evaluator_config": {
    "ResponseEvaluator": {
      "match_type": "exact",
      "similarity_threshold": 1.0,
      "case_sensitive": true,
      "normalize_whitespace": false
    }
  }
}
```

For: Commands, code snippets, structured output

### Pattern 2: Lenient Validation

```json
{
  "evaluator_config": {
    "ResponseEvaluator": {
      "match_type": "recall",
      "similarity_threshold": 0.3,
      "case_sensitive": false
    }
  }
}
```

For: Essays, creative writing, brainstorming

### Pattern 3: Performance Critical

```json
{
  "evaluator_config": {
    "LatencyEvaluator": {
      "max_latency_seconds": 3,
      "warn_threshold_seconds": 1
    },
    "CostEvaluator": {
      "max_cost_per_case": 0.01
    }
  }
}
```

For: High-volume, real-time applications

### Pattern 4: Complex Analysis

```json
{
  "evaluator_config": {
    "LatencyEvaluator": {
      "max_latency_seconds": 180
    },
    "CostEvaluator": {
      "max_cost_per_case": 1.00
    }
  }
}
```

For: Research, code generation, complex reasoning

### Pattern 5: Safety Critical

```json
{
  "evaluator_config": {
    "SafetyEvaluator": {
      "severity_threshold": "low",
      "allowed_safety_issues": 0,
      "check_pii": true,
      "check_toxicity": true
    }
  }
}
```

For: User-facing, regulated content

## Best Practices

### 1. Set Reasonable Global Defaults

```yaml
# Global config should work for MOST tests
evaluators:
  - type: response_evaluator
    config:
      similarity_threshold: 0.7  # Balanced default
      match_type: semantic       # Flexible matching
```

### 2. Override Only When Necessary

```json
// Good: Only override what's needed
{
  "evaluator_config": {
    "ResponseEvaluator": {
      "similarity_threshold": 0.9
    }
  }
}

// Bad: Duplicating global settings
{
  "evaluator_config": {
    "ResponseEvaluator": {
      "similarity_threshold": 0.9,
      "match_type": "semantic",      // Already in global
      "case_sensitive": false,       // Already in global
      "normalize_whitespace": true   // Already in global
    }
  }
}
```

### 3. Document Why You Override

```json
{
  "eval_id": "strict_command_test",
  "description": "Testing exact command replication - requires 100% match",
  "evaluator_config": {
    "ResponseEvaluator": {
      "match_type": "exact",
      "similarity_threshold": 1.0
    }
  }
}
```

### 4. Group Similar Tests

If many tests share overrides, create separate evalset files:

```
tests/
├── strict_tests.evalset.json       # All use exact matching
├── creative_tests.evalset.json     # All use lenient matching
└── performance_tests.evalset.json  # All have strict latency
```

### 5. Verify Overrides Are Applied

```bash
# Debug mode shows effective configuration
judge-llm run --config test.yaml --verbose --show-config
```

## Debugging

### Show Effective Configuration

```bash
judge-llm run --config config.yaml --show-config
```

Shows merged configuration before running.

### Trace Configuration Sources

```bash
judge-llm run --config config.yaml --trace-config
```

Shows where each value comes from (global vs per-test).

### Common Issues

**Issue:** Override not applied

**Solution:** Check evaluator name (use class name, not type):
```json
{
  "evaluator_config": {
    "ResponseEvaluator": {  // ✅ Correct
      ...
    }
  }
}

{
  "evaluator_config": {
    "response_evaluator": {  // ❌ Wrong
      ...
    }
  }
}
```

## Next Steps

After mastering config overrides:

1. **[Safety Evaluation](./safety-evaluation)** - Complex per-test safety settings
2. **[Database Tracking](./database-tracking)** - Track configuration effectiveness
3. **[Default Config](./default-config)** - Combine defaults with overrides

## Related Documentation

- [Configuration Guide](../guides/configuration)
- [Default Configs](../guides/default-configs)
- [Evalset Format](../guides/evalset-format)
- [Response Evaluator](../evaluators/response-evaluator)
