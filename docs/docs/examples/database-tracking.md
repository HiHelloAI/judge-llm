---
sidebar_position: 7
---

# Database Tracking

Store, query, and analyze evaluation results using the Database Reporter for comprehensive historical tracking and trend analysis.

## Overview

**Location:** `examples/06-database-reporter/`

**Difficulty:** Intermediate

**What You'll Learn:**
- Storing evaluation results in SQLite database
- Querying historical data with SQL
- Tracking trends over time
- Analyzing costs and performance
- Detecting regressions
- Building custom analytics

## Why Database Reporter?

### Problems with File-Based Reporting

**JSON/HTML reporters:**
- ❌ Each run overwrites previous results
- ❌ Can't compare across runs
- ❌ Manual work to track trends
- ❌ Difficult to analyze aggregate data

### Solution: Database Reporter

- ✅ Append results (preserve history)
- ✅ Query with SQL
- ✅ Track trends automatically
- ✅ Compare runs easily
- ✅ Build dashboards

## Capabilities

- 📊 **Store all evaluation results** in structured SQLite database
- 📈 **Track trends** over time (cost, performance, success rates)
- 🔍 **Query historical data** using SQL
- 💰 **Analyze costs** by provider, model, and test case
- 🎯 **Monitor evaluator performance** across runs
- 📉 **Detect regressions** by comparing current vs. historical results
- 🏗️ **Build dashboards** using database as backend

## Files

```
06-database-reporter/
├── config.yaml                # Configuration with database reporter
├── math_questions.evalset.json  # Test cases
├── run_evaluation.py          # Evaluation runner
├── query_results.py           # Analysis queries
├── run.sh                     # Convenience script
└── README.md                  # Instructions
```

## Quick Start

### 1. Set up API key

```bash
export GEMINI_API_KEY="your-api-key-here"
```

### 2. Run evaluation

```bash
cd examples/06-database-reporter
./run.sh
# Or: python run_evaluation.py
# Or: judge-llm run --config config.yaml
```

### 3. Query results

```bash
python query_results.py
```

## Configuration

### config.yaml

```yaml
agent:
  name: math_tutor_agent
  description: "Math tutoring agent"
  num_runs: 2  # Run each test twice for consistency check

dataset:
  loader: local_file
  paths:
    - ./math_questions.evalset.json

providers:
  - type: gemini
    agent_id: math_tutor_agent
    model: gemini-2.0-flash-exp
    temperature: 0.7

evaluators:
  - type: response_evaluator
    config:
      similarity_threshold: 0.85

reporters:
  - type: console         # Real-time output
  - type: database        # SQLite storage
    db_path: "../../reports/06-database-reporter/results.db"
  - type: html            # Visual report
    output_path: "../../reports/06-database-reporter/report.html"
```

### Database Reporter Configuration

```yaml
reporters:
  - type: database
    db_path: "path/to/results.db"
    # Optional settings:
    # auto_create_tables: true  # Create tables if not exist (default)
    # append_results: true      # Append vs overwrite (default)
```

**Key Points:**
- Creates SQLite database at specified path
- Auto-creates tables on first run
- Appends new results (preserves history)
- No data loss between runs

## Database Schema

### Table 1: `reports`

High-level summary of each evaluation run:

```sql
CREATE TABLE reports (
    report_id TEXT PRIMARY KEY,
    generated_at TIMESTAMP,
    total_cost REAL,
    total_time REAL,
    success_rate REAL,
    overall_success BOOLEAN,
    summary_json TEXT,
    metadata TEXT
);
```

**Fields:**
- `report_id`: Unique identifier for each run
- `generated_at`: Timestamp of evaluation
- `total_cost`: Sum of all test case costs
- `total_time`: Total execution time
- `success_rate`: Percentage of passing tests
- `overall_success`: True if all tests passed
- `summary_json`: Full summary as JSON
- `metadata`: Additional context

### Table 2: `execution_runs`

Individual test case executions:

