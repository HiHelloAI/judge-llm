# Gemini Provider Example

This example demonstrates how to use the Gemini provider with Judge LLM to evaluate Google's Gemini models.

## Prerequisites

1. **Install Judge LLM with Gemini support:**
   ```bash
   pip install -e ".[gemini]"
   ```

2. **Get a Gemini API key:**
   - Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a new API key
   - Set it as an environment variable:
     ```bash
     export GEMINI_API_KEY="your-api-key-here"
     ```

## Configuration

The [config.yaml](config.yaml) file demonstrates:

- **Gemini Provider Configuration:**
  - Model selection (gemini-2.0-flash-exp)
  - Temperature, max_tokens, top_p, top_k settings
  - API key from environment variable

- **Evaluation Setup:**
  - Response validation with semantic matching
  - Trajectory validation
  - Cost tracking for Gemini API usage
  - Latency monitoring

- **Multi-format Reporting:**
  - Console output with Rich formatting
  - JSON report for programmatic analysis
  - HTML dashboard for interactive exploration

## Running the Example

### Using CLI:

```bash
# Navigate to the example directory
cd examples/gemini

# Run evaluation with Gemini provider
judge-llm run --config config.yaml
```

### Using Python API:

```python
import os
from judge_llm import evaluate

# Make sure API key is set
os.environ["GEMINI_API_KEY"] = "your-api-key-here"

# Run evaluation
result = evaluate(config="examples/gemini/config.yaml")

print(f"Total runs: {result.summary.total_runs}")
print(f"Success rate: {result.summary.success_rate}")
print(f"Total cost: ${result.summary.total_cost:.4f}")
```

## Configuration Options

### Gemini Provider Settings

```yaml
providers:
  - type: gemini
    agent_id: your_agent_id

    # Model configuration
    model: gemini-2.0-flash-exp  # or gemini-1.5-pro, gemini-1.5-flash
    temperature: 0.7              # 0.0 to 2.0
    max_tokens: 2048              # Maximum output tokens
    top_p: 0.95                   # Nucleus sampling
    top_k: 40                     # Top-k sampling

    # API key (prefer environment variable)
    # api_key: "your-key"  # Not recommended for production
```

### Available Gemini Models

- **gemini-2.0-flash-exp**: Latest experimental flash model (fast, cost-effective)
- **gemini-1.5-pro**: Most capable model for complex tasks
- **gemini-1.5-flash**: Balanced speed and capability

## Understanding Results

The evaluation will generate:

1. **Console Output**: Real-time progress and summary
2. **JSON Report** (`gemini_report.json`): Detailed results for analysis
3. **HTML Dashboard** (`gemini_report.html`): Interactive visualization

### Key Metrics:

- **Response Validation**: Checks if responses match expected outputs
- **Trajectory Validation**: Validates the conversation flow
- **Cost Evaluation**: Tracks Gemini API costs
- **Latency Evaluation**: Monitors response times

## Cost Estimation

Approximate Gemini API costs (as of 2024):

- **Input tokens**: $0.075 per 1M tokens
- **Output tokens**: $0.30 per 1M tokens

The cost evaluator tracks actual usage and alerts if costs exceed thresholds.

## Troubleshooting

### API Key Issues

```
Error: Gemini provider requires 'api_key' in config
```

**Solution**: Set the GEMINI_API_KEY environment variable:
```bash
export GEMINI_API_KEY="your-api-key-here"
```

### Rate Limiting

If you hit rate limits, reduce `max_workers` or add delays between requests.

### Model Not Found

Ensure you're using a valid Gemini model name. Check the [Gemini documentation](https://ai.google.dev/models/gemini) for available models.

## Next Steps

- Modify [sample.evalset.json](sample.evalset.json) with your own test cases
- Adjust evaluator thresholds in [config.yaml](config.yaml)
- Try different Gemini models and parameters
- Compare Gemini with other providers (OpenAI, Claude)

## Learn More

- [Gemini API Documentation](https://ai.google.dev/docs)
- [Judge LLM Documentation](../../README.md)
- [Custom Evaluators Guide](../../docs/CUSTOM_EVALUATORS.md)
