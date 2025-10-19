---
sidebar_position: 5
---

# Next Steps

You've completed the quick start tutorials! Here's where to go from here.

## 🎉 What You've Learned

✅ Installed Judge LLM and set up API keys  
✅ Created test cases and configuration files  
✅ Ran your first evaluation  
✅ Used the Python API programmatically  
✅ Compared multiple models  
✅ Analyzed results and made decisions  

## 📚 Continue Learning

### Deep Dive into Features

#### 1. Master Configuration
Learn all configuration options and patterns:
- [Configuration Guide](../guides/configuration) - Complete reference
- [Default Configs](../guides/default-configs) - Reusable defaults
- [Environment Variables](../guides/environment-variables) - Secure config

#### 2. Explore Evaluators
Understand different evaluation methods:
- [Response Evaluator](../evaluators/response-evaluator) - LLM-as-judge
- [Trajectory Evaluator](../evaluators/trajectory-evaluator) - Reasoning process
- [Cost Evaluator](../evaluators/cost-evaluator) - Budget control
- [Latency Evaluator](../evaluators/latency-evaluator) - Performance
- [Custom Evaluators](../evaluators/custom-evaluators) - Build your own

#### 3. Master Reporters
Learn about different output formats:
- [Console Reporter](../reporters/console-reporter) - Terminal output
- [HTML Reporter](../reporters/html-reporter) - Interactive reports
- [JSON Reporter](../reporters/json-reporter) - Machine-readable
- [Database Reporter](../reporters/database-reporter) - SQLite storage
- [Custom Reporters](../reporters/custom-reporters) - Build your own

### Explore Examples

Work through real-world examples:

1. **[01-gemini-agent](../examples/gemini-agent)** - Basic setup
2. **[02-default-config](../examples/default-config)** - Using defaults
3. **[03-custom-evaluator](../examples/custom-evaluator)** - Custom evaluators
4. **[04-safety-evaluation](../examples/safety-evaluation)** - Multi-turn
5. **[05-config-override](../examples/config-override)** - Overrides
6. **[06-database-tracking](../examples/database-tracking)** - Historical tracking
7. **CSV Reporter** - See [Custom Reporters](../reporters/custom-reporters)
8. **Component Registration** - See [Default Configs](../guides/default-configs)

[View All Examples](../examples/overview)

## 🚀 Common Next Projects

### Project 1: Set Up CI/CD Testing

Add LLM evaluation to your CI/CD pipeline:

**GitHub Actions Example:**

```yaml
# .github/workflows/llm-eval.yml
name: LLM Evaluation

on: [push, pull_request]

jobs:
  evaluate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install Judge LLM
        run: pip install judge-llm
      
      - name: Run Evaluation
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
        run: judge-llm run --config tests/eval.yaml
      
      - name: Upload Report
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: evaluation-report
          path: report.html
```

