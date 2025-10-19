---
sidebar_position: 3
---

# HTML Reporter

Generate interactive, self-contained HTML reports with detailed test results, charts, and drill-down capabilities.

## Overview

The **HTML Reporter** creates a standalone HTML file with an interactive dashboard for analyzing evaluation results. Perfect for sharing with team members and detailed result analysis.

**Key Features:**
- Self-contained single HTML file (works offline)
- Interactive UI with drill-down details
- Color-coded test results
- Execution timeline and metrics
- Dark mode support
- Responsive design

## Configuration

### Basic Configuration

```yaml
reporters:
  - type: html
    output_path: ./report.html
```

### Full Configuration

```yaml
reporters:
  - type: html
    output_path: ./reports/eval-{{date}}.html
```

### CLI Usage

```bash
# Generate HTML report
judge-llm run --config test.yaml --report html --output report.html

# Multiple reports
judge-llm run --config test.yaml --report console --report html --output report.html
```

### Python API

```python
from judge_llm import evaluate

report = evaluate(
    dataset={"loader": "local_file", "paths": ["./tests.json"]},
    providers=[{"type": "gemini", "agent_id": "test"}],
    evaluators=[{"type": "response_evaluator"}],
    reporters=[
        {"type": "console"},
        {"type": "html", "output_path": "./report.html"}
    ]
)
```

## Report Structure

### Header Section
- Evaluation summary (total tests, pass rate, cost, time)
- Provider and evaluator configuration
- Timestamp and metadata

### Sidebar
- Summary metrics
- Test case list with status indicators
- Click to navigate to specific test

### Main Panel
- Detailed test case view
- Input/output comparison
- Evaluator scores and feedback
- Provider metadata (tokens, cost, latency)
- Conversation history for multi-turn tests

### Footer
- Attribution (sql.js, Chart.js)
- Copyright information
- Links to documentation

## Use Cases

### Sharing with Team

```yaml
# Generate report for code review
reporters:
  - type: html
    output_path: ./reports/pr-{{pr_number}}.html
```

Share the HTML file via:
- Email attachment
- Slack/Teams upload
- GitHub PR comment
- Internal wiki

### Archiving Results

```yaml
# Timestamped reports
reporters:
  - type: html
    output_path: ./archive/eval-{{timestamp}}.html
```

Keep historical reports organized:
```
archive/
  ├── eval-2025-01-15-10-30.html
  ├── eval-2025-01-15-14-20.html
  └── eval-2025-01-16-09-15.html
```

### Presentation Materials

- Open HTML in browser
- Take screenshots for slides
- Embed in documentation
- Print to PDF

## Features

### Interactive Navigation

Click on any test case in sidebar to view:
- Full conversation history
- Evaluator-by-evaluator breakdown
- Cost and latency metrics
- Input/output comparison

### Color-Coded Status

- **Green** - Test passed all evaluators
- **Red** - Test failed one or more evaluators
- **Yellow** - Warnings or partial success

### Responsive Design

Works on:
- Desktop browsers
- Tablets
- Mobile devices
- Printed pages

### Dark Mode

Toggle between light and dark themes for comfortable viewing.

## Best Practices

### 1. Organized Output

Use templates in paths:

```yaml
reporters:
  - type: html
    output_path: ./reports/{{date}}/{{agent_id}}.html
```

### 2. Multiple HTML Reports

Different reports for different audiences:

```yaml
reporters:
  # Summary for management
  - type: html
    output_path: ./summary-report.html
    
  # Detailed for engineers  
  - type: html
    output_path: ./detailed-report.html
```

### 3. Combine with Database

HTML for sharing, database for querying:

```yaml
reporters:
  - type: html
    output_path: ./report.html
  - type: database
    db_path: ./results.db
```

### 4. CI/CD Artifacts

```yaml
# .github/workflows/eval.yml
- name: Run Evaluations
  run: judge-llm run --config test.yaml --report html --output report.html

- name: Upload Report
  uses: actions/upload-artifact@v3
  with:
    name: evaluation-report
    path: report.html
```

## Troubleshooting

### File Not Found

**Issue:** HTML file not created

**Solutions:**
- Check output directory exists
- Verify write permissions
- Check disk space

### Report Won't Open

**Issue:** Browser security warnings

**Cause:** Some browsers block local HTML files

**Solutions:**
- Use `file:///` protocol: `file:///path/to/report.html`
- Serve via HTTP: `python -m http.server`
- Open with different browser

### Large File Size

**Issue:** HTML file is very large

**Cause:** Many test cases with long conversations

**Solutions:**
- Split into multiple evaluation runs
- Use JSON + separate viewer
- Use database reporter instead

## Related Documentation

- [Reporters Overview](./overview)
- [Console Reporter](./console-reporter)
- [JSON Reporter](./json-reporter)
- [Database Reporter](./database-reporter)
