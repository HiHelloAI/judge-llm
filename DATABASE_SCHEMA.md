# Database Reporter - Complete Schema Documentation

The Database Reporter stores complete evaluation history in a SQLite database with full conversation tracking, enabling comprehensive analysis, trend monitoring, and detailed investigation of test executions.

## Overview

The enhanced database schema provides:
- **Complete conversation history** (expected vs actual responses)
- **Test case tracking** across multiple runs
- **Time-based performance trends**
- **Provider and model comparison**
- **Detailed evaluator scoring**
- **Cost and token usage analysis**
- **Full investigation capabilities** for any test execution

## Database Schema

### Entity Relationship Diagram

```
reports (1) ──< (N) execution_runs (N) >── (1) eval_cases (N) >── (1) eval_sets
                      │
                      ├─< (N) invocations
                      │
                      └─< (N) evaluator_results
```

### Table Definitions

#### 1. `reports`
High-level evaluation report summary

| Column | Type | Description |
|--------|------|-------------|
| `report_id` | TEXT | Primary key, format: `report_YYYY-MM-DDTHH:MM:SS` |
| `generated_at` | TEXT | ISO timestamp when report was generated |
| `total_cost` | REAL | Total cost across all executions in this report |
| `total_time` | REAL | Total time in seconds |
| `success_rate` | REAL | Overall success rate (0.0 - 1.0) |
| `overall_success` | INTEGER | 1 if all tests passed, 0 otherwise |
| `summary_json` | TEXT | Additional summary metadata as JSON |
| `created_at` | TEXT | Database insertion timestamp (auto) |

**Use Cases:**
- Track evaluation runs over time
- Monitor overall success trends
- Analyze cost and performance per evaluation batch

#### 2. `eval_sets`
Evaluation dataset metadata

| Column | Type | Description |
|--------|------|-------------|
| `eval_set_id` | TEXT | Primary key, unique dataset identifier |
| `name` | TEXT | Human-readable dataset name |
| `description` | TEXT | Dataset description |
| `creation_timestamp` | REAL | Unix timestamp when dataset was created |
| `first_seen` | TEXT | When this dataset was first encountered (auto) |

**Use Cases:**
- Group test cases by dataset
- Track dataset history and usage
- Organize test suites

#### 3. `eval_cases`
Individual test case definitions

| Column | Type | Description |
|--------|------|-------------|
| `eval_case_id` | TEXT | Primary key, unique test case identifier |
| `eval_set_id` | TEXT | Foreign key to eval_sets |
| `app_name` | TEXT | Application name from session input |
| `user_id` | TEXT | User identifier from session input |
| `user_prompt` | TEXT | The user's question/prompt for this test |
| `system_instruction` | TEXT | System instructions for the LLM |
| `creation_timestamp` | REAL | Unix timestamp when test case was created |
| `state_json` | TEXT | Session state as JSON |
| `first_seen` | TEXT | When this test case was first encountered (auto) |

**Use Cases:**
- Look up test case details
- Search tests by prompt text
- Track which tests are run most frequently
- Identify problematic test cases

#### 4. `execution_runs`
Individual test executions (the heart of the schema)

| Column | Type | Description |
|--------|------|-------------|
| `execution_id` | TEXT | Primary key, unique execution identifier |
| `report_id` | TEXT | Foreign key to reports |
| `run_number` | INTEGER | Run number (for multiple runs of same test) |
| `eval_set_id` | TEXT | Foreign key to eval_sets |
| `eval_case_id` | TEXT | Foreign key to eval_cases |
| `provider_type` | TEXT | LLM provider (gemini, openai, anthropic, etc.) |
| `provider_model` | TEXT | Specific model used (gpt-4, gemini-2.0-flash-exp, etc.) |
| `overall_success` | INTEGER | 1 if execution succeeded, 0 otherwise |
| `timestamp` | TEXT | ISO timestamp of execution |
| `cost` | REAL | Execution cost in dollars |
| `time_taken` | REAL | Execution time in seconds |
| `input_tokens` | INTEGER | Number of input tokens |
| `output_tokens` | INTEGER | Number of output tokens |
| `total_tokens` | INTEGER | Total tokens (input + output) |
| `metadata_json` | TEXT | Additional provider metadata as JSON |

**Use Cases:**
- Core table for all analysis
- Track performance over time
- Compare providers and models
- Monitor costs and token usage
- Identify slow tests
- Investigate specific executions

