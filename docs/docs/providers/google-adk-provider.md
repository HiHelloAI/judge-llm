---
sidebar_position: 4
---

# Google ADK Provider

The Google ADK Provider integrates Google's Agent Development Kit, enabling evaluation of AI agents with tool calling, multi-turn conversations, and complex workflows.

## Overview

**Type:** `google_adk`

**Purpose:** Evaluate AI agents built with Google's Agent Development Kit (ADK).

**Key Features:**
- ✅ Tool calling / function execution
- ✅ Async agent execution
- ✅ Multi-turn conversations with state
- ✅ Session management
- ✅ Thread-safe agent caching
- ✅ Cost and token tracking

## Quick Start

### 1. Install Google ADK

```bash
pip install google-genai
```

### 2. Create ADK Agent

```python
# tool_agent/agent.py
from google import genai
from google.genai import types

# Define tools
def get_weather(city: str) -> str:
    """Get weather for a city."""
    return f"Weather in {city}: Sunny, 72°F"

# Create agent
root_agent = types.Agent(
    name="weather_agent",
    model="gemini-2.0-flash-exp",
    tools=[get_weather],
)
```

### 3. Configure Provider

```yaml
providers:
  - type: google_adk
    agent_id: adk_weather_agent
    agent_metadata:
      module_path: "tool_agent.agent"
      agent_name: "root_agent"
      root_path: "."
```

### 4. Run Evaluation

```bash
GOOGLE_API_KEY=your-key judge-llm run --config config.yaml
```

## Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `type` | string | - | Must be `google_adk` |
| `agent_id` | string | - | Unique identifier |
| `agent_metadata.module_path` | string | - | Python module path (e.g., "my_agent.agent") |
| `agent_metadata.agent_name` | string | `root_agent` | Agent variable name in module |
| `agent_metadata.root_path` | string | `.` | Root directory for imports |

## Agent Metadata

### module_path

Python import path to your agent module:

```yaml
# For tool_agent/agent.py
agent_metadata:
  module_path: "tool_agent.agent"

# For src/agents/my_agent.py
agent_metadata:
  module_path: "src.agents.my_agent"
```

### agent_name

Variable name of the agent in the module:

```python
# agent.py
root_agent = types.Agent(...)  # ← agent_name: "root_agent"
my_custom_agent = types.Agent(...)  # ← agent_name: "my_custom_agent"
```

### root_path

Base directory for module imports:

```yaml
# If agent is in current directory
agent_metadata:
  root_path: "."

# If agent is in parent directory
agent_metadata:
  root_path: ".."
```

## Complete Example

### Directory Structure

```
my_project/
├── tool_agent/
│   └── agent.py
├── evalset.yaml
└── config.yaml
```

### Agent Implementation

```python
# tool_agent/agent.py
from google import genai
from google.genai import types

def search_docs(query: str) -> str:
    """Search documentation."""
    return f"Documentation for: {query}"

def calculate(expression: str) -> float:
    """Evaluate math expression."""
    return eval(expression)

root_agent = types.Agent(
    name="helpful_agent",
    model="gemini-2.0-flash-exp",
    tools=[search_docs, calculate],
    instructions="You are a helpful assistant with access to tools."
)
```

### Configuration

```yaml
# config.yaml
agent:
  num_runs: 1

dataset:
  loader: local_file
  paths: [./evalset.yaml]

providers:
  - type: google_adk
    agent_id: adk_tool_agent
    agent_metadata:
      module_path: "tool_agent.agent"
      agent_name: "root_agent"
      root_path: "."

evaluators:
  - type: response_evaluator
  - type: trajectory_evaluator  # Validates tool calls
```

### Test Cases

```yaml
# evalset.yaml
eval_set_id: adk_test
name: ADK Tool Agent Test
eval_cases:
  - eval_id: tool_test
    session_input:
      app_name: "tool_test"
      user_id: "user1"
    conversation:
      - invocation_id: turn_1
        user_content:
          parts:
            - text: "What is 25 * 4?"
        final_response:
          parts:
            - text: "100"
        intermediate_data:
          tool_uses:
            - tool_name: "calculate"
              input_data: '{"expression": "25 * 4"}'
```

## Tool Calling

ADK agents can call tools/functions:

### Example with Tools

```python
def get_user_info(user_id: str) -> dict:
    """Get user information."""
    return {"user_id": user_id, "name": "John", "age": 30}

root_agent = types.Agent(
    model="gemini-2.0-flash-exp",
    tools=[get_user_info]
)
```

### Validating Tool Calls

Use the Trajectory Evaluator to validate tool usage:

```yaml
evaluators:
  - type: trajectory_evaluator
    config:
      allow_partial_match: false
```

## Session Management

ADK maintains session state across turns:

```yaml
eval_cases:
  - eval_id: stateful_conversation
    session_input:
      app_name: "my_app"
      user_id: "user123"
      session_state:  # Custom session state
        context: "previous_conversation"
```

## Performance Optimization

### Thread-Safe Caching

The provider caches the agent instance (loaded once, reused):

```yaml
agent:
  parallel_execution: true
  max_workers: 4  # Agent loaded once, shared across workers
```

### Async Execution

ADK agents run asynchronously under the hood:

```python
# Framework handles async execution automatically
# No need for custom async code
```

## Error Handling

```python
report = evaluate(config="config.yaml")

for run in report.execution_runs:
    if not run.provider_result.success:
        print(f"Error: {run.provider_result.error}")
```

## Complete Working Example

See the `examples/09-google-adk-agent` directory for a complete working example:

```bash
cd examples/09-google-adk-agent
GOOGLE_API_KEY=your-key python run_evaluation.py
```

## Troubleshooting

### Module Not Found

```bash
# Ensure module path is correct
python -c "from tool_agent.agent import root_agent; print(root_agent)"
```

### Agent Not Found

```yaml
# Check agent_name matches variable name in module
agent_metadata:
  agent_name: "root_agent"  # Must match: root_agent = types.Agent(...)
```

### API Key Issues

```bash
# Verify API key is set
echo $GOOGLE_API_KEY

# Or set in .env
GOOGLE_API_KEY=your-key-here
```

## Related Documentation

- [Providers Overview](./overview)
- [Google ADK Documentation](https://github.com/google-gemini/agent-developer-kit)
- [Trajectory Evaluator](../evaluators/trajectory-evaluator) - Validate tool calls
- [Examples](../examples/overview)

## Next Steps

- Implement [Custom Providers](./custom-providers) for other frameworks
- Use [Trajectory Evaluator](../evaluators/trajectory-evaluator) to validate agents
- See working example in `examples/09-google-adk-agent`
