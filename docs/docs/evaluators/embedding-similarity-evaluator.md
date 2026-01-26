---
sidebar_position: 6
---

# Embedding Similarity Evaluator

Evaluate semantic similarity between expected and actual responses using embedding models.

## Overview

The **Embedding Similarity Evaluator** computes embeddings for expected and actual responses, then calculates cosine similarity to measure how semantically similar they are.

**Type:** `embedding_similarity_evaluator`

**Key Features:**
- Multiple embedding providers (Gemini, OpenAI, sentence-transformers)
- Cosine similarity scoring
- Automatic text chunking for long responses
- Configurable similarity thresholds
- Optional query-response similarity comparison

## Quick Start

```yaml
evaluators:
  - type: embedding_similarity_evaluator
    config:
      provider: gemini
      similarity_threshold: 0.8
```

## Configuration

### Basic Configuration

```yaml
evaluators:
  - type: embedding_similarity_evaluator
```

### Full Configuration

```yaml
evaluators:
  - type: embedding_similarity_evaluator
    enabled: true
    config:
      provider: gemini                    # gemini, openai, sentence_transformers
      model: text-embedding-004           # Model name (provider-specific)
      api_key: ${GOOGLE_API_KEY}          # API key (or use env var)
      similarity_threshold: 0.8           # Minimum similarity to pass (0.0-1.0)
      compare_with_query: false           # Also compare response with query
      chunk_long_text: true               # Chunk long texts before embedding
      max_chunk_length: 2000              # Max characters per chunk
```

## Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `provider` | string | `gemini` | Embedding provider: `gemini`, `openai`, `sentence_transformers` |
| `model` | string | (varies) | Embedding model name |
| `api_key` | string | (env var) | API key for cloud providers |
| `similarity_threshold` | float | `0.8` | Minimum cosine similarity to pass |
| `compare_with_query` | bool | `false` | Also compute query-response similarity |
| `chunk_long_text` | bool | `true` | Chunk long texts for embedding |
| `max_chunk_length` | int | `2000` | Max characters per chunk |

## Embedding Providers

### Gemini (Default)

Uses Google's text embedding models:

```yaml
config:
  provider: gemini
  model: text-embedding-004  # Default model
```

**Requirements:**
- `pip install google-genai`
- `GOOGLE_API_KEY` environment variable

### OpenAI

Uses OpenAI's embedding models:

```yaml
config:
  provider: openai
  model: text-embedding-3-small
```

**Requirements:**
- `pip install openai`
- `OPENAI_API_KEY` environment variable

### Sentence Transformers

Uses local sentence-transformers models (no API required):

```yaml
config:
  provider: sentence_transformers
  model: all-MiniLM-L6-v2
```

**Requirements:**
- `pip install sentence-transformers`
- No API key needed (runs locally)

## Usage Examples

### Example 1: Basic Semantic Similarity

```yaml
# config.yaml
evaluators:
  - type: embedding_similarity_evaluator
    config:
      provider: gemini
      similarity_threshold: 0.8
```

**Use case:** Verify responses are semantically similar even with different wording.

### Example 2: High-Precision Matching

```yaml
evaluators:
  - type: embedding_similarity_evaluator
    config:
      provider: gemini
      similarity_threshold: 0.95
      chunk_long_text: false
```

**Use case:** Strict semantic matching for critical responses.

### Example 3: Local Evaluation (No API)

```yaml
evaluators:
  - type: embedding_similarity_evaluator
    config:
      provider: sentence_transformers
      model: all-MiniLM-L6-v2
      similarity_threshold: 0.75
```

**Use case:** Offline evaluation without API costs.

### Example 4: Query Relevance Check

```yaml
evaluators:
  - type: embedding_similarity_evaluator
    config:
      provider: gemini
      similarity_threshold: 0.7
      compare_with_query: true
```

**Use case:** Ensure responses are relevant to user queries.

### Example 5: Per-Case Override

