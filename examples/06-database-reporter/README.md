# Example: Database Reporter

This example demonstrates how to use the **Database Reporter** to store evaluation results in a SQLite database for comprehensive analysis, historical tracking, and trend monitoring.

## Overview

The Database Reporter enables you to:
- 📊 **Store all evaluation results** in a structured SQLite database
- 📈 **Track trends** over time (cost, performance, success rates)
- 🔍 **Query historical data** using SQL
- 💰 **Analyze costs** by provider, model, and test case
- 🎯 **Monitor evaluator performance** across runs
- 📉 **Detect regressions** by comparing current vs. historical results

## Files in This Example

```
06-database-reporter/
├── config.yaml              # Evaluation configuration with database reporter
├── math_questions.evalset.json  # Test cases (math tutoring questions)
├── run_evaluation.py        # Script to run the evaluation
├── query_results.py         # Script to query and analyze database
├── run.sh                   # Convenience script to run both
└── README.md               # This file
```

## Quick Start

### 1. Set up API key

```bash
export GEMINI_API_KEY="your-api-key-here"
```

### 2. Run the evaluation

**Option A: Using the convenience script**
```bash
./run.sh
```

**Option B: Using Python directly**
```bash
python run_evaluation.py
```

**Option C: Using CLI**
```bash
judge-llm evaluate --config config.yaml
```

### 3. Query the results

```bash
python query_results.py
```

## What This Example Does

### Evaluation Configuration

The [config.yaml](config.yaml) sets up:
- **Provider**: Gemini (gemini-2.0-flash-exp)
- **Test cases**: 4 math questions
- **Runs**: 2 runs per test case (to test consistency)
- **Evaluators**: Response evaluator with 0.85 threshold
- **Reporters**: Console + Database + HTML

### Database Reporter Configuration

```yaml
reporters:
  - type: database
    db_path: "../../reports/06-database-reporter/results.db"
```

This configuration:
- Creates a SQLite database at the specified path
- Auto-creates tables if they don't exist
- Appends new results to existing database (preserves history)
- Stores structured data for efficient querying

### Generated Database Schema

The database contains three main tables:

**`reports`** - High-level summary
- report_id, generated_at, total_cost, total_time
- success_rate, overall_success, summary_json

**`execution_runs`** - Individual test executions
- execution_id, eval_case_id, provider_type
- cost, time_taken, token_usage, success status
- Full provider results and eval case data as JSON

**`evaluator_results`** - Evaluation outcomes
- evaluator_name, evaluator_type
- success, passed, score, threshold
- Detailed results and error messages

## Example Queries

The [query_results.py](query_results.py) script demonstrates several useful queries:

### 1. Overall Summary
```sql
SELECT
    COUNT(*) as total_runs,
    SUM(cost) as total_cost,
    AVG(time_taken) as avg_time
FROM execution_runs
```

### 2. Results by Test Case
```sql
SELECT
    eval_case_id,
    COUNT(*) as runs,
    AVG(cost) as avg_cost,
    SUM(CASE WHEN overall_success = 1 THEN 1 ELSE 0 END) as passed
FROM execution_runs
GROUP BY eval_case_id
```

### 3. Evaluator Performance
```sql
SELECT
    evaluator_name,
    COUNT(*) as total,
    AVG(score) as avg_score
FROM evaluator_results
GROUP BY evaluator_name
```

### 4. Daily Cost Trends
```sql
SELECT
    DATE(generated_at) as date,
    SUM(total_cost) as daily_cost,
    AVG(success_rate) as avg_success_rate
FROM reports
GROUP BY DATE(generated_at)
```

## Running Multiple Times

To build historical data, run the evaluation multiple times:

```bash
# Run 1
python run_evaluation.py

# Run 2 (results are appended to database)
python run_evaluation.py

# Run 3
python run_evaluation.py

# Analyze trends
python query_results.py
```

Each run creates a new report in the database while preserving all historical data.

## Use Cases Demonstrated

