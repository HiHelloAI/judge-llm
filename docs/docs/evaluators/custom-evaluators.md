---
sidebar_position: 6
---

# Custom Evaluators

Build domain-specific evaluators to validate any aspect of LLM responses beyond the built-in evaluators.

## Overview

Custom evaluators allow you to:
- Implement business-specific validation rules
- Check safety and compliance requirements
- Validate domain knowledge
- Enforce style guidelines
- Combine multiple evaluation criteria

## Creating a Custom Evaluator

### Step 1: Inherit from BaseEvaluator

```python
from judge_llm.evaluators.base import BaseEvaluator
from judge_llm.core.models import EvalCase, ProviderResult, EvaluatorResult
from typing import Any, Dict, Optional

class MyCustomEvaluator(BaseEvaluator):
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        # Initialize your evaluator
        self.threshold = config.get("threshold", 0.8) if config else 0.8
```

### Step 2: Implement evaluate() Method

```python
def evaluate(
    self,
    eval_case: EvalCase,
    agent_metadata: Dict[str, Any],
    provider_result: ProviderResult,
    eval_config: Optional[Dict[str, Any]] = None,
) -> EvaluatorResult:
    """Evaluate provider result
    
    Args:
        eval_case: Original test case with expected outputs
        agent_metadata: Provider metadata
        provider_result: Actual execution results
        eval_config: Per-test-case configuration override
        
    Returns:
        EvaluatorResult with pass/fail and details
    """
    # Merge config: per-test-case overrides instance config
    config = self.get_config(eval_config)
    
    # Check provider succeeded
    if not provider_result.success:
        return EvaluatorResult(
            evaluator_name=self.get_evaluator_name(),
            evaluator_type=self.get_evaluator_type(),
            success=False,
            passed=False,
            details={"error": "Provider execution failed"},
            error="Provider execution failed",
        )
    
    # Your evaluation logic here
    score = self._calculate_score(provider_result)
    passed = score >= self.threshold
    
    return EvaluatorResult(
        evaluator_name=self.get_evaluator_name(),
        evaluator_type=self.get_evaluator_type(),
        success=True,
        score=score,
        threshold=self.threshold,
        passed=passed,
        details={
            "score": score,
            "threshold": self.threshold,
            # Add your custom details
        },
    )

def _calculate_score(self, provider_result: ProviderResult) -> float:
    """Implement your scoring logic"""
    # Your implementation
    return 0.8
```

## Registration Methods

### Method 1: File-Based Registration

Create a Python file with your evaluator:

```python
# my_evaluators/custom_eval.py
from judge_llm.evaluators.base import BaseEvaluator
from judge_llm.core.models import EvaluatorResult

class CustomEvaluator(BaseEvaluator):
    def evaluate(self, eval_case, agent_metadata, provider_result, eval_config=None):
        # Implementation
        pass
```

Use in config:

```yaml
evaluators:
  - type: custom
    module_path: ./my_evaluators/custom_eval.py
    class_name: CustomEvaluator
    enabled: true
    config:
      threshold: 0.8
      custom_param: value
```

### Method 2: Programmatic Registration

```python
from judge_llm import register_evaluator, evaluate
from my_evaluators.custom_eval import CustomEvaluator

# Register your evaluator
register_evaluator("my_custom_eval", CustomEvaluator)

# Use in evaluation
report = evaluate(
    dataset={"loader": "local_file", "paths": ["./tests.json"]},
    providers=[{"type": "gemini", "agent_id": "test"}],
    evaluators=[{
        "type": "my_custom_eval",
        "config": {"threshold": 0.8}
    }],
    reporters=[{"type": "console"}]
)
```

## Complete Examples

### Example 1: Length Validator

Ensures responses are within specified length bounds:

