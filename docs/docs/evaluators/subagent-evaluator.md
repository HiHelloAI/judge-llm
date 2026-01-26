---
sidebar_position: 8
---

# Sub-Agent Evaluator

Evaluate agent transfer chains in multi-agent orchestration systems.

## Overview

The **Sub-Agent Evaluator** tracks which agents were invoked during execution and validates the agent transfer patterns against expected behavior. This is essential for testing multi-agent systems where agents hand off tasks to specialized sub-agents.

**Type:** `subagent_evaluator`

**Key Features:**
- Track agent transfer chains
- Multiple matching modes (exact, subset, contains, flexible)
- Validate agent invocation order
- Support for extra/missing agent detection
- Integration with ADK HTTP provider metadata

## Quick Start

```yaml
evaluators:
  - type: subagent_evaluator
    config:
      sequence_match_type: contains
      min_match_ratio: 0.8
```

## Configuration

### Basic Configuration

```yaml
evaluators:
  - type: subagent_evaluator
```

### Full Configuration

```yaml
evaluators:
  - type: subagent_evaluator
    enabled: true
    config:
      sequence_match_type: contains    # exact, subset, contains, flexible
      allow_extra_agents: true         # Allow agents not in expected list
      min_match_ratio: 0.8             # Minimum match ratio to pass
```

## Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `sequence_match_type` | string | `contains` | How to match agent chains |
| `allow_extra_agents` | bool | `true` | Whether extra agents are allowed |
| `min_match_ratio` | float | `0.8` | Minimum match ratio to pass |

## Matching Modes

### Exact Match

Requires exact order and count of agents:

```yaml
config:
  sequence_match_type: exact
```

**Example:**
```
Expected: [router, search_agent, response_agent]
Actual:   [router, search_agent, response_agent]  ✓ PASS
Actual:   [router, response_agent, search_agent]  ✗ FAIL (wrong order)
Actual:   [router, search_agent]                  ✗ FAIL (missing agent)
```

### Subset Match

Expected agents must appear in actual in order (subsequence):

```yaml
config:
  sequence_match_type: subset
```

**Example:**
```
Expected: [search_agent, response_agent]
Actual:   [router, search_agent, helper, response_agent]  ✓ PASS
Actual:   [response_agent, search_agent]                  ✗ FAIL (wrong order)
```

### Contains Match (Default)

