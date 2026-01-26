---
sidebar_position: 5
---

# ADK HTTP Provider

Connect to remote ADK HTTP endpoints for evaluating AI agents deployed as web services.

## Overview

The **ADK HTTP Provider** connects to remote ADK (Agent Development Kit) endpoints that stream responses via Server-Sent Events (SSE). This enables evaluation of agents deployed as HTTP services without requiring local access to the agent code.

**Type:** `adk_http`

**Key Features:**
- SSE streaming response support
- Multiple authentication methods (Bearer, API Key, Basic)
- Automatic token and cost tracking
- Session management
- Agent chain tracking for multi-agent systems
- Retry with exponential backoff
- Async execution support

## Quick Start

### 1. Start Your ADK Agent Server

```bash
# Example: Start ADK agent on port 8000
adk api_server my_agent --port 8000
```

### 2. Configure Provider

```yaml
providers:
  - type: adk_http
    agent_id: my_remote_agent
    endpoint_url: "http://localhost:8000/run"
```

### 3. Run Evaluation

```bash
judge-llm run --config config.yaml
```

## Configuration

### Basic Configuration

```yaml
providers:
  - type: adk_http
    agent_id: my_agent
    endpoint_url: "http://localhost:8000/run"
```

### Full Configuration

```yaml
providers:
  - type: adk_http
    agent_id: my_agent

    # Endpoint (required)
    endpoint_url: "http://localhost:8000/run"

    # Authentication
    auth_type: bearer              # bearer, api_key, basic, none
    api_key: ${ADK_API_KEY}        # Or set ADK_API_KEY env var
    # auth_header: "X-API-Key"     # For api_key auth type
    # username: "user"             # For basic auth
    # password: "pass"             # For basic auth

    # Request settings
    timeout: 60                    # Request timeout in seconds
    retry_attempts: 3              # Number of retry attempts
    retry_delay: 1                 # Base delay between retries
    verify_ssl: true               # SSL certificate verification

    # Session settings
    user_id: "eval_user"           # User ID for sessions
    app_name: "judge-llm"          # App name for sessions

    # Cost calculation
    model: "gemini-2.0-flash"      # Model name for pricing

    # Custom pricing (optional)
    custom_pricing:
      my-custom-model:
        input: 0.10                # $ per 1M input tokens
        output: 0.50               # $ per 1M output tokens
```

## Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `endpoint_url` | string | (required) | ADK endpoint URL |
| `auth_type` | string | `bearer` | Authentication type |
| `api_key` | string | (env var) | API key for auth |
| `auth_header` | string | `X-API-Key` | Header name for api_key auth |
| `username` | string | - | Username for basic auth |
| `password` | string | - | Password for basic auth |
| `timeout` | int | `60` | Request timeout (seconds) |
| `retry_attempts` | int | `3` | Number of retries |
| `retry_delay` | int | `1` | Base retry delay (seconds) |
| `verify_ssl` | bool | `true` | Verify SSL certificates |
| `user_id` | string | `eval_user` | User ID for sessions |
| `app_name` | string | `judge-llm` | App name for sessions |
| `model` | string | `gemini-2.0-flash` | Model for cost calculation |
| `custom_pricing` | object | - | Custom model pricing |

## Authentication

### Bearer Token (Default)

```yaml
auth_type: bearer
api_key: ${ADK_API_KEY}
```

Sends: `Authorization: Bearer <api_key>`

### API Key Header

```yaml
auth_type: api_key
api_key: ${ADK_API_KEY}
auth_header: "X-API-Key"  # Customize header name
```

Sends: `X-API-Key: <api_key>`

### Basic Auth

```yaml
auth_type: basic
username: "user"
password: "pass"
```

Sends: `Authorization: Basic <base64(user:pass)>`

### No Authentication

```yaml
auth_type: none
```

## Usage Examples

### Example 1: Local Development

```yaml
# config.yaml
providers:
  - type: adk_http
    agent_id: dev_agent
    endpoint_url: "http://localhost:8000/run"
    auth_type: none
    timeout: 30

evaluators:
  - type: response_evaluator
```

### Example 2: Production with Auth

```yaml
providers:
  - type: adk_http
    agent_id: prod_agent
    endpoint_url: "https://api.mycompany.com/agent/run"
    auth_type: bearer
    api_key: ${ADK_API_KEY}
    verify_ssl: true
    timeout: 60
    retry_attempts: 3
```

### Example 3: Multi-Agent Evaluation

```yaml
providers:
  - type: adk_http
    agent_id: orchestrator
    endpoint_url: "http://localhost:8000/run"
    app_name: "travel_assistant"
    user_id: "test_user"

evaluators:
  # Validate response quality
  - type: response_evaluator
    config:
      similarity_threshold: 0.7

  # Validate tool usage
  - type: trajectory_evaluator
    config:
      sequence_match_type: flexible

  # Validate agent transfers
  - type: subagent_evaluator
    config:
      sequence_match_type: contains
      min_match_ratio: 0.8
```

### Example 4: Custom Pricing

```yaml
providers:
  - type: adk_http
    agent_id: custom_model_agent
    endpoint_url: "http://localhost:8000/run"
    model: "my-fine-tuned-model"
    custom_pricing:
      my-fine-tuned-model:
        input: 0.15
        output: 0.60
```

## Request/Response Format

### Request Payload

The provider sends requests in this format:

