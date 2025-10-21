# Example 09: Google ADK Agent

This example demonstrates how to use the **Google ADK (Agent Development Kit) Provider** with Judge LLM to evaluate agents built with Google's ADK framework.

## Overview

The Google ADK provider allows you to test and evaluate agents built with Google's Agent Development Kit without modifying your agent code. The provider:
- Loads your ADK agent from a Python module
- Converts between Judge LLM's format and ADK's format automatically
- Runs evaluations using ADK's evaluation infrastructure
- Reports results in Judge LLM's standard format

## Agent Structure

This example includes a tool-using agent with multiple capabilities:

**Agent:** `tool_agent/agent.py`
- Built with Google ADK's `Agent` class (LlmAgent)
- Has 5 tools:
  - `get_weather()` - Get weather for a location
  - `calculator()` - Perform mathematical calculations
  - `google_search()` - Search the web
  - `get_current_time()` - Get current timestamp
  - `format_as_news_card()` - Format text as a news card

## Configuration

The `config.yaml` file shows how to configure the ADK provider:

```yaml
providers:
  - type: google_adk
    agent_id: adk_tool_agent
    agent_metadata:
      module_path: "tool_agent.agent"  # Path to agent module
      agent_name: "root_agent"         # Agent variable name
      root_path: "."                   # Root path for imports
```

### Agent Metadata Fields

- **module_path** (required): Python module path to your agent (e.g., "tool_agent.agent")
- **agent_name** (default: "root_agent"): Variable name of the agent in the module
- **root_path** (optional): Path to add to sys.path before importing
- **module_prefix** (optional): Prefix to prepend to module path
- **agent_submodule** (default: "agent"): Submodule name if agent is nested

## Prerequisites

1. **Set up your environment:**
   ```bash
   export GOOGLE_API_KEY="your-api-key-here"
   ```

2. **Install dependencies:**
   ```bash
   pip install google-adk python-dotenv
   ```

## Running the Example

### Option 1: Using the CLI

```bash
cd examples/09-google-adk-agent
judge-llm run --config config.yaml
```

### Option 2: Using the run script

```bash
cd examples/09-google-adk-agent
chmod +x run.sh
./run.sh
```

### Option 3: Using Python directly

```bash
cd examples/09-google-adk-agent
python run_evaluation.py
```

## Test Cases

The `sample.evalset.yaml` includes 5 test cases:

1. **weather_query**: Single-turn weather lookup
2. **calculator_basic**: Basic math operation
3. **multi_turn_weather_and_calc**: Multi-turn conversation with different tools
4. **current_time**: Time lookup with flexible matching
5. **weather_celsius**: Weather with unit conversion

## Expected Results

The evaluation will:
- Load the ADK agent from the module
- Run each test case through the agent
- Evaluate responses using semantic matching
- Check that correct tools were called
- Generate reports in console, JSON, and HTML formats

## Key Features Demonstrated

1. **ADK Agent Loading**: Loading agents from Python modules
2. **Tool Usage Validation**: Verifying correct tools are called
3. **Multi-turn Conversations**: Testing stateful interactions
4. **Flexible Evaluation**: Using per-case evaluator configs
5. **Format Conversion**: Automatic conversion between frameworks
6. **Clean Output**: ADK warnings about default values are suppressed for cleaner logs

## Output

Results are saved to:
- `../../reports/09-google-adk-agent/adk_report.json`
- `../../reports/09-google-adk-agent/adk_report.html`

## Customizing Your Agent

To use your own ADK agent:

1. Create your agent module with an LlmAgent instance
2. Update `config.yaml` with your agent's module path
3. Create eval cases matching your agent's capabilities
4. Run the evaluation

Example:
```python
# my_agent/agent.py
from google.adk.agents import Agent

root_agent = Agent(
    name="my_agent",
    model="gemini-2.0-flash",
    instruction="Your instructions here",
    tools=[...]
)
```

Then in config.yaml:
```yaml
agent_metadata:
  module_path: "my_agent.agent"
  agent_name: "root_agent"
  root_path: "."
```

## Troubleshooting

**Error: "Agent 'root_agent' not found in module"**
- Check that your agent variable name matches `agent_name` in config
- Verify the module path is correct

**Error: "is not a Google ADK LlmAgent"**
- Ensure your agent is created with `Agent()` class from google.adk.agents
- Check that you're using LlmAgent, not just BaseAgent

**Error: "Cannot import module"**
- Verify `root_path` is set correctly
- Check that `module_path` points to a valid Python module
- Ensure all dependencies are installed

## Learn More

- [Google ADK Documentation](https://ai.google.dev/adk)
- [Judge LLM Documentation](../../docs)
- [Provider Configuration Guide](../../docs/providers.md)