#### 5. `invocations`
Complete conversation history (NEW - most powerful feature!)

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER | Auto-increment primary key |
| `execution_id` | TEXT | Foreign key to execution_runs |
| `invocation_id` | TEXT | Unique invocation identifier |
| `invocation_type` | TEXT | 'expected' or 'actual' |
| `sequence_order` | INTEGER | Order in conversation (0, 1, 2, ...) |
| `user_message` | TEXT | User's message (extracted text) |
| `assistant_message` | TEXT | Assistant's response (extracted text) |
| `creation_timestamp` | REAL | Unix timestamp of invocation |
| `user_content_json` | TEXT | Full user content as JSON |
| `final_response_json` | TEXT | Full assistant response as JSON |
| `intermediate_data_json` | TEXT | Tool uses, function calls, etc. as JSON |

**Invocation Types:**
- **`expected`**: The expected/reference conversation from the test case
- **`actual`**: The actual conversation generated by the provider during testing

**Use Cases:**
- Compare expected vs actual responses side-by-side
- Investigate why a test failed
- Analyze multi-turn conversations
- Track how responses differ across providers
- Debug evaluator failures
- Extract conversation patterns

#### 6. `evaluator_results`
Evaluation outcomes and scores

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER | Auto-increment primary key |
| `execution_id` | TEXT | Foreign key to execution_runs |
| `evaluator_name` | TEXT | Name of the evaluator |
| `evaluator_type` | TEXT | Type (response_evaluator, custom, etc.) |
| `success` | INTEGER | 1 if evaluator ran successfully, 0 if error |
| `passed` | INTEGER | 1 if evaluation passed, 0 if failed |
| `score` | REAL | Evaluation score (if applicable) |
| `threshold` | REAL | Pass/fail threshold (if applicable) |
| `details_json` | TEXT | Detailed evaluation results as JSON |
| `error` | TEXT | Error message if evaluator failed |
| `evaluated_at` | TEXT | Timestamp of evaluation (auto) |

**Use Cases:**
- Track evaluator performance
- Analyze score distributions
- Identify unreliable evaluators
- Debug evaluation logic
- Monitor pass/fail rates
- Investigate borderline cases

### Indexes

Indexes for query performance:

- `idx_execution_runs_report_id` - Join with reports
- `idx_execution_runs_timestamp` - Time-based queries
- `idx_execution_runs_provider` - Filter by provider
- `idx_execution_runs_eval_case` - Test case lookups
- `idx_execution_runs_eval_set` - Dataset queries
- `idx_evaluator_results_execution_id` - Join evaluator results
- `idx_evaluator_results_evaluator_name` - Filter by evaluator
- `idx_evaluator_results_passed` - Find failures quickly
- `idx_invocations_execution_id` - Get conversation history
- `idx_invocations_type` - Filter by expected/actual

## Common Query Patterns

### 1. Compare Expected vs Actual Responses

```sql
SELECT
    ex.execution_id,
    ex.eval_case_id,
    ec.user_prompt,
    expected.assistant_message as expected_response,
    actual.assistant_message as actual_response,
    ev.score,
    ev.passed
FROM execution_runs ex
JOIN eval_cases ec ON ex.eval_case_id = ec.eval_case_id
LEFT JOIN invocations expected ON ex.execution_id = expected.execution_id
    AND expected.invocation_type = 'expected'
LEFT JOIN invocations actual ON ex.execution_id = actual.execution_id
    AND actual.invocation_type = 'actual'
LEFT JOIN evaluator_results ev ON ex.execution_id = ev.execution_id
WHERE ex.overall_success = 0
ORDER BY ex.timestamp DESC;
```

### 2. Time-Based Performance Trends

```sql
SELECT
    DATE(timestamp) as date,
    provider_type,
    COUNT(*) as runs,
    AVG(cost) as avg_cost,
    AVG(time_taken) as avg_time,
    SUM(CASE WHEN overall_success = 1 THEN 1 ELSE 0 END) as successful
FROM execution_runs
GROUP BY DATE(timestamp), provider_type
ORDER BY date DESC;
```

### 3. Test Case Success Rate Over Time

```sql
SELECT
    ec.eval_case_id,
    ec.user_prompt,
    DATE(er.timestamp) as date,
    COUNT(*) as runs,
    AVG(CASE WHEN er.overall_success = 1 THEN 1.0 ELSE 0.0 END) as success_rate
FROM eval_cases ec
JOIN execution_runs er ON ec.eval_case_id = er.eval_case_id
GROUP BY ec.eval_case_id, DATE(er.timestamp)
ORDER BY date DESC, success_rate ASC;
```

