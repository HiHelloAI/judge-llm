---
sidebar_position: 2
---

# Response Evaluator

Validate LLM response quality by comparing actual outputs against expected responses using industry-standard similarity metrics.

## Overview

The **Response Evaluator** measures how well the agent's responses match expected outputs. It supports multiple similarity metrics and automatically selects the best available method.

**Key Features:**
- Multiple similarity metrics (ROUGE, Jaccard, Recall, Exact)
- Automatic ROUGE-1 selection when available
- Configurable thresholds
- Case sensitivity and whitespace normalization
- Multi-turn conversation support
- Detailed similarity breakdowns

## Installation

The response evaluator is **built-in** - no additional installation required!

For ROUGE metrics (recommended):

```bash
pip install judge-llm[rouge]
# or
pip install rouge-score
```

## Configuration

### Basic Configuration

```yaml
evaluators:
  - type: response_evaluator
```

Uses defaults: 0.8 similarity threshold, semantic matching.

### Full Configuration

```yaml
evaluators:
  - type: response_evaluator
    enabled: true
    config:
      similarity_threshold: 0.8      # Pass threshold (0.0-1.0)
      match_type: semantic           # exact, semantic, rouge, recall
      case_sensitive: false          # Case-sensitive matching
      normalize_whitespace: true     # Normalize whitespace/list markers
```

## Similarity Metrics

### 1. ROUGE (Recommended)

**Industry-standard metric** for text similarity used in summarization and translation tasks.

```yaml
config:
  match_type: rouge  # Or auto-selected if rouge-score installed
```

**How it works:**
- Calculates ROUGE-1 F1 score (unigram overlap)
- Balances precision and recall
- Uses stemming for better matching
- Range: 0.0 (no match) to 1.0 (perfect match)

**Example:**
```
Expected: "The capital of France is Paris"
Actual:   "Paris is the capital of France"
ROUGE-1:  0.95 (very high similarity despite different order)
```

**Best for:** Most use cases, natural language responses

### 2. Semantic (Jaccard Index)

**Word-based similarity** using set intersection/union.

```yaml
config:
  match_type: semantic
```

**How it works:**
- Compares word sets (not order)
- Score = intersection / union
- Penalizes both missing and extra words equally

**Example:**
```
Expected: "red blue green"
Actual:   "blue green yellow"
Jaccard:  0.5 (2 overlap / 4 unique words)
```

**Best for:** When ROUGE unavailable, keyword matching

### 3. Recall

**Word recall metric** focusing on expected content coverage.

```yaml
config:
  match_type: recall
```

**How it works:**
- Score = overlap / expected_words
- More lenient for responses with extra information
- Doesn't penalize additional content

**Example:**
```
Expected: "red blue"
Actual:   "red blue green yellow"
Recall:   1.0 (all expected words present)
```

**Best for:** When extra information is acceptable

### 4. Exact Match

**Strict string equality** after normalization.

```yaml
config:
  match_type: exact
```

**How it works:**
- Compares normalized strings
- Returns 1.0 (match) or 0.0 (no match)
- Applies case and whitespace normalization

**Example:**
```
Expected: "Hello World"
Actual:   "hello world"
Score:    1.0 (if case_sensitive: false)
```

**Best for:** Deterministic tests, exact outputs required

## Metric Selection Guide

| Metric | Pros | Cons | Use When |
|--------|------|------|----------|
| **ROUGE** | Industry standard, robust | Requires package | Natural language (recommended) |
| **Semantic** | No dependencies, balanced | Simple word matching | Keyword/short responses |
| **Recall** | Lenient, allows extras | May miss wrong info | Extra details OK |
| **Exact** | Deterministic, fast | Very strict | Exact matches needed |

## Threshold Configuration

### Recommended Thresholds

```yaml
# Strict - For critical/factual responses
similarity_threshold: 0.9

# Balanced - General purpose (default)
similarity_threshold: 0.8

# Lenient - For creative/varied responses
similarity_threshold: 0.7

# Very Lenient - For exploratory/brainstorming
similarity_threshold: 0.6
```

### Task-Specific Thresholds

```yaml
# Math problems - Exact answers
config: {similarity_threshold: 0.95, match_type: exact}

# Translations - High similarity
config: {similarity_threshold: 0.85, match_type: rouge}

# Creative writing - Moderate similarity
config: {similarity_threshold: 0.6, match_type: semantic}

# Code generation - Exact match
config: {similarity_threshold: 1.0, match_type: exact}
```

## Best Practices

### 1. Use ROUGE When Possible

Install `rouge-score` for best results:

```bash
pip install rouge-score
```

ROUGE is industry-standard and more robust than simple word matching.

### 2. Set Realistic Thresholds

Start with 0.8 and adjust:

```yaml
# Start here
similarity_threshold: 0.8

# Adjust based on results
# - Too many failures? Lower to 0.7
# - Need stricter? Raise to 0.9
```

### 3. Test with Mock First

Use mock provider to validate evalsets:

```yaml
providers:
  - type: mock  # Returns expected responses
    agent_id: test

evaluators:
  - type: response_evaluator
```

Should get 100% pass rate (validates your evalset format).

## Related Documentation

- [Evaluators Overview](./overview.md)
- [Trajectory Evaluator](./trajectory-evaluator.md)
- [Custom Evaluators](./custom-evaluators.md)
- [Configuration Guide](../guides/configuration.md)

## API Reference

For implementation details, see the [ResponseEvaluator API Reference](../api-reference/base-classes.md#responseevaluator).
