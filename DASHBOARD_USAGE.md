# Dashboard Usage Guide

## Overview

The Judge LLM framework includes a powerful, self-contained HTML dashboard for visualizing evaluation results. The dashboard (`monitor.html`) is stored as part of the module and can be launched via CLI.

## File Location

```
judge_llm/
└── templates/
    └── monitor.html  (93KB - Professional monitoring dashboard)
```

## Quick Start

### Method 1: CLI Command (Recommended)

```bash
# Generate and open dashboard in browser
judge-llm dashboard

# Or using Python module
python -m judge_llm.cli dashboard
```

### Method 2: Direct Access

The template is available at:
```
judge_llm/templates/monitor.html
```

## CLI Options

### Basic Usage
```bash
judge-llm dashboard [OPTIONS]
```

### Available Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--db` | `-d` | Path to SQLite database file | None |
| `--output` | `-o` | Output path for dashboard HTML | `./dashboard.html` |
| `--no-browser` | | Don't auto-open browser | Opens automatically |

### Examples

```bash
# Generate with custom output path
judge-llm dashboard --output ~/my-results/dashboard.html

# Specify database file (for reference)
judge-llm dashboard --db ./evaluation_results.db

# Generate without opening browser
judge-llm dashboard --no-browser

# Combine options
judge-llm dashboard --db ./results.db --output ./reports/dashboard.html
```

## Features

### 📊 Professional Design
- Clean gray/white color scheme
- Left sidebar navigation
- Responsive layout
- Modern UI components

### 📈 Views Available

1. **Monitor** - Overview with key metrics and charts
2. **Agents** - Agent performance tracking over time
3. **Executions** - Complete execution history (date-grouped)
4. **Providers** - Provider comparison
5. **Test Cases** - Test case performance
6. **Evaluators** - Evaluator statistics
7. **Datasets** - Dataset overview
8. **Reports** - Report history

### 🎯 Key Features

- **Date Grouping**: Executions grouped by date, latest first
- **Expandable Details**: Click any execution to see full details
- **Evaluators**: View all evaluator results with scores
- **Chat Conversations**: Beautiful side-by-side expected vs actual
- **Test Cases Table**: All test cases for each agent
- **Evaluator Charts**: Score vs threshold visualization
- **Time Filters**: 1d/3d/7d/30d/All

### 🔒 Privacy & Security

- ✅ **100% Local** - All data stays in your browser
- ✅ **No Uploads** - No data sent to external services
- ✅ **Offline Ready** - Works completely offline
- ✅ **Self-Contained** - Single HTML file with everything included

## Using the Dashboard

### Step 1: Generate Dashboard

```bash
judge-llm dashboard
```

This will:
1. Create `dashboard.html` in current directory
2. Open it in your default browser

### Step 2: Load Database

Once the dashboard opens:
1. Click "Load Database" button (or drag & drop)
2. Select your `.db` file
3. Explore your results!

### Step 3: Navigate Views

Use the left sidebar to switch between views:
- **Monitor**: Quick overview
- **Agents**: Click to see performance trends
- **Executions**: Click to expand details

## Database File

The dashboard works with SQLite databases created by the `DatabaseReporter`:

```yaml
# In your evaluation config
reporters:
  - type: database
    db_path: ./evaluation_results.db
```

After running evaluations, use the generated `.db` file with the dashboard.

## Advanced Usage

### Custom Output Location

```bash
# Generate in specific directory
judge-llm dashboard --output ~/reports/$(date +%Y%m%d)_dashboard.html
```

### Integration with CI/CD

```bash
# Generate dashboard without opening browser
judge-llm dashboard --no-browser --output ./artifacts/dashboard.html

# Upload to artifact storage
aws s3 cp ./artifacts/dashboard.html s3://my-bucket/reports/
```

### Multiple Databases

The dashboard can load any `.db` file at runtime:
1. Generate once: `judge-llm dashboard`
2. Use with different databases by loading them in the UI

## Troubleshooting

### Dashboard Not Opening

```bash
# Generate without auto-open, then open manually
judge-llm dashboard --no-browser
open dashboard.html  # macOS
xdg-open dashboard.html  # Linux
start dashboard.html  # Windows
```

### Template Not Found

Ensure `judge_llm` is properly installed:
```bash
pip install -e .
```

The template should be at:
```
<installation-path>/judge_llm/templates/monitor.html
```

### Browser Compatibility

Supported browsers:
- ✅ Chrome/Edge (recommended)
- ✅ Firefox
- ✅ Safari
- ⚠️ IE/Old browsers not supported

## Development

### Regenerating Dashboard

If you modify the template:

```bash
# Example script available at
python examples/06-database-reporter/generate_dashboard.py
```

### Template Location

The source template is at:
```
judge_llm/templates/monitor.html
```

Modifications should be made there, then redistributed via CLI.

## Help

```bash
# Show CLI help
judge-llm dashboard --help

# Show all commands
judge-llm --help
```

## Summary

**One command to visualize your evaluations:**
```bash
judge-llm dashboard
```

That's it! Simple, powerful, and completely local. 🎉
