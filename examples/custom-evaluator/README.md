# Custom Evaluator Example

This example demonstrates how to create and use custom evaluators in Judge LLM.

## Files

- `evaluators/sentiment_evaluator.py` - Custom evaluator implementation
- `config.yaml` - Configuration file using the custom evaluator
- `sample.evalset.json` - Sample evaluation dataset
- `run.py` - Python script demonstrating both config-based and programmatic registration

## Custom Evaluator Implementation

The `SentimentEvaluator` is a simple example that:
1. Counts positive and negative words in responses
2. Calculates a sentiment score
3. Checks if the score meets the threshold

### Key Points

1. **Inherit from `BaseEvaluator`**: All custom evaluators must inherit from the base class
2. **Implement `evaluate()` method**: This is where your evaluation logic goes
3. **Use the config**: Accept configuration via the `config` parameter
4. **Return `EvaluatorResult`**: Return a structured result with score, pass/fail, and details

## Usage Methods

### Method 1: Config File (Recommended)

Load custom evaluator via config file:

```yaml
evaluators:
  - type: custom
    module_path: ./evaluators/sentiment_evaluator.py
    class_name: SentimentEvaluator
    enabled: true
    config:
      min_positive_sentiment: 0.3
```

Run:
```bash
judge-llm run --config config.yaml
```

### Method 2: Programmatic Registration

Register and use in Python code:

```python
from judge_llm import evaluate, register_evaluator
from evaluators.sentiment_evaluator import SentimentEvaluator

# Register the evaluator
register_evaluator("sentiment", SentimentEvaluator)

# Use it in evaluate()
report = evaluate(
    evaluators=[
        {
            "type": "sentiment",
            "enabled": True,
            "config": {"min_positive_sentiment": 0.3},
        }
    ],
    ...
)
```

## Running the Example

```bash
python run.py
```

## Creating Your Own Evaluator

1. Create a new Python file in `evaluators/` directory
2. Import `BaseEvaluator` from `judge_llm.evaluators.base`
3. Import required models from `judge_llm.core.models`
4. Create a class that inherits from `BaseEvaluator`
5. Implement the `__init__` and `evaluate` methods
6. Use it via config file or register programmatically

### Template

```python
from judge_llm.evaluators.base import BaseEvaluator
from judge_llm.core.models import EvalCase, ProviderResult, EvaluatorResult

class MyCustomEvaluator(BaseEvaluator):
    def __init__(self, config=None):
        super().__init__(config)
        # Extract config values
        self.my_threshold = self.config.get("my_threshold", 0.5)

    def evaluate(self, eval_case, agent_metadata, provider_result):
        # Your evaluation logic here

        return EvaluatorResult(
            evaluator_name=self.get_evaluator_name(),
            evaluator_type=self.get_evaluator_type(),
            success=True,
            score=my_score,
            threshold=self.my_threshold,
            passed=my_score >= self.my_threshold,
            details={"key": "value"},
        )
```

## Benefits of Custom Evaluators

- Implement domain-specific evaluation logic
- Add business rules validation
- Integrate with external services or APIs
- Create specialized metrics for your use case
- Share evaluators across different eval sets