```json
{
  "eval_id": "technical_qa_001",
  "evaluator_config": {
    "EmbeddingSimilarityEvaluator": {
      "similarity_threshold": 0.9
    }
  }
}
```

## Evaluation Result

The evaluator returns detailed results:

```python
{
    "evaluator_name": "EmbeddingSimilarityEvaluator",
    "evaluator_type": "embedding_similarity_evaluator",
    "passed": True,
    "score": 0.87,
    "threshold": 0.8,
    "success": True,
    "details": {
        "provider": "gemini",
        "model": "text-embedding-004",
        "similarity_threshold": 0.8,
        "average_similarity": 0.87,
        "num_invocations": 2,
        "invocation_results": [
            {
                "invocation": 0,
                "similarity": 0.92,
                "expected_preview": "The weather in Paris is...",
                "actual_preview": "Paris currently has..."
            },
            {
                "invocation": 1,
                "similarity": 0.82,
                "expected_preview": "The best time to visit...",
                "actual_preview": "I recommend visiting..."
            }
        ]
    }
}
```

## How It Works

### 1. Text Extraction
Extracts text content from expected and actual response parts.

### 2. Text Chunking (Optional)
For long texts, splits into chunks of `max_chunk_length` characters.

### 3. Embedding Generation
Generates embeddings using the configured provider/model.

### 4. Similarity Calculation
Computes cosine similarity between embedding vectors:

```
cosine_similarity = dot(A, B) / (||A|| * ||B||)
```

### 5. Scoring
- Averages similarity across all invocations
- Compares against threshold to determine pass/fail

## When to Use

### Use Embedding Similarity When:

- Responses can vary in wording but should have same meaning
- Testing paraphrasing or summarization
- Validating semantic understanding
- Comparing responses across different models
- Testing multilingual responses

### Don't Use When:

- Exact text match is required (use Response Evaluator)
- Responses contain structured data (JSON, code)
- Testing specific formats or templates
- Cost is a primary concern (consider local models)

## Best Practices

### 1. Choose Appropriate Thresholds

```yaml
# Strict semantic match
similarity_threshold: 0.9

# Moderate match (recommended starting point)
similarity_threshold: 0.8

# Lenient match (for creative responses)
similarity_threshold: 0.7
```

### 2. Use Local Models for Cost Efficiency

```yaml
# No API costs
config:
  provider: sentence_transformers
  model: all-MiniLM-L6-v2
```

### 3. Combine with Other Evaluators

```yaml
evaluators:
  - type: embedding_similarity_evaluator
    config:
      similarity_threshold: 0.8
  - type: response_evaluator
    config:
      match_type: contains  # Check for key phrases
```

### 4. Handle Long Responses

```yaml
config:
  chunk_long_text: true
  max_chunk_length: 2000  # Adjust based on model limits
```

## Troubleshooting

### Low Similarity Scores

**Issue:** Scores consistently below threshold

**Solutions:**
- Lower the threshold (0.7-0.8 is often appropriate)
- Check if responses are actually semantically different
- Verify expected responses are reasonable paraphrases

### API Key Errors

**Issue:** "No API key" errors

**Solutions:**
```bash
# Set environment variable
export GOOGLE_API_KEY=your-key-here

# Or use local model (no key needed)
provider: sentence_transformers
```

### Import Errors

**Issue:** "package not installed" errors

**Solutions:**
```bash
# For Gemini
pip install google-genai

# For OpenAI
pip install openai

# For local models
pip install sentence-transformers
```

### Dimension Mismatch

**Issue:** "Embedding dimension mismatch" warning

**Cause:** Comparing embeddings from different models

**Solution:** Use consistent model for all evaluations

## Related Documentation

- [Evaluators Overview](./overview)
- [Response Evaluator](./response-evaluator) - Text matching
- [LLM Judge Evaluator](./llm-judge-evaluator) - LLM-based evaluation
- [Custom Evaluators](./custom-evaluators)