### 1. Cost Tracking
Monitor how much each evaluation costs and identify expensive test cases:
```bash
sqlite3 ../../reports/06-database-reporter/results.db \
  "SELECT eval_case_id, AVG(cost) as avg_cost
   FROM execution_runs
   GROUP BY eval_case_id
   ORDER BY avg_cost DESC"
```

### 2. Performance Monitoring
Track execution times to identify slow tests:
```bash
sqlite3 ../../reports/06-database-reporter/results.db \
  "SELECT eval_case_id, AVG(time_taken) as avg_time
   FROM execution_runs
   GROUP BY eval_case_id
   ORDER BY avg_time DESC"
```

### 3. Success Rate Trends
Monitor if success rates are improving or degrading:
```bash
sqlite3 ../../reports/06-database-reporter/results.db \
  "SELECT generated_at, success_rate
   FROM reports
   ORDER BY generated_at"
```

### 4. Evaluator Analysis
Understand which evaluators pass/fail most often:
```bash
sqlite3 ../../reports/06-database-reporter/results.db \
  "SELECT evaluator_name,
          COUNT(*) as total,
          SUM(passed) as passed
   FROM evaluator_results
   GROUP BY evaluator_name"
```

## Extending This Example

### Compare Multiple Providers

Modify [config.yaml](config.yaml) to test multiple providers:

```yaml
providers:
  - type: gemini
    agent_id: math_tutor_agent
    model: gemini-2.0-flash-exp

  - type: openai
    agent_id: math_tutor_agent
    model: gpt-4

  - type: anthropic
    agent_id: math_tutor_agent
    model: claude-3-sonnet
```

Then query to compare:
```sql
SELECT
    provider_type,
    COUNT(*) as runs,
    AVG(cost) as avg_cost,
    AVG(time_taken) as avg_time,
    AVG(CASE WHEN overall_success = 1 THEN 1.0 ELSE 0.0 END) as success_rate
FROM execution_runs
GROUP BY provider_type
```

### Track Model Versions

Add model version to metadata and track performance over time as models improve.

### Build Custom Dashboard

Use the database as a backend for custom dashboards:
- Flask/FastAPI web app
- Streamlit dashboard
- Jupyter notebook analysis
- Export to visualization tools (Tableau, Power BI, etc.)

## Working with the Database

### Using SQLite CLI

```bash
# Open the database
sqlite3 ../../reports/06-database-reporter/results.db

# List all tables
.tables

# Show table schema
.schema execution_runs

# Run a query
SELECT * FROM reports;

# Export to CSV
.mode csv
.output results.csv
SELECT * FROM execution_runs;
.quit
```

### Using Python

```python
import sqlite3

conn = sqlite3.connect('results.db')
cursor = conn.cursor()

cursor.execute("SELECT * FROM reports")
for row in cursor.fetchall():
    print(row)

conn.close()
```

### Using GUI Tools

Open the database with any SQLite tool:
- [DB Browser for SQLite](https://sqlitebrowser.org/) (Free)
- [DataGrip](https://www.jetbrains.com/datagrip/) (JetBrains)
- [DBeaver](https://dbeaver.io/) (Free)
- VS Code with SQLite extension

## Expected Output

After running the evaluation, you should see:

1. **Console output** with real-time progress
2. **HTML report** at `../../reports/06-database-reporter/report.html`
3. **SQLite database** at `../../reports/06-database-reporter/results.db`

Example query output:
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
```

## Next Steps

1. **Run multiple times** to build historical data
2. **Modify test cases** to test different scenarios
3. **Try different providers** to compare performance
4. **Create custom queries** for your specific analysis needs
5. **Build a dashboard** on top of the database

## Tips

- Run evaluations regularly to track trends
- Use the database to detect regressions before deploying
- Compare costs across different providers/models
- Archive old databases for long-term historical analysis
- Consider backing up the database periodically

## Resources

- [Database Reporter Documentation](../../test_db_reporter/README.md)
- [Query Examples](../../test_db_reporter/query_db.py)
- [SQLite Documentation](https://www.sqlite.org/docs.html)
