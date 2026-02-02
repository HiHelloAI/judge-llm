---
sidebar_position: 5
---

# Database Reporter

Store evaluation results in SQLite for historical tracking, trend analysis, and powerful querying capabilities.

## Overview

The **Database Reporter** persists evaluation results to a SQLite database, enabling long-term storage, trend analysis, and complex queries across multiple evaluation runs.

**Key Features:**
- Persistent storage of all evaluation runs
- Historical trend analysis
- SQL-based querying
- Interactive dashboard generation
- Lightweight (no external database required)
- ACID compliance

## Configuration

### Basic Configuration

```yaml
reporters:
  - type: database
    db_path: ./results.db
```

### Python API

```python
from judge_llm import evaluate

report = evaluate(
    dataset={"loader": "local_file", "paths": ["./tests.json"]},
    providers=[{"type": "gemini", "agent_id": "test"}],
    evaluators=[{"type": "response_evaluator"}],
    reporters=[{"type": "database", "db_path": "./results.db"}]
)
```

### CLI Usage

```bash
# Store results in database
judge-llm run --config test.yaml --report database --db-path results.db

# Multiple reporters
judge-llm run --config test.yaml --report console --report database --db-path results.db
```

## Database Schema

### Tables

#### evaluation_runs
Stores metadata about each evaluation run.

| Column | Type | Description |
|--------|------|-------------|
| run_id | TEXT PRIMARY KEY | Unique identifier for the run |
| timestamp | TEXT | ISO 8601 timestamp |
| total_cost | REAL | Total cost across all test cases |
| total_time | REAL | Total execution time (seconds) |
| success_rate | REAL | Percentage of passed tests (0-1) |
| overall_success | INTEGER | 1 if all tests passed, 0 otherwise |
| total_executions | INTEGER | Number of test cases |
| successful_executions | INTEGER | Number of passed tests |
| failed_executions | INTEGER | Number of failed tests |

#### test_cases
Stores individual test case results.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PRIMARY KEY | Auto-increment ID |
| run_id | TEXT | Foreign key to evaluation_runs |
| eval_id | TEXT | Test case identifier |
| agent_id | TEXT | Agent identifier |
| provider_type | TEXT | Provider type (gemini, openai, etc.) |
| passed | INTEGER | 1 if passed, 0 if failed |
| cost | REAL | Cost for this test case |
| time_taken | REAL | Execution time (seconds) |
| evaluation_results | TEXT | JSON blob with evaluator results |
| conversation_history | TEXT | JSON blob with full conversation |
| source_path | TEXT | Relative file path from dataset root directory (set by directory loader) |

## Querying the Database

### SQL Examples

#### Get Recent Runs

```sql
SELECT
    run_id,
    timestamp,
    success_rate,
    total_cost,
    total_executions
FROM evaluation_runs
ORDER BY timestamp DESC
LIMIT 10;
```

#### Find Expensive Tests

```sql
SELECT
    eval_id,
    agent_id,
    cost,
    time_taken,
    passed
FROM test_cases
WHERE cost > 0.01
ORDER BY cost DESC;
```

#### Success Rate by Provider

```sql
SELECT
    provider_type,
    COUNT(*) as total_tests,
    SUM(passed) as passed_tests,
    ROUND(AVG(passed) * 100, 2) as success_rate
FROM test_cases
GROUP BY provider_type;
```

#### Results by Source Directory

```sql
SELECT
    CASE
        WHEN source_path LIKE '%/%' THEN SUBSTR(source_path, 1, INSTR(source_path, '/') - 1)
        ELSE 'root'
    END as directory,
    COUNT(*) as total_tests,
    SUM(passed) as passed_tests,
    ROUND(AVG(passed) * 100, 2) as success_rate
FROM test_cases
WHERE source_path IS NOT NULL
GROUP BY directory;
```

#### Trend Analysis

```sql
SELECT
    DATE(timestamp) as date,
    AVG(success_rate) as avg_success_rate,
    AVG(total_cost) as avg_cost,
    COUNT(*) as num_runs
FROM evaluation_runs
GROUP BY DATE(timestamp)
ORDER BY date DESC;
```

### Python Querying

```python
import sqlite3
import pandas as pd

# Connect to database
conn = sqlite3.connect("results.db")

# Query as DataFrame
df = pd.read_sql_query("""
    SELECT
        eval_id,
        agent_id,
        cost,
        time_taken,
        passed
    FROM test_cases
    WHERE passed = 0
""", conn)

print(df)

# Aggregate analysis
summary = pd.read_sql_query("""
    SELECT
        provider_type,
        COUNT(*) as count,
        AVG(cost) as avg_cost,
        AVG(time_taken) as avg_latency
    FROM test_cases
    GROUP BY provider_type
""", conn)

print(summary)

conn.close()
```

## Dashboard Generation

The Database Reporter provides instructions for viewing results in an interactive dashboard.

### Generating Dashboard

After running evaluations with the database reporter, you'll see:

```
Results stored in results.db

To view the interactive dashboard:
1. Navigate to the dashboard directory
2. Start a local web server
3. Open the dashboard in your browser
```

### Dashboard Features

- **Overview Charts**: Success rate, cost trends, execution times
- **Test Case Browser**: Drill down into individual test results
- **Directory Grouping**: Executions organized by source directory structure (when using directory loader)
- **Filtering**: By date, provider, agent, source path, pass/fail status
- **SQL Query Interface**: Run custom queries
- **Export**: Download filtered results as CSV/JSON

## Use Cases

### Historical Tracking

```python
# Track improvements over time
from judge_llm import evaluate

# Run daily evaluations
for day in range(30):
    report = evaluate(
        dataset={"loader": "local_file", "paths": ["./tests.json"]},
        providers=[{"type": "gemini", "agent_id": f"v1.{day}"}],
        evaluators=[{"type": "response_evaluator"}],
        reporters=[{"type": "database", "db_path": "./history.db"}]
    )
```