All expected agents must be present (order doesn't matter):

```yaml
config:
  sequence_match_type: contains
```

**Example:**
```
Expected: [search_agent, response_agent]
Actual:   [response_agent, router, search_agent]  ✓ PASS
Actual:   [router, helper]                        ✗ FAIL (missing agents)
```

### Flexible Match

Any overlap counts, with partial credit:

```yaml
config:
  sequence_match_type: flexible
```

**Example:**
```
Expected: [search_agent, response_agent]
Actual:   [search_agent, helper]  → 50% score (1/2 match)
Actual:   [completely_different]  → 0% score
```

## Usage Examples

### Example 1: Validate Multi-Agent Workflow

```yaml
# config.yaml
providers:
  - type: adk_http
    agent_id: orchestrator
    endpoint_url: "http://localhost:8000/run"

evaluators:
  - type: subagent_evaluator
    config:
      sequence_match_type: contains
      min_match_ratio: 0.8
```

**Evalset with expected agent chain:**
```yaml
eval_cases:
  - eval_id: travel_booking_001
    conversation:
      - invocation_id: turn_1
        user_content:
          parts:
            - text: "Book a flight to Paris"
        intermediate_data:
          intermediate_responses:
            - type: agent_transfer
              from_agent: router
              to_agent: flight_search_agent
            - type: agent_transfer
              from_agent: flight_search_agent
              to_agent: booking_agent
        final_response:
          parts:
            - text: "I've booked your flight to Paris"
```

### Example 2: Strict Agent Order

```yaml
evaluators:
  - type: subagent_evaluator
    config:
      sequence_match_type: exact
      allow_extra_agents: false
```

**Use case:** Compliance workflows where agent order matters.

### Example 3: Flexible Agent Discovery

```yaml
evaluators:
  - type: subagent_evaluator
    config:
      sequence_match_type: flexible
      min_match_ratio: 0.5
```

**Use case:** Exploratory agents that may use different paths.

### Example 4: Per-Case Override

```json
{
  "eval_id": "critical_workflow_001",
  "evaluator_config": {
    "SubAgentEvaluator": {
      "sequence_match_type": "exact",
      "allow_extra_agents": false
    }
  }
}
```

## Specifying Expected Agents

### Method 1: Intermediate Responses

```yaml
intermediate_data:
  intermediate_responses:
    - type: agent_transfer
      from_agent: router
      to_agent: search_agent
    - type: agent_transfer
      from_agent: search_agent
      to_agent: response_agent
```

### Method 2: Tool Uses

```yaml
intermediate_data:
  tool_uses:
    - name: transfer_to_agent
      input_data: '{"agent_name": "search_agent"}'
    - name: transfer_to_agent
      input_data: '{"agent_name": "response_agent"}'
```

### Method 3: Agent Name in Responses

```yaml
intermediate_data:
  intermediate_responses:
    - agent_name: search_agent
    - agent_name: response_agent
```

## Evaluation Result

The evaluator returns detailed results:

```python
{
    "evaluator_name": "SubAgentEvaluator",
    "evaluator_type": "subagent_evaluator",
    "passed": True,
    "score": 1.0,
    "threshold": 0.8,
    "success": True,
    "details": {
        "sequence_match_type": "contains",
        "allow_extra_agents": True,
        "min_match_ratio": 0.8,
        "average_score": 1.0,
        "all_expected_agents": ["search_agent", "booking_agent"],
        "all_actual_agents": ["router", "search_agent", "booking_agent"],
        "agents_missing": [],
        "agents_extra": ["router"],
        "invocation_results": [
            {
                "invocation": 0,
                "expected_agents": ["search_agent", "booking_agent"],
                "actual_agents": ["router", "search_agent", "booking_agent"],
                "score": 1.0,
                "match_details": {
                    "all_expected_present": True,
                    "missing_agents": [],
                    "extra_agents": ["router"]
                }
            }
        ]
    }
}
```

## Integration with ADK HTTP Provider

The SubAgent Evaluator works seamlessly with the ADK HTTP Provider, which tracks agent chains in metadata:

```yaml
providers:
  - type: adk_http
    agent_id: multi_agent_system
    endpoint_url: "http://localhost:8000/run"

evaluators:
  - type: subagent_evaluator
    config:
      sequence_match_type: contains
```

The provider automatically extracts agent chain from SSE events and includes it in the result metadata.

## When to Use

### Use Sub-Agent Evaluator When:

- Testing multi-agent orchestration systems
- Validating agent routing logic
- Ensuring correct agent specialization
- Testing agent handoff workflows
- Verifying compliance agent chains

### Don't Use When:

- Single-agent systems
- Agent order is truly irrelevant
- Only final response matters
- No agent transfer occurs

## Best Practices

### 1. Start with Flexible Matching

```yaml
config:
  sequence_match_type: flexible
  min_match_ratio: 0.5
```

Then tighten as you understand patterns.

### 2. Use Contains for Most Cases

```yaml
config:
  sequence_match_type: contains
  allow_extra_agents: true
```

Validates key agents are involved without over-specifying.

### 3. Use Exact for Critical Paths

```yaml
config:
  sequence_match_type: exact
  allow_extra_agents: false
```

For compliance or security-critical workflows.

### 4. Combine with Trajectory Evaluator

```yaml
evaluators:
  - type: subagent_evaluator
    config:
      sequence_match_type: contains
  - type: trajectory_evaluator
    config:
      sequence_match_type: partial
```

Validate both agent transfers AND tool usage.

### 5. Document Expected Agent Flows

```yaml
# Clear expected agent flow in evalset
intermediate_data:
  intermediate_responses:
    # Step 1: Router identifies intent
    - type: agent_transfer
      to_agent: intent_classifier
    # Step 2: Specialized agent handles request
    - type: agent_transfer
      to_agent: booking_agent
```

## Troubleshooting

### No Agents Detected

**Issue:** `actual_agents` is empty

**Causes:**
- Provider doesn't track agent chains
- Agent metadata not in expected format

**Solutions:**
- Use ADK HTTP Provider (tracks agents automatically)
- Add agent transfers to intermediate_data
- Check provider metadata for agent_chain

### All Tests Failing

**Issue:** Every test fails agent validation

**Solutions:**
- Start with `flexible` matching
- Lower `min_match_ratio`
- Check actual vs expected agent names (case-sensitive)
- Use `allow_extra_agents: true`

### Order Mismatches

**Issue:** Agents present but in wrong order

**Solutions:**
```yaml
# If order doesn't matter
sequence_match_type: contains

# If only subsequence matters
sequence_match_type: subset
```

## Related Documentation

- [Evaluators Overview](./overview)
- [Trajectory Evaluator](./trajectory-evaluator) - Tool usage validation
- [ADK HTTP Provider](../providers/adk-http-provider) - Multi-agent support
- [Google ADK Provider](../providers/google-adk-provider)
