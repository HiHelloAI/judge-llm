---
sidebar_position: 7
---

# LLM Judge Evaluator

Use an LLM as a judge to evaluate response quality, relevance, hallucination, and factuality.

## Overview

The **LLM Judge Evaluator** sends responses to an LLM (like Gemini) that acts as a judge to assess various quality dimensions. This enables sophisticated evaluation that goes beyond simple text matching.

**Type:** `llm_judge_evaluator`

**Key Features:**
- Multiple evaluation types (relevance, hallucination, quality, factuality)
- Comprehensive multi-dimensional scoring
- Custom evaluation prompts
- Configurable scoring thresholds
- Detailed reasoning and feedback

## Quick Start

```yaml
evaluators:
  - type: llm_judge_evaluator
    config:
      evaluation_type: comprehensive
      min_score: 3.0
```

## Configuration

### Basic Configuration

```yaml
evaluators:
  - type: llm_judge_evaluator
```

### Full Configuration

```yaml
evaluators:
  - type: llm_judge_evaluator
    enabled: true
    config:
      model: gemini-2.0-flash            # Judge model
      api_key: ${GOOGLE_API_KEY}         # API key (or use env var)
      evaluation_type: comprehensive     # Type of evaluation
      min_score: 3.0                     # Minimum score to pass (1-5 scale)
      temperature: 0.0                   # LLM temperature (0 for consistency)
      max_retries: 2                     # Retries on parse failure
      custom_prompt: null                # Custom evaluation prompt
```

## Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `model` | string | `gemini-2.0-flash` | LLM model for judging |
| `api_key` | string | (env var) | API key for the model |
| `evaluation_type` | string | `comprehensive` | Type of evaluation |
| `min_score` | float | `3.0` | Minimum score to pass (1-5) |
| `temperature` | float | `0.0` | LLM temperature |
| `max_retries` | int | `2` | Max retries on parse failure |
| `custom_prompt` | string | `null` | Custom evaluation prompt |

## Evaluation Types

### Relevance

Assesses how well the response addresses the user's query:

```yaml
config:
  evaluation_type: relevance
```

**Scoring (1-5):**
- 5: Highly relevant, fully addresses the query
- 4: Mostly relevant, minor gaps
- 3: Somewhat relevant, addresses part of query
- 2: Mostly irrelevant, tangentially related
- 1: Completely irrelevant

### Hallucination Detection

Checks for fabricated or false information:

```yaml
config:
  evaluation_type: hallucination
```

**Scoring (1-5):**
- 5: No hallucination, all accurate
- 4: Minimal, very minor imprecisions
- 3: Minor hallucination, mostly accurate
- 2: Significant hallucination
- 1: Severe hallucination, multiple false claims

**Additional output:** List of hallucinated claims

### Quality Assessment

Evaluates overall response quality:

```yaml
config:
  evaluation_type: quality
```

**Scoring dimensions:**
- Helpfulness
- Clarity
- Completeness
- Coherence
- Tone

### Factuality

Checks factual accuracy against expected response:

```yaml
config:
  evaluation_type: factuality
```

**Additional output:** List of factual errors found

### Comprehensive (Default)

Multi-dimensional assessment covering all aspects:

```yaml
config:
  evaluation_type: comprehensive
```

**Returns:**
- Overall score (1-5)
- Dimension scores: relevance, accuracy, completeness, clarity, helpfulness
- Strengths and suggested improvements

## Usage Examples

### Example 1: Comprehensive Evaluation

```yaml
evaluators:
  - type: llm_judge_evaluator
    config:
      evaluation_type: comprehensive
      min_score: 3.5
```

**Use case:** General-purpose quality assessment.

### Example 2: Hallucination Detection

```yaml
evaluators:
  - type: llm_judge_evaluator
    config:
      evaluation_type: hallucination
      min_score: 4.0  # Strict - minimal hallucination allowed
```

**Use case:** Fact-critical applications, medical/legal content.

### Example 3: Custom Evaluation Prompt

```yaml
evaluators:
  - type: llm_judge_evaluator
    config:
      custom_prompt: |
        You are evaluating a customer support response.

        User Query: {user_query}
        Response: {response}
        Expected Response: {expected_response}

        Rate the response on professionalism and helpfulness (1-5).

        Respond with ONLY JSON: {{"score": <1-5>, "reasoning": "<explanation>"}}
```

**Use case:** Domain-specific evaluation criteria.

### Example 4: Strict Quality Gate

