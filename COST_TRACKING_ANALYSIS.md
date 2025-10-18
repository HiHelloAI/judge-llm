# Cost Tracking Analysis

## Overview
This document analyzes how cost is tracked throughout the judge_llm evaluation system.

## Cost Calculation Flow

### 1. Provider Level (Gemini Example)
**File**: `judge_llm/providers/gemini_provider.py:315-324`

```python
def _calculate_cost(self, token_usage: Dict[str, int]) -> float:
    input_tokens = token_usage.get("prompt_tokens", 0)
    output_tokens = token_usage.get("completion_tokens", 0)

    # Pricing per million tokens
    input_cost_per_million = 0.075   # $0.075 per 1M input tokens
    output_cost_per_million = 0.30   # $0.30 per 1M output tokens

    input_cost = (input_tokens / 1_000_000) * input_cost_per_million
    output_cost = (output_tokens / 1_000_000) * output_cost_per_million

    return input_cost + output_cost
```

**Multi-turn Conversations**: Cost is accumulated across all turns
- Line 106: `total_cost = 0.0`
- Line 156-157: For each turn, calculate cost and add to total
- Line 183: Return `ProviderResult(cost=total_cost, ...)`

### 2. ProviderResult Model
**File**: `judge_llm/core/models.py:114-123`

```python
class ProviderResult(BaseModel):
    conversation_history: List[Invocation]
    cost: float = 0.0          # ✓ Cost stored here
    time_taken: float = 0.0
    token_usage: Dict[str, int] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    success: bool = True
    error: Optional[str] = None
```

### 3. Database Storage
**File**: `judge_llm/reporters/database_reporter.py:77-98`

**Schema**:
```sql
CREATE TABLE execution_runs (
    execution_id TEXT PRIMARY KEY,
    ...
    cost REAL DEFAULT 0.0,              -- ✓ Per-execution cost
    time_taken REAL DEFAULT 0.0,
    input_tokens INTEGER DEFAULT 0,
    output_tokens INTEGER DEFAULT 0,
    total_tokens INTEGER DEFAULT 0,
    ...
)
```

**Insertion** (Line 336):
```python
cursor.execute("""
    INSERT INTO execution_runs (...)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (
    ...
    run.provider_result.cost,  # ✓ Uses provider-calculated cost
    run.provider_result.time_taken,
    ...
))
```

### 4. Dashboard Queries
**File**: `judge_llm/templates/dashboard_v2.html`

#### Total Cost (Line 695):
```javascript
const totalCost = db.exec(`
    SELECT SUM(cost) as total
    FROM execution_runs
    ${filter}
`)[0];
```

#### Cost Over Time (Line 711):
```javascript
SELECT
    DATE(timestamp) as date,
    SUM(cost) as cost,
    ...
FROM execution_runs
GROUP BY DATE(timestamp)
```

#### Individual Execution Costs (Line 720):
```javascript
SELECT
    execution_id,
    eval_case_id,
    cost,
    timestamp
FROM execution_runs
ORDER BY timestamp DESC
LIMIT 50
```

#### Agent-Specific Costs (Line 963):
```javascript
SELECT
    DATE(er.timestamp) as date,
    SUM(er.cost) as cost,
    ...
FROM eval_cases ec
JOIN execution_runs er ON ec.eval_case_id = er.eval_case_id
WHERE ec.app_name = ?
GROUP BY DATE(er.timestamp)
```

## Data Verification

### Test Database: test_multiple_runs.db
```sql
SELECT execution_id, cost, input_tokens, output_tokens, provider_type
FROM execution_runs LIMIT 5;

exec-1|0.001|11|6|gemini
exec-2|0.002|12|7|openai
exec-3|0.003|13|8|gemini
exec-4|0.004|14|9|anthropic
exec-5|0.005|15|10|openai
```

✓ Cost is stored correctly in database
✓ Cost is associated with each execution_id

## Potential Issues

### Issue 1: Provider-Specific Pricing
**Current**: Only Gemini provider has actual cost calculation
**Impact**: Other providers (OpenAI, Anthropic) may show $0.00 or incorrect costs

**Files to check**:
- `judge_llm/providers/openai_provider.py`
- `judge_llm/providers/anthropic_provider.py`
- `judge_llm/providers/mock_provider.py`

### Issue 2: Cost Aggregation
**Correct Approach**:
```sql
SUM(cost) FROM execution_runs  -- ✓ Sum individual execution costs
```

**Incorrect Approach**:
```sql
SUM(total_cost) FROM reports   -- ✗ Would sum report-level costs (different granularity)
```

### Issue 3: Multi-Turn Conversations
**Gemini Provider**: ✓ Correctly accumulates cost across turns
**Question**: Do other providers handle this correctly?

## Recommendations

### 1. Verify All Providers Calculate Cost
Check each provider implementation:
- OpenAI: Uses different pricing model
- Anthropic: Uses different pricing model
- Mock: Should return test cost values

### 2. Add Cost Validation Query
```sql
-- Check if costs are being recorded
SELECT
    provider_type,
    COUNT(*) as executions,
    SUM(cost) as total_cost,
    AVG(cost) as avg_cost,
    MIN(cost) as min_cost,
    MAX(cost) as max_cost
FROM execution_runs
GROUP BY provider_type;
```

### 3. Add Cost Debugging
In dashboard, add console logging:
```javascript
console.log('Total Cost Query Result:', totalCost);
console.log('Individual Costs:', individualCosts);
```

### 4. Verify Token Usage
Cost should correlate with token usage:
```sql
SELECT
    execution_id,
    cost,
    input_tokens,
    output_tokens,
    (cost * 1000000) / (input_tokens + output_tokens) as cost_per_token
FROM execution_runs
WHERE cost > 0
ORDER BY cost DESC
LIMIT 10;
```

## What to Check Next

1. **Which provider are you using?**
   - If not Gemini, cost calculation may not be implemented

2. **Are tokens being tracked?**
   ```sql
   SELECT * FROM execution_runs WHERE input_tokens > 0 LIMIT 5;
   ```

3. **Is cost zero for all executions?**
   ```sql
   SELECT COUNT(*) as zero_cost FROM execution_runs WHERE cost = 0;
   SELECT COUNT(*) as has_cost FROM execution_runs WHERE cost > 0;
   ```

4. **Check the actual database file you're loading in the dashboard**
   - Make sure you're not looking at test data with fake costs

## Conclusion

The cost tracking infrastructure is **correctly implemented** for:
- ✓ Cost calculation in Gemini provider
- ✓ Storage in database (execution_runs.cost)
- ✓ Dashboard queries (SUM, aggregation, filtering)

**Most likely issue**: You're either:
1. Using a provider without cost calculation implemented
2. Looking at test data with synthetic costs
3. Database file doesn't have real execution data yet

**Next steps**:
- Check which provider you're using
- Run actual evaluations to generate real cost data
- Query your database to see actual cost values