```sql
CREATE TABLE execution_runs (
    execution_id TEXT PRIMARY KEY,
    report_id TEXT,
    eval_case_id TEXT,
    provider_type TEXT,
    cost REAL,
    time_taken REAL,
    token_usage INTEGER,
    overall_success BOOLEAN,
    provider_result TEXT,
    eval_case_data TEXT,
    FOREIGN KEY (report_id) REFERENCES reports(report_id)
);
```

**Fields:**
- `execution_id`: Unique execution identifier
- `eval_case_id`: Test case identifier
- `provider_type`: Which provider was used (gemini, openai, etc.)
- `cost`: Cost for this execution
- `time_taken`: Execution time in seconds
- `token_usage`: Number of tokens used
- `overall_success`: Pass/fail status
- `provider_result`: Full provider response as JSON
- `eval_case_data`: Test case data as JSON

### Table 3: `evaluator_results`

Detailed evaluator outcomes:

```sql
CREATE TABLE evaluator_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    execution_id TEXT,
    evaluator_name TEXT,
    evaluator_type TEXT,
    success BOOLEAN,
    passed BOOLEAN,
    score REAL,
    threshold REAL,
    result_data TEXT,
    error_message TEXT,
    FOREIGN KEY (execution_id) REFERENCES execution_runs(execution_id)
);
```

**Fields:**
- `evaluator_name`: Evaluator identifier
- `evaluator_type`: Type of evaluator
- `success`: Whether evaluator ran successfully
- `passed`: Whether test passed this evaluator
- `score`: Numeric score (0-1)
- `threshold`: Required threshold
- `result_data`: Full result as JSON
- `error_message`: Error if evaluator failed

## Example Queries

### 1. Overall Summary

```sql
SELECT
    COUNT(*) as total_runs,
    SUM(total_cost) as cumulative_cost,
    AVG(total_time) as avg_time,
    AVG(success_rate) as avg_success_rate
FROM reports;
```

**Output:**
```
total_runs: 5
cumulative_cost: $0.0450
avg_time: 8.5s
avg_success_rate: 92.5%
```

### 2. Results by Test Case

```sql
SELECT
    eval_case_id,
    COUNT(*) as runs,
    AVG(cost) as avg_cost,
    AVG(time_taken) as avg_time,
    SUM(CASE WHEN overall_success = 1 THEN 1 ELSE 0 END) as passed,
    COUNT(*) - SUM(CASE WHEN overall_success = 1 THEN 1 ELSE 0 END) as failed
FROM execution_runs
GROUP BY eval_case_id
ORDER BY avg_cost DESC;
```

**Output:**
```
eval_case_id              | runs | avg_cost | avg_time | passed | failed
--------------------------|------|----------|----------|--------|-------
complex_math_problem      |  10  |  $0.0025 |  2.5s    |   8    |   2
simple_addition           |  10  |  $0.0008 |  1.1s    |   10   |   0
word_problem              |  10  |  $0.0018 |  1.8s    |   9    |   1
```

### 3. Evaluator Performance

```sql
SELECT
    evaluator_name,
    evaluator_type,
    COUNT(*) as total,
    SUM(passed) as passed,
    AVG(score) as avg_score,
    AVG(threshold) as threshold
FROM evaluator_results
GROUP BY evaluator_name, evaluator_type
ORDER BY avg_score DESC;
```

**Output:**
```
evaluator_name      | type              | total | passed | avg_score | threshold
--------------------|-------------------|-------|--------|-----------|----------
response_evaluator  | response          |  30   |  27    |  0.87     |  0.85
cost_evaluator      | cost              |  30   |  30    |  1.00     |  N/A
latency_evaluator   | latency           |  30   |  28    |  0.93     |  N/A
```

### 4. Daily Cost Trends

```sql
SELECT
    DATE(generated_at) as date,
    SUM(total_cost) as daily_cost,
    COUNT(*) as runs,
    AVG(success_rate) as avg_success_rate
FROM reports
GROUP BY DATE(generated_at)
ORDER BY date DESC;
```

