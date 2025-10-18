---
sidebar_position: 1
---

# Getting Started with Judge LLM

Welcome to **Judge LLM** - a lightweight, extensible Python framework for evaluating and comparing LLM providers.

![Judge LLM Demo](/img/demo.gif)

## What is Judge LLM?

Judge LLM helps you systematically evaluate AI agents and LLM providers by running test cases against your models and measuring:

- **Response Quality** - Exact matching, semantic similarity, ROUGE scores
- **Cost & Latency** - Token usage, execution time, budget compliance
- **Conversation Flow** - Tool uses, multi-turn interactions
- **Safety & Custom Metrics** - Extensible evaluation logic

Perfect for regression testing, A/B testing providers, and ensuring production-grade quality.

## Key Features

- 🚀 **Multiple Providers** - Gemini, Mock, and custom providers
- 📊 **Built-in Evaluators** - Response similarity, trajectory validation, cost/latency checks
- 🔌 **Extensible** - Plugin system for custom evaluators and providers
- 📈 **Rich Reports** - Console tables, interactive HTML dashboard, JSON exports, SQLite database
- ⚡ **Parallel Execution** - Run evaluations concurrently with configurable workers
- 🛠️ **Config-Driven** - YAML configs with smart defaults or programmatic Python API
- 🎯 **Per-Test Overrides** - Fine-tune evaluator thresholds per test case

## Quick Example

### CLI Usage

```bash
# Run evaluation from config file
judge-llm run --config config.yaml

# Run with inline arguments
judge-llm run --dataset ./data/eval.json --provider mock --agent-id my_agent --report html
```

### Python API

```python
from judge_llm import evaluate

# From config file
report = evaluate(config="config.yaml")

# Programmatic API
report = evaluate(
    dataset={"loader": "local_file", "paths": ["./data/eval.json"]},
    providers=[{"type": "mock", "agent_id": "my_agent"}],
    evaluators=[{"type": "response_evaluator", "config": {"similarity_threshold": 0.8}}],
    reporters=[{"type": "console"}, {"type": "html", "output_path": "./report.html"}]
)

print(f"Success: {report.success_rate:.1%} | Cost: ${report.total_cost:.4f}")
```

## Use Cases

- **Regression Testing** - Ensure new model versions don't degrade performance
- **Provider Comparison** - Compare Gemini vs OpenAI vs Claude on your use cases
- **Cost Optimization** - Track and optimize API costs across evaluations
- **Safety Validation** - Detect PII leaks, toxic content, harmful instructions
- **Quality Assurance** - Systematic testing before production deployment

## Next Steps

1. [Install Judge LLM](./installation.md)
2. [Follow the Quick Start guide](./quick-start.md)
3. [Explore Examples](./examples/overview.md)
4. [Learn Core Concepts](./core-concepts/overview.md)

## Need Help?

- 📚 Browse the [documentation](./guides/basic-usage.md)
- 💡 Check out [examples](./examples/overview.md)
- 🐛 Report issues on [GitHub](https://github.com/yourusername/judge-llm/issues)
- 🤝 Read the [contributing guide](./contributing/development-setup.md)
