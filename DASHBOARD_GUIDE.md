# Interactive Dashboard Guide

## 🎨 Standalone HTML Dashboard for Judge LLM Results

A beautiful, interactive dashboard to visualize your Judge LLM evaluation results. **100% local, no server required, works offline!**

## ✨ Features

### 📊 **7 Interactive Views**

1. **Overview** - Recent evaluation reports summary
2. **Executions** - Detailed test execution history with expandable details
3. **Providers** - Provider/model performance comparison
4. **Test Cases** - Test case success rates and costs
5. **Evaluators** - Evaluator score distributions and pass rates
6. **Conversations** - Side-by-side expected vs actual response comparison
7. **Trends** - Performance and cost trends over time with charts

### 🎯 **Key Capabilities**

- **Drag & Drop Database Loading** - Just drop your .db file
- **Real-time Statistics** - Live dashboard with key metrics
- **Interactive Charts** - Success rate and cost trends visualization
- **Conversation Analysis** - Compare expected vs actual responses
- **Provider Comparison** - Cost, speed, and quality metrics
- **Zero Configuration** - Works out of the box
- **100% Private** - All data stays in your browser

## 🚀 Quick Start

### Method 1: Generate Dashboard

```bash
cd examples/06-database-reporter
python generate_dashboard.py
```

This creates `dashboard.html` in the current directory.

### Method 2: Use Template Directly

The dashboard template is located at:
```
judge_llm/templates/dashboard.html
```

Just copy it anywhere you want!

## 📖 How to Use

### Step 1: Open the Dashboard

Double-click `dashboard.html` to open it in your web browser.

Or open it with a specific browser:
```bash
# macOS
open dashboard.html

# Linux
xdg-open dashboard.html

# Windows
start dashboard.html
```

### Step 2: Load Your Database

**Option A: Drag & Drop**
1. Drag your `.db` file from Finder/Explorer
2. Drop it onto the upload area
3. Dashboard loads automatically!

**Option B: Click to Browse**
1. Click the upload area
2. Select your `.db` file
3. Dashboard loads automatically!

### Step 3: Explore Your Data

Navigate through the 7 tabs:

- **📊 Overview** - Start here for a quick summary
- **🚀 Executions** - Click on any execution to see details
- **🤖 Providers** - Compare different LLM providers
- **🧪 Test Cases** - See which tests are passing/failing
- **🎯 Evaluators** - Analyze evaluator performance
- **💬 Conversations** - Compare expected vs actual responses
- **📈 Trends** - View performance over time

## 🎨 Dashboard Sections

### 1. Statistics Overview

Four key metrics displayed at the top:

- **Total Executions** - Number of test runs
- **Success Rate** - Percentage of passed tests
- **Total Cost** - Cumulative spending
- **Providers** - Number of LLM providers tested

Color-coded for quick insights:
- 🟢 Green: Good (success rate ≥ 80%)
- 🟡 Yellow: Warning (50-79%)
- 🔴 Red: Critical (< 50%)

### 2. Overview Tab

Shows recent evaluation reports with:
- Report ID and timestamp
- Success rate
- Total cost and time
- Overall pass/fail status

### 3. Executions Tab

Detailed execution history with expandable cards:

**Summary View:**
- Test case ID
- Pass/fail badge
- Provider and model
- Cost and time

**Expanded View (click to expand):**
- Full execution ID
- Exact timestamp
- Original prompt
- Token usage breakdown

### 4. Providers Tab

Comprehensive provider comparison table:

| Metric | Description |
|--------|-------------|
| Provider | LLM provider name |
| Model | Specific model version |
| Runs | Total test executions |
| Success Rate | Pass rate percentage |
| Avg Cost | Average cost per execution |
| Total Cost | Cumulative cost |
| Avg Time | Average execution time |
| Avg Tokens | Input/output token counts |

### 5. Test Cases Tab

Performance metrics per test case:

- Test case ID
- User prompt (truncated)
- Number of runs
- Pass rate
- Average cost and time

Identifies:
- ✅ **Passing tests** (100% pass rate)
- ⚠️ **Flaky tests** (50-99% pass rate)
- ❌ **Failing tests** (< 50% pass rate)

### 6. Evaluators Tab

