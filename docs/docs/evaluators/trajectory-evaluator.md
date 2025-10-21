---
sidebar_position: 3
---

# Trajectory Evaluator

Validate conversation flow and tool usage patterns in multi-turn dialogues.

## Overview

The **Trajectory Evaluator** checks whether the agent follows the expected conversation path, including:
- Correct number of conversation turns
- Expected tool usage sequences
- Proper intermediate steps
- Structured dialogue flow

**Key Features:**
- Multi-turn conversation validation
- Tool use sequence matching
- Exact and partial matching modes
- Intermediate step verification

## Configuration

### Basic Configuration

```yaml
evaluators:
  - type: trajectory_evaluator
```

### Full Configuration

```yaml
evaluators:
  - type: trajectory_evaluator
    enabled: true
    config:
      sequence_match_type: exact    # exact or partial
      allow_partial_match: false    # Allow partial tool matches
```

## Matching Modes

### Exact Match (Default)

Requires tool sequences to match exactly:

```yaml
config:
  sequence_match_type: exact
```

**Pass criteria:**
- Same number of tools
- Same tool names
- Same order

**Example:**
```
Expected: [search, calculate, respond]
Actual:   [search, calculate, respond]  ✓ PASS

Actual:   [search, respond]              ✗ FAIL (missing tool)
Actual:   [calculate, search, respond]  ✗ FAIL (wrong order)
```

### Partial Match

Allows some overlap in tool usage:

```yaml
config:
  sequence_match_type: partial
  allow_partial_match: true
```

**Pass criteria:**
- Some tool overlap required
- Order doesn't matter
- Extra tools allowed

**Example:**
```
Expected: [search, calculate]
Actual:   [search, calculate, respond]  ✓ PASS (overlap exists)

Actual:   [respond, summarize]          ✗ FAIL (no overlap)
```

## Usage Examples

### Example 1: Validate Customer Support Flow

```yaml
# config.yaml
dataset:
  loader: local_file
  paths: [./support_flow.json]

providers:
  - type: gemini
    agent_id: support_agent
    model: gemini-2.0-flash-exp

evaluators:
  - type: trajectory_evaluator
    config:
      sequence_match_type: exact

reporters:
  - type: console
```

**Evalset:**
```json
{
  "eval_id": "support_001",
  "conversation": [
    {
      "invocation_id": "inv-1",
      "user_content": {"parts": [{"text": "I need help"}]},
      "intermediate_data": {
        "tool_uses": [
          {"name": "search_kb", "input": {"query": "help"}}
        ]
      },
      "final_response": {"parts": [{"text": "How can I help?"}]}
    },
    {
      "invocation_id": "inv-2",
      "user_content": {"parts": [{"text": "My order is late"}]},
      "intermediate_data": {
        "tool_uses": [
          {"name": "lookup_order", "input": {"order_id": "123"}},
          {"name": "check_shipping", "input": {"tracking": "ABC"}}
        ]
      },
      "final_response": {"parts": [{"text": "Your order will arrive tomorrow"}]}
    }
  ]
}
```

### Example 2: Lenient Tool Matching

```yaml
evaluators:
  - type: trajectory_evaluator
    config:
      sequence_match_type: partial
      allow_partial_match: true
```

Good for exploratory agents that may use different tool combinations.

### Example 3: Per-Case Override

```json
{
  "eval_id": "strict_flow_001",
  "conversation": [...],
  "evaluator_config": {
    "TrajectoryEvaluator": {
      "sequence_match_type": "exact"
    }
  }
},
{
  "eval_id": "flexible_flow_001",
  "conversation": [...],
  "evaluator_config": {
    "TrajectoryEvaluator": {
      "sequence_match_type": "partial"
    }
  }
}
```

## Evaluation Result

The trajectory evaluator returns detailed results:

```python
{
    "evaluator_name": "TrajectoryEvaluator",
    "evaluator_type": "trajectory_evaluator",
    "passed": True,
    "score": 1.0,
    "success": True,
    "details": {
        "sequence_match_type": "exact",
        "allow_partial_match": false,
        "match_rate": 1.0,
        "tool_matches": [
            {
                "invocation": 0,
                "expected_tool_count": 1,
                "actual_tool_count": 1,
                "match": true,
                "expected_tools": ["search_kb"],
                "actual_tools": ["search_kb"]
            },
            {
                "invocation": 1,
                "expected_tool_count": 2,
                "actual_tool_count": 2,
                "match": true,
                "expected_tools": ["lookup_order", "check_shipping"],
                "actual_tools": ["lookup_order", "check_shipping"]
            }
        ]
    }
}
```

## When to Use

### Use Trajectory Evaluator When:

- Testing multi-step workflows
- Validating agent planning
- Checking tool usage patterns
- Ensuring consistent execution paths
- Testing dialogue systems

### Don't Use When:

- Single-turn conversations (no trajectory to validate)
- Tool order doesn't matter
- Only final response quality matters
- Agents should be creative/exploratory

## Best Practices

### 1. Define Clear Expected Paths

Be explicit about expected tool sequences:

```json
{
  "intermediate_data": {
    "tool_uses": [
      {"name": "search", "input": {...}},
      {"name": "filter", "input": {...}},
      {"name": "respond", "input": {...}}
    ]
  }
}
```

### 2. Use Exact Match for Critical Paths

For safety-critical or compliance workflows:

```yaml
config:
  sequence_match_type: exact
```

### 3. Use Partial Match for Exploration

For research/creative tasks:

```yaml
config:
  sequence_match_type: partial
```

### 4. Combine with Response Evaluator

Validate both trajectory and response quality:

```yaml
evaluators:
  - type: trajectory_evaluator
  - type: response_evaluator
```

## Troubleshooting

### All Trajectories Failing

**Issue:** All test cases fail trajectory check

**Solutions:**

1. **Check tool names match exactly:**
   ```json
   Expected: "search_database"
   Actual:   "searchDatabase"  ✗ (case-sensitive)
   ```

2. **Use partial matching if appropriate:**
   ```yaml
   sequence_match_type: partial
   ```

3. **Review intermediate_data structure:**
   Ensure tool_uses array is properly formatted

### Conversation Length Mismatch

**Error:** `conversation_length mismatch`

**Cause:** Different number of turns

**Solution:** Ensure expected and actual conversations have same number of invocations

## Related Documentation

- [Evaluators Overview](./overview)
- [Response Evaluator](./response-evaluator)
- [Custom Evaluators](./custom-evaluators)
- [Evalset Format](../guides/evalset-format)

## API Reference

For implementation details, see the [TrajectoryEvaluator API Reference](../guides/python-api).