### 4. Provider Cost and Performance Comparison

```sql
SELECT
    provider_type,
    provider_model,
    COUNT(*) as total_runs,
    SUM(cost) as total_cost,
    AVG(cost) as avg_cost,
    AVG(time_taken) as avg_time,
    AVG(input_tokens) as avg_input_tokens,
    AVG(output_tokens) as avg_output_tokens,
    AVG(CASE WHEN overall_success = 1 THEN 1.0 ELSE 0.0 END) as success_rate
FROM execution_runs
GROUP BY provider_type, provider_model
ORDER BY total_runs DESC;
```

### 5. Evaluator Score Distribution

```sql
SELECT
    evaluator_name,
    ROUND(score, 1) as score_bucket,
    COUNT(*) as count,
    AVG(score) as avg_score,
    SUM(CASE WHEN passed = 1 THEN 1 ELSE 0 END) as passed_count
FROM evaluator_results
WHERE score IS NOT NULL
GROUP BY evaluator_name, score_bucket
ORDER BY evaluator_name, score_bucket;
```

### 6. Investigate Specific Failure

```sql
SELECT
    er.execution_id,
    er.eval_case_id,
    ec.user_prompt,
    ec.system_instruction,
    er.provider_type,
    er.provider_model,
    er.timestamp,
    actual.assistant_message as actual_response,
    expected.assistant_message as expected_response,
    ev.evaluator_name,
    ev.score,
    ev.threshold,
    ev.error,
    ev.details_json
FROM execution_runs er
JOIN eval_cases ec ON er.eval_case_id = ec.eval_case_id
LEFT JOIN invocations actual ON er.execution_id = actual.execution_id
    AND actual.invocation_type = 'actual'
LEFT JOIN invocations expected ON er.execution_id = expected.execution_id
    AND expected.invocation_type = 'expected'
LEFT JOIN evaluator_results ev ON er.execution_id = ev.execution_id
WHERE er.execution_id = 'exec-XXX';
```

### 7. Most Expensive Test Cases

```sql
SELECT
    ec.eval_case_id,
    ec.user_prompt,
    COUNT(er.execution_id) as runs,
    SUM(er.cost) as total_cost,
    AVG(er.cost) as avg_cost,
    SUM(er.total_tokens) as total_tokens,
    AVG(er.total_tokens) as avg_tokens
FROM eval_cases ec
JOIN execution_runs er ON ec.eval_case_id = er.eval_case_id
GROUP BY ec.eval_case_id
ORDER BY total_cost DESC
LIMIT 20;
```

### 8. Multi-turn Conversation Analysis

```sql
SELECT
    i.execution_id,
    i.invocation_type,
    i.sequence_order,
    i.user_message,
    i.assistant_message
FROM invocations i
JOIN execution_runs er ON i.execution_id = er.execution_id
WHERE er.eval_case_id = 'YOUR_TEST_CASE_ID'
ORDER BY i.execution_id, i.invocation_type, i.sequence_order;
```

## Dashboard Use Cases

### 1. Real-time Monitoring Dashboard
- Track success rates by hour/day
- Monitor cost trends
- Alert on high failure rates
- Display recent failed tests

### 2. Provider Comparison Dashboard
- Side-by-side provider metrics
- Cost per token comparison
- Quality scores by provider
- Speed comparison charts

### 3. Test Case Health Dashboard
- Identify flaky tests (inconsistent pass/fail)
- Track test case success rate trends
- Find slow or expensive tests
- Monitor test coverage

### 4. Investigation Dashboard
- Drill down into specific failures
- Compare expected vs actual responses
- View full conversation history
- Analyze evaluator decisions

### 5. Cost Analysis Dashboard
- Daily/weekly/monthly cost tracking
- Cost per test case
- Cost per provider/model
- Budget forecasting

## Example Analysis Workflows

### Workflow 1: Investigate Why a Test Failed

1. **Find the failure:**
   ```sql
   SELECT * FROM execution_runs WHERE overall_success = 0
   ORDER BY timestamp DESC LIMIT 1;
   ```

2. **Get the test case details:**
   ```sql
   SELECT * FROM eval_cases WHERE eval_case_id = 'case-id';
   ```