```json
{
  "app_name": "judge-llm",
  "user_id": "eval_user",
  "session_id": "session-uuid",
  "new_message": {
    "role": "user",
    "parts": [{"text": "User message here"}]
  },
  "system_instruction": "Optional system prompt"
}
```

### Response Handling

The provider handles two response formats:

**SSE Streaming:**
```
data: {"content": {"parts": [{"text": "Response"}]}, "author": "agent"}
data: {"actions": {"stateDelta": {"key": "value"}}}
```

**JSON Array:**
```json
[
  {"content": {"parts": [{"text": "Response"}]}, "author": "agent"},
  {"usageMetadata": {"promptTokenCount": 100, "candidatesTokenCount": 50}}
]
```

## Provider Result

The provider returns comprehensive results:

```python
ProviderResult(
    conversation_history=[...],
    cost=0.0012,
    time_taken=1.45,
    token_usage={
        "prompt_tokens": 150,
        "completion_tokens": 75,
        "total_tokens": 225
    },
    metadata={
        "provider": "adk_http",
        "agent_id": "my_agent",
        "model": "gemini-2.0-flash",
        "session_id": "session-uuid",
        "endpoint": "http://localhost:8000/run",
        "event_count": 5,
        "agent_chain": ["router", "search_agent", "response_agent"]
    },
    success=True
)
```

## Session Management

The provider manages sessions automatically:

1. **Session Creation:** Creates a session on the ADK server before first message
2. **State Tracking:** Updates session state from `stateDelta` in responses
3. **Session Cleanup:** Closes sessions after evaluation completes

### Custom Session Settings

```yaml
providers:
  - type: adk_http
    agent_id: my_agent
    endpoint_url: "http://localhost:8000/run"
    app_name: "my_application"
    user_id: "test_user_123"
```

### Per-Case Session Override

```yaml
eval_cases:
  - eval_id: test_001
    session_input:
      app_name: "custom_app"
      user_id: "custom_user"
      state:
        context: "previous_conversation"
```

## Agent Chain Tracking

For multi-agent systems, the provider tracks agent transfers:

```python
# Accessible in provider result metadata
result.metadata["agent_chain"]
# Returns: ["router", "flight_agent", "booking_agent"]
```

Use with the SubAgent Evaluator:

```yaml
evaluators:
  - type: subagent_evaluator
    config:
      sequence_match_type: contains
```

## Error Handling

### Retry Logic

The provider implements exponential backoff:

```yaml
retry_attempts: 3
retry_delay: 1  # seconds
```

Retry schedule: 1s, 2s, 4s (exponential)

### Error Result

On failure, the provider returns:

```python
ProviderResult(
    conversation_history=[],
    success=False,
    error="Connection refused",
    metadata={
        "provider": "adk_http",
        "error": "Connection refused"
    }
)
```

## Complete Example

### Directory Structure

```
my_project/
├── config.yaml
├── evalset.yaml
└── .env
```

### Configuration

```yaml
# config.yaml
agent:
  name: adk_http_test
  num_runs: 1

dataset:
  loader: local_file
  paths: [./evalset.yaml]

providers:
  - type: adk_http
    agent_id: travel_agent
    endpoint_url: "http://localhost:8000/run"
    auth_type: bearer
    timeout: 60
    app_name: "travel_assistant"
    model: "gemini-2.0-flash"

evaluators:
  - type: response_evaluator
    config:
      similarity_threshold: 0.7

  - type: trajectory_evaluator
    config:
      sequence_match_type: flexible

  - type: subagent_evaluator
    config:
      sequence_match_type: contains

reporters:
  - type: console
  - type: html
    output_path: "./report.html"
```

### Environment Variables

```bash
# .env
ADK_API_KEY=your-api-key-here
```

### Evalset

```yaml
# evalset.yaml
eval_set_id: adk_http_test
name: ADK HTTP Agent Test
eval_cases:
  - eval_id: flight_booking_001
    session_input:
      app_name: "travel_assistant"
      user_id: "test_user"
    conversation:
      - invocation_id: turn_1
        user_content:
          parts:
            - text: "Find flights to Paris next week"
        intermediate_data:
          tool_uses:
            - tool_name: "search_flights"
              input_data: '{"destination": "Paris"}'
        final_response:
          parts:
            - text: "I found several flights to Paris"
```

## Troubleshooting

### Connection Refused

**Issue:** Cannot connect to endpoint

**Solutions:**
```bash
# Verify server is running
curl http://localhost:8000/health

# Check endpoint URL in config
endpoint_url: "http://localhost:8000/run"
```

### Authentication Errors

**Issue:** 401 Unauthorized

**Solutions:**
```bash
# Verify API key is set
echo $ADK_API_KEY

# Check auth_type matches server expectations
auth_type: bearer  # or api_key, basic
```

### Timeout Errors

**Issue:** Request timeout

**Solutions:**
```yaml
# Increase timeout
timeout: 120

# Check server response time
curl -w "%{time_total}" http://localhost:8000/run
```

### SSL Errors

**Issue:** SSL certificate verification failed

**Solutions:**
```yaml
# For development only
verify_ssl: false

# For production, use valid certificates
verify_ssl: true
```

### Missing httpx Package

**Issue:** "httpx is required"

**Solution:**
```bash
pip install httpx
```

## Related Documentation

- [Providers Overview](./overview)
- [Google ADK Provider](./google-adk-provider) - Local ADK agents
- [SubAgent Evaluator](../evaluators/subagent-evaluator) - Multi-agent validation
- [Trajectory Evaluator](../evaluators/trajectory-evaluator) - Tool validation
