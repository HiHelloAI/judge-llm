# HTML Report Example

This example demonstrates how to generate comprehensive HTML reports with Judge LLM.

## Features

- **Interactive Dashboard**: Click on executions to view details
- **Summary Metrics**: Success rate, cost, time, token usage
- **Execution List**: All runs organized by eval set and case
- **Detailed Views**:
  - Conversation history
  - Evaluator results with pass/fail status
  - Metrics and scores
  - Raw JSON data
- **Dark Mode Support**: Toggle between light and dark themes
- **Responsive Design**: Works on desktop and mobile

## Files

- `config.yaml` - Configuration with HTML reporter enabled
- `sample.evalset.json` - Sample evaluation dataset
- `run.py` - Python script to generate reports
- `report.html` - Generated HTML report (after running)
- `report.json` - Generated JSON report (after running)

## Running the Example

```bash
python run.py
```

Or via CLI:

```bash
judge-llm run --config config.yaml
```

## Viewing the Report

After running, open `report.html` in your web browser:

```bash
# On macOS
open report.html

# On Linux
xdg-open report.html

# On Windows
start report.html
```

## Report Structure

### Left Sidebar
- **Dashboard Summary**: Total executions, success rate, cost, time
- **Execution List**: Clickable list of all runs
  - Shows status badge (✓/✗)
  - Displays key metrics (time, cost)
  - Grouped by eval case and run number

### Main Panel
When you click an execution, you'll see:

1. **Execution Header**
   - Execution ID
   - Eval case ID
   - Provider type
   - Run number
   - Time taken
   - Cost
   - Token usage
   - Overall status

2. **Evaluator Results**
   - Each evaluator displayed separately
   - Pass/fail status
   - Score vs threshold
   - Detailed results

3. **Conversation History**
   - User inputs
   - Agent responses
   - Tool uses (if any)
   - Intermediate responses

## Customization

### Change Output Path

In `config.yaml`:

```yaml
reporters:
  - type: html
    output_path: ./custom_path/my_report.html
```

### Multiple Reports

Generate reports in different formats:

```yaml
reporters:
  - type: console  # Terminal output
  - type: html     # Interactive dashboard
    output_path: ./report.html
  - type: json     # Machine-readable
    output_path: ./report.json
```

## Configuration Options

The example uses:
- **num_runs: 2**: Each eval case runs twice
- **parallel_execution: true**: Runs execute in parallel
- **max_workers: 4**: Up to 4 parallel workers

This generates multiple execution results, making the HTML report more interesting and useful for comparing runs.

## Benefits of HTML Reports

1. **Easy Sharing**: Send the HTML file to stakeholders
2. **No Dependencies**: Self-contained, opens in any browser
3. **Interactive**: Click to explore, no command-line needed
4. **Visual**: Color-coded status, organized layout
5. **Complete**: All data embedded in one file
6. **Professional**: Clean, modern design

## Tips

- Run with multiple eval cases for a richer dashboard
- Use `num_runs > 1` to see variation across runs
- Enable parallel execution for faster generation
- The HTML file is completely self-contained - no external dependencies needed
