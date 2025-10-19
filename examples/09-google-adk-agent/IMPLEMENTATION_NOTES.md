# ADK Provider Implementation Notes

This document explains how the Google ADK provider works and important implementation details.

## Architecture

### Provider Design

The `GoogleADKProvider` integrates Google's Agent Development Kit with the Judge LLM framework:

```
Framework (sync)  →  ADK Provider  →  ADK (async)  →  Gemini API
                      ↓
                 asyncio.run()
```

### Key Components

1. **Async Handling**
   - Framework calls `execute()` synchronously for each eval case
   - ADK uses async/await internally
   - We use `asyncio.run()` to bridge sync/async boundary
   - Each eval case gets its own event loop (independent execution)

2. **Agent Caching**
   - Agent loaded once and cached per provider instance
   - Reused across all eval cases for efficiency
   - Module import happens lazily on first use

3. **Session Management**
   - `InMemorySessionService` and `InMemoryArtifactService` are instance variables
   - Persist across all eval cases
   - Each case gets unique session ID for isolation

4. **Model Conversion**
   - Bidirectional conversion between framework and ADK models
   - Framework `Invocation` ↔ ADK `Invocation`
   - Framework `Content` ↔ ADK `Content` (google.genai.types)
   - Framework `ToolUse` ↔ ADK `FunctionCall`

## Important Implementation Details

### Multiple execute() Calls

The provider correctly handles being called multiple times:

```python
# Each call:
1. Reuses cached agent (if already loaded)
2. Creates new event loop via asyncio.run()
3. Gets unique session ID
4. Runs inference independently
5. Returns ProviderResult
```

This is **safe and correct** because:
- Each eval case is independent (no shared state needed between cases)
- Session/artifact services persist (in case state sharing is needed)
- Agent is reused (efficiency)
- Fresh event loop prevents async context pollution

### Warning Suppression

ADK warns about default values in Python function parameters:
```
WARNING: Default value is not supported in function declaration schema for Google AI.
```

This is expected when using Python functions with default parameters as tools. The provider suppresses this warning in `__init__`:

```python
logging.getLogger('google_adk.google.adk.tools._function_parameter_parse_util').setLevel(logging.ERROR)
```

### Error Handling

Errors are caught and returned in `ProviderResult`:
- `success=False`
- `error` contains error message
- Framework handles evaluation failure appropriately

### Async Resource Cleanup

You may see warnings about unclosed connectors:
```
Unclosed client session
Unclosed connector
```

These are from aiohttp's HTTP connection pool. They're harmless warnings about cleanup and don't affect functionality. They appear because `asyncio.run()` creates and tears down event loops.

## Configuration

### Required Agent Metadata

```yaml
agent_metadata:
  module_path: "tool_agent.agent"  # Required: Python module path
  agent_name: "root_agent"         # Optional: Agent variable (default: "root_agent")
  root_path: "."                   # Optional: Path to add to sys.path
  module_prefix: "examples"        # Optional: Module prefix
  agent_submodule: "agent"         # Optional: Submodule name (default: "agent")
```

### Agent Requirements

The agent must be an `LlmAgent` (not just `BaseAgent`):
```python
from google.adk.agents import Agent

root_agent = Agent(
    name="my_agent",
    model="gemini-2.0-flash",
    instruction="...",
    tools=[...]
)
```

## Performance Characteristics

- **Agent Loading**: ~100-200ms (first eval case only, then cached)
- **Per-Case Overhead**: ~10-20ms (event loop creation)
- **Memory**: Agent cached in memory, services persistent
- **Concurrency**: Safe for sequential execution (framework default)

## Future Improvements

Potential optimizations if needed:
1. Shared event loop with thread pool (if hundreds of cases)
2. HTTP connection pooling configuration
3. Explicit async context manager for session/artifact services
4. Batch processing of multiple cases in single event loop

Currently, the simple approach with `asyncio.run()` is correct and performs well for typical use cases.

## Debugging Tips

1. **"coroutine not iterable"**: Check that `asyncio.run()` is used for all async ADK calls
2. **"got multiple values for keyword argument"**: Check that `agent_metadata` isn't in both places
3. **"not a Google ADK LlmAgent"**: Ensure agent uses `Agent()` class, not custom `BaseAgent`
4. **"Cannot import module"**: Verify `root_path` and `module_path` are correct

## Testing

Run the test script to verify setup:
```bash
python test_provider.py
```

This tests:
- Provider instantiation
- Agent loading
- Model conversion
- Execution flow (with fake API key)