**Output:**
```
date       | daily_cost | runs | avg_success_rate
-----------|------------|------|------------------
2025-10-19 |  $0.0180   |  3   |  95.0%
2025-10-18 |  $0.0150   |  2   |  90.0%
2025-10-17 |  $0.0120   |  2   |  92.5%
```

### 5. Provider Comparison

```sql
SELECT
    provider_type,
    COUNT(*) as runs,
    AVG(cost) as avg_cost,
    AVG(time_taken) as avg_time,
    AVG(CASE WHEN overall_success = 1 THEN 1.0 ELSE 0.0 END) as success_rate
FROM execution_runs
GROUP BY provider_type;
```

**Output:**
```
provider_type | runs | avg_cost | avg_time | success_rate
--------------|------|----------|----------|-------------
gemini        |  20  |  $0.0015 |  1.5s    |  95.0%
openai        |  15  |  $0.0025 |  1.2s    |  93.3%
anthropic     |  10  |  $0.0035 |  2.1s    |  100.0%
```

### 6. Detect Regressions

```sql
WITH recent_runs AS (
    SELECT AVG(success_rate) as recent_success
    FROM reports
    WHERE generated_at >= datetime('now', '-7 days')
),
historical_runs AS (
    SELECT AVG(success_rate) as historical_success
    FROM reports
    WHERE generated_at < datetime('now', '-7 days')
)
SELECT
    recent_success,
    historical_success,
    (recent_success - historical_success) as change,
    CASE
        WHEN (recent_success - historical_success) < -5 THEN 'REGRESSION'
        WHEN (recent_success - historical_success) > 5 THEN 'IMPROVEMENT'
        ELSE 'STABLE'
    END as status
FROM recent_runs, historical_runs;
```

## Running Multiple Times

Build historical data by running repeatedly:

```bash
# Run 1
python run_evaluation.py

# Wait, make changes, run again
python run_evaluation.py

# Run 3
python run_evaluation.py

# Analyze trends
python query_results.py
```

Each run appends to the database - no data loss!

## Using the Database

### Method 1: SQLite CLI

```bash
# Open database
sqlite3 ../../reports/06-database-reporter/results.db

# List tables
.tables

# Describe table
.schema execution_runs

# Run query
SELECT * FROM reports;

# Export to CSV
.mode csv
.output results.csv
SELECT * FROM execution_runs;
.quit
```

### Method 2: Python

```python
import sqlite3
import pandas as pd

# Connect
conn = sqlite3.connect('results.db')

# Query
df = pd.read_sql_query("""
    SELECT eval_case_id, AVG(cost) as avg_cost
    FROM execution_runs
    GROUP BY eval_case_id
""", conn)

print(df)
conn.close()
```

### Method 3: GUI Tools