[Learn More: CLI Reference](../guides/cli-reference.md#cicd-integration)

### Project 2: Build Custom Evaluator

Create domain-specific validation:

```python
# evaluators/my_evaluator.py
from judge_llm.evaluators.base import BaseEvaluator
from judge_llm.core.models import EvaluationResult

class MyDomainEvaluator(BaseEvaluator):
    def evaluate(self, test_case, response):
        # Your custom logic here
        content = response.get("content", "")
        
        # Check your domain-specific rules
        is_valid = self._check_domain_rules(content)
        
        return EvaluationResult(
            evaluator_type="my_domain",
            passed=is_valid,
            score=1.0 if is_valid else 0.0,
            reason="Valid" if is_valid else "Invalid"
        )
    
    def _check_domain_rules(self, content):
        # Implement your rules
        return True
```

[Learn More: Custom Evaluators Guide](../evaluators/custom-evaluators)

### Project 3: Historical Tracking

Track evaluation results over time:

```yaml
# config.yaml
reporters:
  - type: console
  - type: database
    db_path: ./history.db
```

Query trends:
```sql
SELECT
    DATE(timestamp) as date,
    AVG(success_rate) as avg_success,
    AVG(total_cost) as avg_cost
FROM evaluation_runs
GROUP BY DATE(timestamp)
ORDER BY date DESC
LIMIT 30;
```

[Learn More: Database Reporter](../reporters/database-reporter)

### Project 4: Multi-Provider Testing

Test across different providers:

```yaml
providers:
  - type: gemini
    agent_id: gemini
  - type: openai
    agent_id: openai
  - type: anthropic
    agent_id: claude

evaluators:
  - type: response_evaluator
  - type: cost_evaluator
    max_cost: 0.01

reporters:
  - type: html
    output_path: ./provider-comparison.html
```

[Learn More: Comparing Models](./comparing-models)

## 🔧 Advanced Topics

### Custom Component Registration

Register components globally for reuse:

```yaml
# .judge_llm.defaults.yaml
evaluators:
  - type: custom
    module_path: ./evaluators/safety.py
    class_name: SafetyEvaluator
    register_as: safety

reporters:
  - type: custom
    module_path: ./reporters/slack.py
    class_name: SlackReporter
    register_as: slack
```

Use everywhere:
```yaml
# test.yaml
evaluators:
  - type: safety
reporters:
  - type: slack
    webhook_url: ${SLACK_WEBHOOK}
```

[Learn More: Default Configs](../guides/default-configs)

### Programmatic Workflows

Build automated evaluation workflows:

```python
from judge_llm import evaluate
import schedule
import time

def daily_evaluation():
    """Run daily evaluation and alert on failures"""
    report = evaluate(
        dataset={"loader": "local_file", "paths": ["./daily-tests.json"]},
        providers=[{"type": "gemini", "agent_id": "prod"}],
        evaluators=[{"type": "response_evaluator"}],
        reporters=[
            {"type": "database", "db_path": "./daily.db"},
            {"type": "slack", "webhook_url": os.getenv("SLACK_WEBHOOK")}
        ]
    )
    
    if not report.overall_success:
        send_alert(f"Daily evaluation failed: {report.success_rate:.1%}")

# Schedule daily at 9 AM
schedule.every().day.at("09:00").do(daily_evaluation)

while True:
    schedule.run_pending()
    time.sleep(60)
```

[Learn More: Python API Reference](../guides/python-api)

## 📖 Reference Documentation

### Quick Links

- **[CLI Reference](../guides/cli-reference)** - All CLI commands
- **[Python API](../guides/python-api)** - Complete API docs
- **[Configuration Guide](../guides/configuration)** - All config options
- **[Evalset Format](../guides/evalset-format)** - Test case specification

### Component Documentation

**Evaluators:**
- [Overview](../evaluators/overview)
- [Response](../evaluators/response-evaluator)
- [Trajectory](../evaluators/trajectory-evaluator)
- [Cost](../evaluators/cost-evaluator)
- [Latency](../evaluators/latency-evaluator)
- [Custom](../evaluators/custom-evaluators)

**Reporters:**
- [Overview](../reporters/overview)
- [Console](../reporters/console-reporter)
- [HTML](../reporters/html-reporter)
- [JSON](../reporters/json-reporter)
- [Database](../reporters/database-reporter)
- [Custom](../reporters/custom-reporters)

## 🤝 Get Help

### Troubleshooting

Check the troubleshooting sections in:
- [Basic Usage Guide](../guides/basic-usage.md#common-mistakes)
- [CLI Reference](../guides/cli-reference.md#troubleshooting)
- Each component's documentation

### Common Issues

1. **API Key Not Found**
   - Check `.env` file exists
   - Verify environment variables are set
   - See [Environment Variables](../guides/environment-variables)

2. **Tests Failing**
   - Review evaluator output for reasons
   - Check expected responses are correct
   - See [First Evaluation](./first-evaluation.md#troubleshooting)

3. **High Costs**
   - Add cost evaluator with limits
   - Use cheaper models
   - See [Cost Evaluator](../evaluators/cost-evaluator)

## 🎯 Choose Your Path

### For Application Developers
Focus on integration and automation:
1. [Python API Reference](../guides/python-api)
2. [Custom Evaluators](../evaluators/custom-evaluators)
3. [Database Reporter](../reporters/database-reporter)

### For QA Engineers
Focus on testing and validation:
1. [CLI Reference](../guides/cli-reference)
2. [Evalset Format](../guides/evalset-format)
3. [HTML Reporter](../reporters/html-reporter)

### For Data Scientists
Focus on analysis and comparison:
1. [Comparing Models](./comparing-models)
2. [Python API](../guides/python-api)
3. [Database Reporter](../reporters/database-reporter)

### For DevOps Engineers
Focus on CI/CD and monitoring:
1. [CLI Reference](../guides/cli-reference.md#cicd-integration)
2. [Environment Variables](../guides/environment-variables)
3. [Database Reporter](../reporters/database-reporter)

## 🚀 You're Ready!

You now have all the knowledge to:
- ✅ Evaluate LLMs effectively
- ✅ Compare models objectively
- ✅ Integrate into your workflow
- ✅ Build custom components
- ✅ Track results over time

**Happy evaluating!** 🎉

---

*Need more help? Check out the [complete documentation](../intro) or explore [examples](../examples).*