```python
# evaluators/length_validator.py
from judge_llm.evaluators.base import BaseEvaluator
from judge_llm.core.models import EvalCase, ProviderResult, EvaluatorResult
from typing import Any, Dict, Optional

class LengthValidator(BaseEvaluator):
    """Validate response length is within bounds"""
    
    def evaluate(
        self,
        eval_case: EvalCase,
        agent_metadata: Dict[str, Any],
        provider_result: ProviderResult,
        eval_config: Optional[Dict[str, Any]] = None,
    ) -> EvaluatorResult:
        config = self.get_config(eval_config)
        min_length = config.get("min_length", 10)
        max_length = config.get("max_length", 1000)
        
        if not provider_result.success:
            return EvaluatorResult(
                evaluator_name=self.get_evaluator_name(),
                evaluator_type=self.get_evaluator_type(),
                success=False,
                passed=False,
                details={"error": "Provider execution failed"},
            )
        
        # Check all responses
        issues = []
        total_length = 0
        
        for inv in provider_result.conversation_history:
            response_text = " ".join(
                part.text for part in inv.final_response.parts if part.text
            )
            length = len(response_text)
            total_length += length
            
            if length < min_length:
                issues.append({
                    "invocation": inv.invocation_id,
                    "issue": "too_short",
                    "actual": length,
                    "minimum": min_length
                })
            elif length > max_length:
                issues.append({
                    "invocation": inv.invocation_id,
                    "issue": "too_long",
                    "actual": length,
                    "maximum": max_length
                })
        
        passed = len(issues) == 0
        avg_length = total_length / len(provider_result.conversation_history)
        
        return EvaluatorResult(
            evaluator_name=self.get_evaluator_name(),
            evaluator_type=self.get_evaluator_type(),
            success=True,
            score=1.0 if passed else 0.0,
            passed=passed,
            details={
                "min_length": min_length,
                "max_length": max_length,
                "average_length": avg_length,
                "total_invocations": len(provider_result.conversation_history),
                "issues": issues,
            },
        )
```

**Configuration:**

```yaml
evaluators:
  - type: custom
    module_path: ./evaluators/length_validator.py
    class_name: LengthValidator
    config:
      min_length: 50
      max_length: 500
```

### Example 2: JSON Format Validator

Validates responses are valid JSON:

```python
# evaluators/json_validator.py
import json
from judge_llm.evaluators.base import BaseEvaluator
from judge_llm.core.models import EvalCase, ProviderResult, EvaluatorResult
from typing import Any, Dict, Optional

class JSONValidator(BaseEvaluator):
    """Validate responses are valid JSON"""
    
    def evaluate(
        self,
        eval_case: EvalCase,
        agent_metadata: Dict[str, Any],
        provider_result: ProviderResult,
        eval_config: Optional[Dict[str, Any]] = None,
    ) -> EvaluatorResult:
        config = self.get_config(eval_config)
        require_schema = config.get("require_schema", False)
        expected_keys = config.get("expected_keys", [])
        
        if not provider_result.success:
            return EvaluatorResult(
                evaluator_name=self.get_evaluator_name(),
                evaluator_type=self.get_evaluator_type(),
                success=False,
                passed=False,
                details={"error": "Provider execution failed"},
            )
        
        validation_results = []
        
        for inv in provider_result.conversation_history:
            response_text = " ".join(
                part.text for part in inv.final_response.parts if part.text
            )
            
            try:
                # Try to parse JSON
                parsed = json.loads(response_text)
                
                # Check for expected keys
                missing_keys = [
                    key for key in expected_keys 
                    if key not in parsed
                ]
                
                validation_results.append({
                    "invocation": inv.invocation_id,
                    "valid_json": True,
                    "missing_keys": missing_keys,
                    "has_all_keys": len(missing_keys) == 0,
                })
                
            except json.JSONDecodeError as e:
                validation_results.append({
                    "invocation": inv.invocation_id,
                    "valid_json": False,
                    "error": str(e),
                })
        
        # All must be valid JSON with required keys
        passed = all(
            r["valid_json"] and r.get("has_all_keys", True)
            for r in validation_results
        )
        
        valid_count = sum(1 for r in validation_results if r["valid_json"])
        score = valid_count / len(validation_results)
        
        return EvaluatorResult(
            evaluator_name=self.get_evaluator_name(),
            evaluator_type=self.get_evaluator_type(),
            success=True,
            score=score,
            passed=passed,
            details={
                "expected_keys": expected_keys,
                "validation_results": validation_results,
                "valid_count": valid_count,
                "total_count": len(validation_results),
            },
        )
```

**Configuration:**

```yaml
evaluators:
  - type: custom
    module_path: ./evaluators/json_validator.py
    class_name: JSONValidator
    config:
      expected_keys: ["status", "data", "message"]
```

### Example 3: Safety Evaluator (Full Implementation)

See the complete safety evaluator in Example 04:

[examples/04-safety-long-conversation/evaluators/safety_evaluator.py](https://github.com/yourusername/judge-llm/tree/main/examples/04-safety-long-conversation/evaluators/safety_evaluator.py)

Features:
- PII detection (email, phone, SSN, credit cards)
- Toxicity checking
- Harmful instruction detection
- Hate speech prevention
- Severity thresholds
- Context-aware filtering
- LLM-as-judge pattern support

## Best Practices

### 1. Error Handling

Always handle errors gracefully:

```python
def evaluate(self, eval_case, agent_metadata, provider_result, eval_config=None):
    try:
        # Your evaluation logic
        return EvaluatorResult(...)
    except Exception as e:
        return EvaluatorResult(
            evaluator_name=self.get_evaluator_name(),
            evaluator_type=self.get_evaluator_type(),
            success=False,
            passed=False,
            error=str(e),
            details={"exception": str(e)},
        )
```

### 2. Use Per-Case Config

Support overriding settings per test case:

```python
def evaluate(self, eval_case, agent_metadata, provider_result, eval_config=None):
    # Merge configurations
    config = self.get_config(eval_config)
    
    # Use merged config
    threshold = config.get("threshold", 0.8)
```

### 3. Provide Detailed Feedback

Include actionable details in results:

```python
return EvaluatorResult(
    # ...
    details={
        "score": score,
        "threshold": threshold,
        "reasons_for_failure": reasons,  # What went wrong
        "suggestions": suggestions,       # How to fix
        "examples": examples,             # Specific examples
    },
)
```

### 4. Analyze All Invocations

For multi-turn conversations, check all turns:

```python
for inv in provider_result.conversation_history:
    response_text = " ".join(
        part.text for part in inv.final_response.parts if part.text
    )
    # Analyze this turn
```

### 5. Normalize Scores

Return scores in 0.0-1.0 range:

```python
# Good
score = valid_count / total_count  # 0.0 to 1.0

# Also good
score = max(0.0, 1.0 - (issues / max_expected_issues))
```

## Common Patterns

### Pattern 1: Keyword Checker

```python
def _check_keywords(self, text: str, required_keywords: list) -> float:
    """Check presence of required keywords"""
    text_lower = text.lower()
    found = sum(1 for kw in required_keywords if kw in text_lower)
    return found / len(required_keywords)
```

### Pattern 2: Regex Validator

```python
def _validate_format(self, text: str, pattern: str) -> bool:
    """Validate text matches regex pattern"""
    import re
    return bool(re.match(pattern, text))
```

### Pattern 3: External API Call

```python
def _call_external_validator(self, text: str) -> dict:
    """Call external validation service"""
    import requests
    response = requests.post(
        "https://api.validator.com/check",
        json={"text": text},
        timeout=10
    )
    return response.json()
```

### Pattern 4: LLM-as-Judge

```python
def _llm_judge(self, text: str, criteria: str) -> dict:
    """Use LLM to evaluate quality"""
    # Call LLM API with evaluation prompt
    prompt = f"""Evaluate this response based on: {criteria}
    
Response: {text}

Return JSON with score (0-1) and reasoning."""
    
    # Call your LLM provider
    result = your_llm_call(prompt)
    return result
```

## Testing Your Evaluator

### Unit Tests

```python
# tests/test_custom_evaluator.py
from my_evaluators.length_validator import LengthValidator
from judge_llm.core.models import EvalCase, ProviderResult

def test_length_validator():
    evaluator = LengthValidator({"min_length": 10, "max_length": 100})
    
    # Create test case
    eval_case = create_test_eval_case()
    provider_result = create_test_provider_result()
    
    # Run evaluation
    result = evaluator.evaluate(eval_case, {}, provider_result)
    
    assert result.success
    assert result.passed or not result.passed  # Depends on test data
```

### Integration Tests

```python
from judge_llm import evaluate

def test_length_validator_integration():
    report = evaluate(
        dataset={"loader": "local_file", "paths": ["./test_cases.json"]},
        providers=[{"type": "mock", "agent_id": "test"}],
        evaluators=[{
            "type": "custom",
            "module_path": "./my_evaluators/length_validator.py",
            "class_name": "LengthValidator",
            "config": {"min_length": 10, "max_length": 100}
        }],
        reporters=[{"type": "console"}]
    )
    
    assert report.total_test_cases > 0
```

## Troubleshooting

### Evaluator Not Found

**Error:** `Evaluator type 'my_custom' not found`

**Solution:** Use `type: custom` with `module_path` and `class_name`

### Module Import Error

**Error:** `ModuleNotFoundError: No module named 'my_evaluators'`

**Solution:** Check `module_path` is correct relative path from execution directory

### AttributeError

**Error:** `'CustomEvaluator' object has no attribute 'get_evaluator_name'`

**Solution:** Ensure you inherit from `BaseEvaluator`

## Related Documentation

- [Evaluators Overview](./overview.md)
- [Response Evaluator](./response-evaluator.md)
- [Safety Evaluation Example](../examples/safety-evaluation.md)
- [Base Classes API](../api-reference/base-classes.md)

## Example Gallery

Find more custom evaluator examples in:
- [examples/04-safety-long-conversation/](https://github.com/yourusername/judge-llm/tree/main/examples/04-safety-long-conversation)
- [examples/03-custom-evaluator/](https://github.com/yourusername/judge-llm/tree/main/examples/03-custom-evaluator)