3. **Compare expected vs actual:**
   ```sql
   SELECT invocation_type, assistant_message
   FROM invocations
   WHERE execution_id = 'exec-id'
   ORDER BY invocation_type, sequence_order;
   ```

4. **Check evaluator decision:**
   ```sql
   SELECT * FROM evaluator_results
   WHERE execution_id = 'exec-id';
   ```

### Workflow 2: Track Performance Regression

1. **Get baseline performance:**
   ```sql
   SELECT
       eval_case_id,
       AVG(time_taken) as avg_time,
       AVG(cost) as avg_cost
   FROM execution_runs
   WHERE timestamp < '2025-01-01'
   GROUP BY eval_case_id;
   ```

2. **Compare to recent runs:**
   ```sql
   SELECT
       eval_case_id,
       AVG(time_taken) as avg_time,
       AVG(cost) as avg_cost
   FROM execution_runs
   WHERE timestamp >= '2025-01-01'
   GROUP BY eval_case_id;
   ```

3. **Identify significant changes:**
   ```sql
   SELECT
       curr.eval_case_id,
       base.avg_time as baseline_time,
       curr.avg_time as current_time,
       ((curr.avg_time - base.avg_time) / base.avg_time * 100) as pct_change
   FROM (/* baseline query */) base
   JOIN (/* current query */) curr ON base.eval_case_id = curr.eval_case_id
   WHERE ABS((curr.avg_time - base.avg_time) / base.avg_time) > 0.1;
   ```

### Workflow 3: Provider ROI Analysis

Calculate cost-effectiveness of each provider:

```sql
SELECT
    provider_type,
    provider_model,
    COUNT(*) as runs,
    AVG(CASE WHEN overall_success = 1 THEN 1.0 ELSE 0.0 END) as success_rate,
    SUM(cost) as total_cost,
    AVG(cost) as avg_cost,
    AVG(time_taken) as avg_time,
    (SUM(cost) / SUM(CASE WHEN overall_success = 1 THEN 1 ELSE 0 END)) as cost_per_success
FROM execution_runs
GROUP BY provider_type, provider_model
HAVING COUNT(*) >= 10
ORDER BY cost_per_success;
```

## Data Retention and Archival

### Archiving Old Data

```sql
-- Archive runs older than 90 days to a separate table
CREATE TABLE execution_runs_archive AS
SELECT * FROM execution_runs
WHERE timestamp < date('now', '-90 days');

-- Delete from main table
DELETE FROM execution_runs
WHERE timestamp < date('now', '-90 days');

-- Vacuum to reclaim space
VACUUM;
```

### Backup Strategy

```bash
# Daily backups
sqlite3 results.db ".backup 'backup_$(date +%Y%m%d).db'"

# Weekly aggregation
sqlite3 results.db < aggregate_weekly_stats.sql > weekly_summary.csv
```

## Performance Optimization Tips

1. **Use indexes**: All common query patterns are indexed
2. **Limit result sets**: Always use `LIMIT` for large tables
3. **Aggregate at query time**: Pre-aggregate for dashboards
4. **Archive old data**: Keep active dataset reasonable size
5. **Analyze query plans**: Use `EXPLAIN QUERY PLAN`

## Integration with External Tools

### Export to CSV

```bash
sqlite3 -header -csv results.db "SELECT * FROM execution_runs;" > runs.csv
```

### Load into Pandas

```python
import sqlite3
import pandas as pd

conn = sqlite3.connect('results.db')
df = pd.read_sql_query("SELECT * FROM execution_runs", conn)
```

### Grafana Integration

Use SQLite data source plugin to create dashboards directly from the database.

### Custom Dashboards

Build web dashboards using:
- Flask/FastAPI + SQL queries
- Streamlit with SQL integration
- Jupyter notebooks with SQL magic

## Migration from Legacy Schema

If you have data in the old schema (before invocations table), it will still work! The new tables are created automatically, and old tables are untouched. Future runs will populate all tables.

## Summary

The enhanced database schema provides complete evaluation history with full conversation tracking. This enables:

✅ **Complete Investigation**: Drill down into any test execution
✅ **Trend Analysis**: Track performance over time
✅ **Provider Comparison**: Compare costs, speeds, and quality
✅ **Conversation Analysis**: Compare expected vs actual responses
✅ **Cost Management**: Track and optimize spending
✅ **Quality Monitoring**: Track evaluator scores and distributions
✅ **Dashboard Ready**: Build custom monitoring and alerting

Use the provided query patterns and workflows to extract maximum value from your evaluation data!