Query trends:
```sql
SELECT
    DATE(timestamp) as date,
    success_rate,
    total_cost
FROM evaluation_runs
ORDER BY timestamp;
```

### A/B Testing

```python
# Compare two models
evaluate(
    dataset={"loader": "local_file", "paths": ["./tests.json"]},
    providers=[
        {"type": "gemini", "agent_id": "model-a"},
        {"type": "openai", "agent_id": "model-b"}
    ],
    evaluators=[{"type": "response_evaluator"}],
    reporters=[{"type": "database", "db_path": "./ab_test.db"}]
)
```

Compare results:
```sql
SELECT
    agent_id,
    AVG(cost) as avg_cost,
    AVG(time_taken) as avg_latency,
    AVG(passed) as success_rate
FROM test_cases
GROUP BY agent_id;
```

### Regression Detection

```python
import sqlite3

def check_regression(db_path, threshold=0.9):
    """Alert if success rate drops below threshold"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get latest run
    cursor.execute("""
        SELECT success_rate
        FROM evaluation_runs
        ORDER BY timestamp DESC
        LIMIT 1
    """)

    latest_rate = cursor.fetchone()[0]

    if latest_rate < threshold:
        print(f"⚠️  REGRESSION DETECTED: {latest_rate:.1%}")
        return False

    print(f"✓ Success rate: {latest_rate:.1%}")
    return True

check_regression("./results.db")
```

### Cost Analysis

```sql
-- Most expensive test cases
SELECT
    eval_id,
    provider_type,
    cost,
    time_taken
FROM test_cases
WHERE cost > (SELECT AVG(cost) * 2 FROM test_cases)
ORDER BY cost DESC;

-- Cost by provider
SELECT
    provider_type,
    SUM(cost) as total_cost,
    COUNT(*) as num_tests,
    AVG(cost) as avg_cost_per_test
FROM test_cases
GROUP BY provider_type;
```

## Best Practices

### 1. Single Database for Related Tests

```yaml
# All tests in same domain
reporters:
  - type: database
    db_path: ./production/evals.db
```

### 2. Separate Databases by Environment

```yaml
# Development
reporters:
  - type: database
    db_path: ./dev/results.db

# Production
reporters:
  - type: database
    db_path: ./prod/results.db
```

### 3. Regular Backups

```bash
# Backup database
cp results.db backups/results-$(date +%Y%m%d).db

# Or use SQLite backup
sqlite3 results.db ".backup backups/results-backup.db"
```

### 4. Archive Old Data

```sql
-- Archive runs older than 90 days
DELETE FROM test_cases
WHERE run_id IN (
    SELECT run_id
    FROM evaluation_runs
    WHERE timestamp < datetime('now', '-90 days')
);

DELETE FROM evaluation_runs
WHERE timestamp < datetime('now', '-90 days');

-- Vacuum to reclaim space
VACUUM;
```

### 5. Combine with Other Reporters

```yaml
reporters:
  - type: console      # Monitor progress
  - type: database     # Long-term storage
    db_path: ./results.db
  - type: html         # Share with team
    output_path: ./report.html
```

## Advanced Queries

### Percentile Analysis

```sql
-- 95th percentile latency
SELECT
    provider_type,
    (SELECT time_taken
     FROM test_cases t2
     WHERE t2.provider_type = t1.provider_type
     ORDER BY time_taken
     LIMIT 1 OFFSET (SELECT COUNT(*) * 0.95 FROM test_cases t3 WHERE t3.provider_type = t1.provider_type)
    ) as p95_latency
FROM test_cases t1
GROUP BY provider_type;
```

### Failure Analysis

```sql
-- Common failure patterns
SELECT
    eval_id,
    COUNT(*) as failure_count,
    AVG(cost) as avg_cost,
    GROUP_CONCAT(DISTINCT provider_type) as providers
FROM test_cases
WHERE passed = 0
GROUP BY eval_id
HAVING failure_count > 1
ORDER BY failure_count DESC;
```

### Time-Series Analysis

```sql
-- Success rate trend (daily)
SELECT
    DATE(timestamp) as date,
    AVG(success_rate) as avg_success_rate,
    MIN(success_rate) as min_success_rate,
    MAX(success_rate) as max_success_rate,
    COUNT(*) as num_runs
FROM evaluation_runs
GROUP BY DATE(timestamp)
ORDER BY date DESC
LIMIT 30;
```

## Troubleshooting

### Database Locked

**Issue:** `database is locked` error

**Cause:** Another process is writing to the database

**Solutions:**
- Ensure only one evaluation runs at a time
- Increase SQLite timeout
- Use Write-Ahead Logging (WAL):

```python
import sqlite3
conn = sqlite3.connect("results.db")
conn.execute("PRAGMA journal_mode=WAL")
```

### Large Database Size

**Issue:** Database file is very large

**Solutions:**
- Archive old data (see Best Practices)
- Run `VACUUM` to reclaim space
- Split by time period:

```yaml
reporters:
  - type: database
    db_path: ./results/{{year}}-{{month}}.db
```

### Schema Changes

**Issue:** Need to add custom fields

**Solution:** Extend the schema:

```python
import sqlite3

conn = sqlite3.connect("results.db")
conn.execute("""
    ALTER TABLE test_cases
    ADD COLUMN custom_field TEXT
""")
conn.commit()
```

## Related Documentation

- [Reporters Overview](./overview)
- [Console Reporter](./console-reporter)
- [JSON Reporter](./json-reporter)
- [HTML Reporter](./html-reporter)
- [Custom Reporters](./custom-reporters)