Evaluator performance analysis:

- Evaluator name and type
- Total evaluations
- Pass rate
- Score statistics (avg, min, max)
- Average threshold

### 7. Conversations Tab

**Side-by-side comparison of responses!**

For each execution, see:

📝 **Expected Response** (from test case)
- The reference answer
- What you wanted the LLM to say

🤖 **Actual Response** (from provider)
- What the LLM actually said
- Compare against expected

Perfect for investigating failures!

### 8. Trends Tab

**Visual charts showing:**

**Success Rate Trend**
- Line chart of success rate over time
- Identify performance regressions
- Track improvements

**Daily Cost Chart**
- Bar chart of daily spending
- Monitor cost trends
- Budget forecasting

## 🔒 Privacy & Security

### 100% Local Processing

- ✅ Database loaded entirely in your browser
- ✅ No data uploaded to any server
- ✅ No external API calls for data
- ✅ Works completely offline (after initial load)
- ✅ Your data never leaves your computer

### External Dependencies (CDN)

The dashboard uses two libraries loaded from CDN:

1. **SQL.js** - JavaScript SQLite engine
   - Enables reading .db files in the browser
   - From: cdnjs.cloudflare.com

2. **Chart.js** - Charting library
   - Creates the trend charts
   - From: cdn.jsdelivr.net

**These libraries only process data locally in your browser.**

### Offline Usage

To use completely offline:

1. Download SQL.js and Chart.js locally
2. Update the `<script>` tags in dashboard.html to point to local files
3. Open dashboard.html - works without internet!

## 💡 Use Cases

### 1. Quick Results Review

After running evaluations:
1. Open dashboard
2. Load latest .db file
3. Check overview stats
4. Done in 30 seconds!

### 2. Failure Investigation

When tests fail:
1. Go to **Executions** tab
2. Find failed execution (red badge)
3. Expand to see details
4. Go to **Conversations** tab
5. Compare expected vs actual responses
6. Understand what went wrong!

### 3. Provider Comparison

Testing multiple providers:
1. Go to **Providers** tab
2. Compare:
   - Success rates
   - Costs
   - Speed
   - Token usage
3. Make data-driven decisions!

### 4. Cost Optimization

Monitor spending:
1. Check **Trends** tab for daily costs
2. Go to **Test Cases** tab
3. Sort by average cost
4. Identify expensive tests
5. Optimize or reduce frequency

### 5. Quality Monitoring

Track quality over time:
1. **Trends** tab shows success rate trend
2. Spot regressions immediately
3. Correlate with deployments
4. Maintain quality standards

### 6. Evaluator Tuning

Optimize evaluators:
1. **Evaluators** tab shows score distributions
2. Check if thresholds are appropriate
3. Identify unreliable evaluators
4. Adjust thresholds or logic

## 🎯 Tips & Tricks

### Keyboard Shortcuts

- Tab through different views quickly
- Click execution cards to expand/collapse

### Quick Filters

Currently viewing all data. Future versions will add:
- Date range filters
- Provider filters
- Success/failure filters
- Search by test case ID

### Multiple Databases

To compare databases:
1. Open dashboard in multiple browser tabs/windows
2. Load different .db file in each
3. Compare side-by-side

### Export Screenshots

To share results:
1. Navigate to desired view
2. Take screenshot (Cmd+Shift+4 on Mac)
3. Share with team!

### Browser Compatibility

Works in all modern browsers:
- ✅ Chrome/Edge (recommended)
- ✅ Firefox
- ✅ Safari
- ✅ Opera

**Note:** Requires JavaScript enabled

## 🛠️ Customization

### Modify Dashboard

The dashboard is a single HTML file. You can customize:

**Colors:**
Edit the CSS gradient in `<style>` section:
```css
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
```

**Stats Cards:**
Modify the `loadStats()` function to add new metrics

**Tables:**
Edit table rendering functions to add/remove columns

**Charts:**
Customize Chart.js options in `loadTrends()`

### Add New Views

1. Add new tab button in HTML
2. Add new tab content div
3. Create load function for your view
4. Call it in `loadDashboard()`

### Custom Queries

Edit SQL queries in load functions to show different data:

```javascript
const myData = db.exec(`
    SELECT your_custom_query
    FROM your_table
    WHERE your_conditions
`)[0];
```

## 📊 Sample Workflow

### Daily Monitoring

```bash
# Morning: Run evaluations
judge-llm evaluate --config config.yaml

# Open dashboard
open dashboard.html

# Load today's results
# Drag results.db into browser

# Check overview:
# - Success rate still good? ✅
# - Costs within budget? ✅
# - Any new failures? ⚠️

# Investigate failures if any:
# - Go to Executions tab
# - Find failures
# - Check Conversations tab
# - Fix issues
```

### Weekly Review

```bash
# Open dashboard
# Load accumulated results.db

# Check Trends tab:
# - Success rate trending up? 📈
# - Costs stable? 💰
# - Performance improving? ⚡

# Review Providers tab:
# - Which provider performing best?
# - Any cost optimization opportunities?

# Review Test Cases:
# - Any flaky tests? Fix them!
# - Any consistently failing? Update expected responses?
```

### Monthly Analysis

```bash
# Export monthly stats:
# - Screenshot Trends charts
# - Screenshot Provider comparison
# - Screenshot cost summary

# Share with team:
# - Attach to monthly report
# - Present in team meeting
# - Document learnings
```

## 🚨 Troubleshooting

### Dashboard Won't Load

**Problem:** Blank page or errors

**Solutions:**
1. Check browser console for errors (F12)
2. Ensure JavaScript is enabled
3. Try different browser
4. Check file permissions

### Database Won't Load

**Problem:** "Error loading database" message

**Solutions:**
1. Ensure file is a valid SQLite .db file
2. Check file isn't corrupted
3. Try re-generating database
4. Verify file permissions

### No Data Showing

**Problem:** Dashboard loads but shows empty states

**Solutions:**
1. Verify database has data (`sqlite3 file.db "SELECT COUNT(*) FROM reports;"`)
2. Check if tables exist (`sqlite3 file.db ".tables"`)
3. Ensure database is from current version of Judge LLM
4. Try with sample database first

### Charts Not Rendering

**Problem:** Trend charts don't appear

**Solutions:**
1. Check internet connection (needs Chart.js from CDN)
2. Check browser console for errors
3. Verify sufficient data exists (need multiple days for trends)
4. Try refreshing page

### Slow Performance

**Problem:** Dashboard is slow with large databases

**Solutions:**
1. Database size > 100MB? Consider archiving old data
2. Use Chrome for best performance
3. Close other browser tabs
4. Increase browser memory limit

## 🎓 Advanced Usage

### Custom SQL Queries

Open browser console (F12) and run custom queries:

```javascript
// Example: Find most expensive execution
const result = db.exec(`
    SELECT eval_case_id, cost
    FROM execution_runs
    ORDER BY cost DESC
    LIMIT 1
`);
console.log(result);
```

### Extract Data

Export data from browser console:

```javascript
// Get all provider data
const providers = db.exec(`
    SELECT * FROM execution_runs
    WHERE provider_type = 'gemini'
`)[0];

// Convert to CSV
console.table(providers.values);

// Copy-paste from console
```

### Automated Screenshots

Use headless browser to automate dashboard screenshots:

```python
from selenium import webdriver

driver = webdriver.Chrome()
driver.get('file:///path/to/dashboard.html')
# ... upload db file programmatically ...
driver.save_screenshot('dashboard.png')
```

## 📚 Resources

- **Dashboard Template:** `judge_llm/templates/dashboard.html`
- **Generator Script:** `examples/06-database-reporter/generate_dashboard.py`
- **Database Schema:** See `DATABASE_SCHEMA.md`
- **Example Database:** Run `examples/06-database-reporter/run_evaluation.py`

## 🤝 Contributing

Want to improve the dashboard?

1. Edit `judge_llm/templates/dashboard.html`
2. Test your changes
3. Submit a pull request!

Ideas for improvements:
- Additional chart types
- Filter/search functionality
- Export to CSV/PDF
- Dark mode
- More advanced analytics
- Custom date ranges

## 📄 License

Same as Judge LLM (MIT License)

---

**Enjoy your beautiful, interactive, privacy-focused evaluation dashboard! 🎉**