```yaml
evaluators:
  - type: llm_judge_evaluator
    config:
      evaluation_type: quality
      min_score: 4.0
      temperature: 0.0  # Consistent scoring
```

**Use case:** Production quality gates.

### Example 5: Per-Case Override

```json
{
  "eval_id": "factual_qa_001",
  "evaluator_config": {
    "LLMJudgeEvaluator": {
      "evaluation_type": "factuality",
      "min_score": 4.5
    }
  }
}
```

## Evaluation Result

The evaluator returns detailed results:

```python
{
    "evaluator_name": "LLMJudgeEvaluator",
    "evaluator_type": "llm_judge_evaluator",
    "passed": True,
    "score": 0.75,              # Normalized to 0-1
    "threshold": 0.5,           # Normalized threshold
    "success": True,
    "details": {
        "evaluation_type": "comprehensive",
        "model": "gemini-2.0-flash",
        "min_score": 3.0,
        "average_score": 4.0,   # Original 1-5 scale
        "normalized_score": 0.75,
        "all_invocations_passed": True,
        "num_invocations": 1,
        "invocation_results": [
            {
                "invocation": 0,
                "score": 4.0,
                "passed": True,
                "evaluation_type": "comprehensive",
                "llm_response": {
                    "overall_score": 4,
                    "dimensions": {
                        "relevance": 5,
                        "accuracy": 4,
                        "completeness": 4,
                        "clarity": 4,
                        "helpfulness": 4
                    },
                    "reasoning": "Response addresses the query well...",
                    "strengths": ["Clear explanation", "Accurate facts"],
                    "improvements": ["Could provide more examples"]
                }
            }
        ]
    }
}
```

## When to Use

### Use LLM Judge When:

- Evaluating subjective quality (tone, helpfulness)
- Detecting hallucinations and false claims
- Assessing relevance to user intent
- Testing open-ended or creative responses
- Need nuanced feedback beyond text matching

### Don't Use When:

- Exact output matching is required
- Cost is a primary concern (each eval = API call)
- Evaluating structured data (JSON, code syntax)
- Simple pass/fail criteria exist

## Best Practices

### 1. Use Low Temperature

```yaml
config:
  temperature: 0.0  # Consistent, reproducible scores
```

### 2. Set Appropriate Thresholds

```yaml
# Strict quality (production)
min_score: 4.0

# Moderate quality (development)
min_score: 3.0

# Lenient (early prototyping)
min_score: 2.5
```

### 3. Combine with Other Evaluators

```yaml
evaluators:
  - type: response_evaluator          # Fast, cheap check
    config:
      similarity_threshold: 0.6
  - type: llm_judge_evaluator         # Detailed quality check
    config:
      evaluation_type: comprehensive
      min_score: 3.5
```

### 4. Use Specific Evaluation Types

```yaml
# For Q&A systems
evaluation_type: factuality

# For chatbots
evaluation_type: quality

# For search/retrieval
evaluation_type: relevance
```

### 5. Custom Prompts for Domains

```yaml
config:
  custom_prompt: |
    Evaluate this medical advice response...
    Check for: accuracy, safety warnings, clarity
    ...
```

## Cost Considerations

Each evaluation makes an API call to the judge LLM:

| Scenario | API Calls | Cost Impact |
|----------|-----------|-------------|
| 100 test cases, 1 turn each | 100 | Low |
| 100 test cases, 5 turns each | 500 | Medium |
| 1000 test cases | 1000+ | High |

**Tips to reduce cost:**
- Use smaller judge models (`gemini-2.0-flash`)
- Pre-filter with cheaper evaluators first
- Use sampling for large test suites

## Troubleshooting

### JSON Parse Errors

**Issue:** "Failed to parse JSON response"

**Solutions:**
- Increase `max_retries`
- Use lower temperature
- Simplify custom prompts

### Inconsistent Scores

**Issue:** Same content gets different scores

**Solutions:**
```yaml
config:
  temperature: 0.0  # Deterministic output
  max_retries: 3    # Retry on failures
```

### API Key Errors

**Issue:** "LLM client not available"

**Solutions:**
```bash
export GOOGLE_API_KEY=your-key-here
```

### Low Scores Despite Good Responses

**Issue:** Judge is too strict

**Solutions:**
- Lower `min_score` threshold
- Review expected responses for realism
- Use more lenient evaluation type

## Related Documentation

- [Evaluators Overview](./overview)
- [Embedding Similarity Evaluator](./embedding-similarity-evaluator)
- [Response Evaluator](./response-evaluator)
- [Custom Evaluators](./custom-evaluators)
