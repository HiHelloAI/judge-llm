# Example 05: Evaluator Config Override

This example demonstrates how to use `evaluator_config` in evalset files to override global evaluator settings on a per-test-case basis.

## Concept

**Two-Level Configuration System:**

1. **Global Config** (config.yaml) - Default settings for all tests
2. **Per-Test Config** (evalset.json `evaluator_config`) - Override settings for specific tests

Per-test settings **override** global settings, allowing fine-grained control over how each test is evaluated.

## File Structure

```
05-evaluator-config-override/
├── config.yaml              # Global evaluator defaults
├── test_cases.evalset.json  # Test cases with per-test overrides
└── README.md
```

## Global Configuration (config.yaml)

Sets defaults that apply to **all** test cases:

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

## Per-Test Overrides (evalset.json)

### Test 1: Uses Global Defaults

```json
{
  "eval_id": "test_001_uses_defaults",
  "conversation": [...],
  "session_input": {...}
  // NO evaluator_config field
  // Uses all global defaults: 0.6 threshold, semantic matching
}
```

**Result:**
- Threshold: 0.6 (from global)
- Match type: semantic (from global)
- Max latency: 30s (from global)

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

**Result:**
- ✅ Threshold: **1.0** (overridden - requires 100% match)
- ✅ Match type: **exact** (overridden - must match exactly)
- ✅ Case sensitive: **true** (overridden)
- ❌ Max latency: 30s (still uses global - not overridden)

**Use Case:** Commands that must be reproduced exactly (e.g., "Say 'Hello World'")

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

**Result:**
- ✅ Threshold: **0.3** (overridden - only 30% match needed)
- ✅ Match type: **recall** (overridden - doesn't penalize extra content)
- ❌ Case sensitive: false (still uses global)

**Use Case:** Creative writing where AI can add extra helpful content

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

**Result:**
- ✅ Threshold: **0.85** (overridden - requires 85% precision)
- ✅ Match type: **rouge** (overridden - uses ROUGE-1 metric)

**Use Case:** Factual questions where accuracy is critical

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

**Result:**
- ✅ Max latency: **5s** (overridden from 30s)
- ✅ Warn threshold: **2s** (overridden from 10s)
- ✅ Match type: **exact** (overridden)
- ✅ Threshold: **1.0** (overridden)

**Use Case:** Simple queries that should be fast AND accurate

---

### Test 6: Complex Operation - More Resources

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

**Result:**
- ✅ Max cost: **$0.50** (overridden from $0.10)
- ✅ Max latency: **120s** (overridden from 30s)
- ✅ Warn threshold: **60s** (overridden from 10s)

**Use Case:** Complex analysis that needs more time and tokens

## How Merge Works

The merge happens in `BaseEvaluator.get_config()`:

```python
def get_config(self, eval_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    if eval_config is None:
        return self.config.copy()  # Use global only

    # Merge: per-test overrides global
    merged = self.config.copy()
    merged.update(eval_config)  # Per-test wins
    return merged
```

**Example:**

Global config:
```python
{
  "similarity_threshold": 0.6,
  "match_type": "semantic",
  "case_sensitive": false
}
```

Per-test override:
```python
{
  "match_type": "exact",
  "similarity_threshold": 1.0
}
```

Merged result:
```python
{
  "similarity_threshold": 1.0,     # Overridden
  "match_type": "exact",            # Overridden
  "case_sensitive": false           # Inherited from global
}
```

## Running the Example

```bash
cd examples/05-evaluator-config-override
python -m judge_llm.cli evaluate --config config.yaml
```

## Expected Output

```
test_001_uses_defaults:
  ResponseEvaluator: threshold=0.6, match_type=semantic  (global defaults)

test_002_strict_exact_match:
  ResponseEvaluator: threshold=1.0, match_type=exact  (overridden)

test_003_lenient_creative:
  ResponseEvaluator: threshold=0.3, match_type=recall  (overridden)

test_004_high_precision_factual:
  ResponseEvaluator: threshold=0.85, match_type=rouge  (overridden)

test_005_fast_latency_required:
  ResponseEvaluator: threshold=1.0, match_type=exact  (overridden)
  LatencyEvaluator: max=5s  (overridden)

test_006_expensive_operation_allowed:
  CostEvaluator: max=$0.50  (overridden)
  LatencyEvaluator: max=120s  (overridden)
```

## Key Takeaways

1. **Evaluator name matters**: Use class name `"ResponseEvaluator"`, not type `"response_evaluator"`

2. **Partial overrides work**: You don't need to specify all settings, only what you want to change

3. **Multiple evaluators**: You can override settings for multiple evaluators in one test

4. **No code changes**: All configuration is declarative in YAML/JSON

5. **Inheritance**: Unspecified settings inherit from global config

## Use Cases

| Test Type | Override Strategy |
|-----------|------------------|
| Exact commands | `match_type: exact, threshold: 1.0` |
| Creative content | `match_type: recall, threshold: 0.3` |
| Factual Q&A | `match_type: rouge, threshold: 0.85` |
| Simple queries | Low latency limits |
| Complex operations | Higher cost/latency limits |
| Safety-critical | Enable specific safety checks |

## Best Practices

1. **Set reasonable global defaults** that work for most tests
2. **Override only when necessary** - don't duplicate global settings
3. **Document why** you're overriding (in comments in JSON)
4. **Group similar tests** in separate evalset files if they share overrides
5. **Test both ways** - verify overrides are actually applied

## Related Examples

- [Example 01](../01-gemini-agent/) - Basic Gemini integration
- [Example 04](../04-safety-long-conversation/) - Safety evaluator with per-test config
- [EVALUATOR_CONFIG_GUIDE.md](../../EVALUATOR_CONFIG_GUIDE.md) - Complete reference
