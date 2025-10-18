# Database Reporter

The Database Reporter stores evaluation results in a SQLite database for comprehensive analysis, historical tracking, and querying.

## Features

- **Auto-initialization**: Automatically creates database and tables if they don't exist
- **Append-only**: Preserves historical data across multiple evaluation runs
- **Zero configuration**: Works out-of-the-box with SQLite (no additional dependencies)
- **Structured storage**: Normalized schema with proper indexing for efficient queries
- **Flexible querying**: Use SQL to analyze results, trends, costs, and performance

## Quick Start

### 1. Add to Configuration

Add the database reporter to your `config.yaml`:

```yaml
reporters:
  - type: database
    db_path: ./results.db  # Optional, defaults to ./judge_llm_results.db
```

### 2. Run Evaluation

```bash
judge-llm evaluate --config config.yaml
```

The database will be automatically created with all necessary tables and indexes.

### 3. Query Results

Use the provided query script or any SQLite tool:

```bash
python query_db.py ./results.db
```

Or use the SQLite CLI:

```bash
sqlite3 results.db "SELECT * FROM reports;"
```

## Database Schema

### Tables

#### `reports`
High-level summary of evaluation runs
- `report_id` (TEXT, PRIMARY KEY): Unique report identifier
- `generated_at` (TEXT): Timestamp when report was generated
- `total_cost` (REAL): Total cost across all executions
- `total_time` (REAL): Total time in seconds
- `success_rate` (REAL): Overall success rate (0.0-1.0)
- `overall_success` (INTEGER): 1 if all tests passed, 0 otherwise
- `summary_json` (TEXT): Additional summary metadata as JSON

#### `execution_runs`
Individual test executions
- `execution_id` (TEXT, PRIMARY KEY): Unique execution identifier
- `report_id` (TEXT, FOREIGN KEY): Associated report
- `run_number` (INTEGER): Run number (for multiple runs)
- `eval_set_id` (TEXT): Evaluation set identifier
- `eval_case_id` (TEXT): Evaluation case identifier
- `provider_type` (TEXT): LLM provider type (gemini, openai, etc.)
- `overall_success` (INTEGER): 1 if execution succeeded, 0 otherwise
- `timestamp` (TEXT): Execution timestamp
- `cost` (REAL): Execution cost
- `time_taken` (REAL): Execution time in seconds
- `token_usage_json` (TEXT): Token usage details as JSON
- `provider_result_json` (TEXT): Full provider result as JSON
- `eval_case_json` (TEXT): Original eval case as JSON
- `metadata_json` (TEXT): Additional metadata as JSON

#### `evaluator_results`
Evaluation outcomes
- `id` (INTEGER, PRIMARY KEY): Auto-incrementing ID
- `execution_id` (TEXT, FOREIGN KEY): Associated execution
- `evaluator_name` (TEXT): Name of the evaluator
- `evaluator_type` (TEXT): Type of evaluator
- `success` (INTEGER): 1 if evaluator ran successfully, 0 otherwise
- `passed` (INTEGER): 1 if evaluation passed, 0 otherwise
- `score` (REAL): Evaluation score (if applicable)
- `threshold` (REAL): Pass/fail threshold (if applicable)
- `details_json` (TEXT): Detailed evaluation results as JSON
- `error` (TEXT): Error message (if evaluation failed)

### Indexes

The following indexes are created automatically for query performance:
- `idx_execution_runs_report_id`: Speed up joins with reports
- `idx_execution_runs_timestamp`: Enable time-based queries
- `idx_execution_runs_provider`: Filter by provider type
- `idx_evaluator_results_execution_id`: Speed up joins with executions

## Example Queries

### Get all reports with summary statistics
```sql
SELECT
    report_id,
    generated_at,
    total_cost,
    total_time,
    success_rate,
    overall_success
FROM reports
ORDER BY generated_at DESC;
```

### Analyze provider performance
```sql
SELECT
    provider_type,
    COUNT(*) as total_runs,
    SUM(CASE WHEN overall_success = 1 THEN 1 ELSE 0 END) as successful_runs,
    AVG(cost) as avg_cost,
    AVG(time_taken) as avg_time
FROM execution_runs
GROUP BY provider_type;
```

### Find failed evaluations
```sql
SELECT
    er.evaluator_name,
    er.evaluator_type,
    er.error,
    ex.execution_id,
    ex.eval_case_id,
    ex.provider_type
FROM evaluator_results er
JOIN execution_runs ex ON er.execution_id = ex.execution_id
WHERE er.passed = 0
ORDER BY ex.timestamp DESC;
```

### Track cost over time
```sql
SELECT
    DATE(timestamp) as date,
    SUM(cost) as daily_cost,
    COUNT(*) as daily_runs
FROM execution_runs
GROUP BY DATE(timestamp)
ORDER BY date DESC;
```

### Compare evaluator performance
```sql
SELECT
    evaluator_name,
    COUNT(*) as total_evaluations,
    SUM(CASE WHEN passed = 1 THEN 1 ELSE 0 END) as passed_count,
    AVG(score) as avg_score
FROM evaluator_results
GROUP BY evaluator_name;
```

## Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `db_path` | string | `./judge_llm_results.db` | Path to SQLite database file |

## Use Cases

### Historical Tracking
Store results from multiple evaluation runs to track performance trends over time.

### Cost Analysis
Analyze spending patterns across different providers, models, and test cases.

### Performance Monitoring
Track execution times and identify slow-running test cases.

### Regression Detection
Compare current results against historical baselines to detect regressions.

### Provider Comparison
Aggregate data to compare different LLM providers on cost, performance, and accuracy.

### Custom Reporting
Query the database to generate custom reports and dashboards tailored to your needs.

## Working with the Database

### Using Python
```python
import sqlite3

conn = sqlite3.connect('results.db')
cursor = conn.cursor()

# Query example
cursor.execute("""
    SELECT provider_type, AVG(cost) as avg_cost
    FROM execution_runs
    GROUP BY provider_type
""")

for row in cursor.fetchall():
    print(f"{row[0]}: ${row[1]:.4f}")

conn.close()
```

### Using SQLite CLI
```bash
# Open database
sqlite3 results.db

# List tables
.tables

# Show schema
.schema reports

# Run query
SELECT * FROM reports;

# Export to CSV
.mode csv
.output results.csv
SELECT * FROM execution_runs;
.quit
```

### Using Database Tools
Any SQLite-compatible tool can be used:
- [DB Browser for SQLite](https://sqlitebrowser.org/)
- [DataGrip](https://www.jetbrains.com/datagrip/)
- [DBeaver](https://dbeaver.io/)
- VS Code SQLite extension

## Integration with Other Reporters

The database reporter works alongside existing reporters:

```yaml
reporters:
  - type: console        # Real-time console output
  - type: database       # Store to database
  - type: html           # Generate HTML report
    output_path: ./report.html
  - type: json           # Export JSON
    output_path: ./report.json
```

All reporters receive the same evaluation data and run independently.

## Future Enhancements

Potential additions for future versions:
- PostgreSQL/MySQL support (via SQLAlchemy)
- Built-in query API (REST endpoints)
- Web-based dashboard
- Automated trend analysis and alerts
- Export to other formats (CSV, Excel)

## Testing

Run the included test script to verify the database reporter:

```bash
cd test_db_reporter
python test_db_direct.py
```

This creates a sample database with test data and verifies all tables and indexes are created correctly.