Open with any SQLite tool:
- [DB Browser for SQLite](https://sqlitebrowser.org/) (Free)
- [DataGrip](https://www.jetbrains.com/datagrip/)
- [DBeaver](https://dbeaver.io/) (Free)
- VS Code SQLite extension

## Use Cases

### 1. Cost Tracking

Monitor spending per test case:

```bash
sqlite3 results.db \
  "SELECT eval_case_id, AVG(cost) as avg_cost
   FROM execution_runs
   GROUP BY eval_case_id
   ORDER BY avg_cost DESC
   LIMIT 10"
```

**Use:** Identify expensive tests to optimize

### 2. Performance Monitoring

Track execution times:

```bash
sqlite3 results.db \
  "SELECT eval_case_id, AVG(time_taken) as avg_time
   FROM execution_runs
   GROUP BY eval_case_id
   ORDER BY avg_time DESC
   LIMIT 10"
```

**Use:** Find slow tests

### 3. Success Rate Trends

Monitor quality over time:

```bash
sqlite3 results.db \
  "SELECT DATE(generated_at) as date, success_rate
   FROM reports
   ORDER BY generated_at DESC
   LIMIT 30"
```

**Use:** Detect regressions early

### 4. Evaluator Analysis

Which evaluators fail most?

```bash
sqlite3 results.db \
  "SELECT evaluator_name,
          COUNT(*) as total,
          SUM(passed) as passed,
          ROUND(100.0 * SUM(passed) / COUNT(*), 2) as pass_rate
   FROM evaluator_results
   GROUP BY evaluator_name"
```

**Use:** Tune evaluation criteria

## Advanced: Build a Dashboard

### Using Streamlit

```python
# dashboard.py
import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

st.title("LLM Evaluation Dashboard")

conn = sqlite3.connect('results.db')

# Cost over time
cost_df = pd.read_sql_query("""
    SELECT DATE(generated_at) as date, SUM(total_cost) as cost
    FROM reports
    GROUP BY DATE(generated_at)
    ORDER BY date
""", conn)

fig = px.line(cost_df, x='date', y='cost', title='Daily Cost')
st.plotly_chart(fig)

# Success rate
success_df = pd.read_sql_query("""
    SELECT DATE(generated_at) as date, AVG(success_rate) as rate
    FROM reports
    GROUP BY DATE(generated_at)
    ORDER BY date
""", conn)

fig = px.line(success_df, x='date', y='rate', title='Success Rate')
st.plotly_chart(fig)

conn.close()
```

Run:
```bash
streamlit run dashboard.py
```

## Expected Output

After running evaluation:

```
📊 Math Tutor Evaluation Results
================================================================================

📋 OVERALL SUMMARY
--------------------------------------------------------------------------------
Total evaluation reports: 3
Total test executions: 24
Successful executions: 22 (91.7%)

Cost metrics:
  Total cost: $0.0450
  Average cost per run: $0.0019

Time metrics:
  Total time: 45.30s
  Average time per run: 1.89s

📊 BY TEST CASE
--------------------------------------------------------------------------------
eval_case_id           | runs | avg_cost | avg_time | passed | failed
-----------------------|------|----------|----------|--------|-------
math_001_addition      |  6   |  $0.0008 |  1.1s    |  6     |  0
math_002_subtraction   |  6   |  $0.0010 |  1.3s    |  5     |  1
math_003_multiplication|  6   |  $0.0012 |  1.5s    |  6     |  0
math_004_division      |  6   |  $0.0015 |  2.2s    |  5     |  1

🎯 BY EVALUATOR
--------------------------------------------------------------------------------
evaluator_name       | total | avg_score | pass_rate
---------------------|-------|-----------|----------
response_evaluator   |  24   |  0.87     |  91.7%
cost_evaluator       |  24   |  1.00     |  100.0%
latency_evaluator    |  24   |  0.95     |  95.8%
```

## Best Practices

### 1. Regular Runs

Run evaluations regularly to build trends:

```bash
# Cron job: daily at midnight
0 0 * * * cd /path/to/judge_llm && python run_evaluation.py
```

### 2. Backup Database

```bash
# Backup before major changes
cp results.db results.backup.$(date +%Y%m%d).db
```

### 3. Archive Old Data

```sql
-- Archive runs older than 90 days
DELETE FROM reports WHERE generated_at < datetime('now', '-90 days');
VACUUM;  -- Reclaim space
```

### 4. Index for Performance

```sql
-- Add indexes for common queries
CREATE INDEX idx_generated_at ON reports(generated_at);
CREATE INDEX idx_eval_case_id ON execution_runs(eval_case_id);
CREATE INDEX idx_provider_type ON execution_runs(provider_type);
```

## Next Steps

After mastering database tracking:

1. **Run multiple times** to build historical data
2. **Try different providers** to compare performance
3. **Create custom queries** for your specific analytics
4. **Build a dashboard** (Streamlit, Flask, Grafana)
5. **Set up alerts** for regressions or cost spikes

## Related Documentation

- [Database Reporter](../reporters/database-reporter)
- [Reporters Overview](../reporters/overview)
- [Configuration Guide](../guides/configuration)
- [Python API](../guides/python-api)
