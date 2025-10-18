# Professional Dashboard - User Guide

## 🎨 Clean, Sophisticated Monitoring Interface

A professional-grade dashboard with a clean, minimal design inspired by modern monitoring tools. Features a left navigation panel and comprehensive data views.

## ✨ Key Features

### Clean Design
- ✅ **Minimal colors** - Clean grays and whites
- ✅ **Professional typography** - System fonts, clear hierarchy
- ✅ **Subtle borders** - Clean visual separation
- ✅ **No distracting gradients** - Focus on data

### Navigation
- **Left Panel** - Persistent navigation
- **7 Views** - Monitor, Executions, Providers, Test Cases, Evaluators, Datasets, Reports
- **Time Filters** - 1d, 3d, 7d, 30d, All
- **Small Upload Button** - Unobtrusive top-right corner

### Data Views

#### 1. Monitor (Overview)
- 4 key metrics cards
- 4 trend charts (Success Rate, Cost, Executions, Latency)
- Clean line and bar charts
- Time-filtered data

#### 2. Executions
- Complete execution history table
- Expandable rows for details
- Conversation comparison (expected vs actual)
- Search functionality
- Clean status badges

#### 3. Providers
- Provider performance comparison
- Success rates, costs, latency
- Model-level breakdown
- Sortable table

#### 4. Test Cases
- Test case performance tracking
- Pass rates and costs
- Historical data
- Prompt previews

#### 5. Evaluators
- Evaluator performance metrics
- Score distributions
- Pass rates and thresholds
- Reliability tracking

#### 6. Datasets
- Dataset overview
- Test case counts
- Execution statistics
- Timeline tracking

#### 7. Reports
- Evaluation report history
- Success rates
- Cost and time metrics
- Status tracking

## 🚀 Quick Start

### Generate Dashboard
```bash
cd examples/06-database-reporter
python generate_dashboard.py monitor.html v2
```

### Open Dashboard
```bash
# macOS
open monitor.html

# Linux
xdg-open monitor.html

# Windows
start monitor.html
```

### Load Database
1. Click **"Load Database"** button (top-right)
2. Select your `.db` file
3. Dashboard loads automatically

## 📊 Design Philosophy

### Inspired by Modern Tools
- Clean, professional appearance
- Data-first approach
- Minimal visual noise
- Clear information hierarchy

### Color Palette
- **Background**: Light gray (#fafafa)
- **Cards**: White
- **Borders**: Light gray (#e0e0e0)
- **Text**: Dark gray (#1a1a1a)
- **Accents**: Blue (#4a90e2) for interactions
- **Success**: Green (#1e7e34)
- **Error**: Red (#c41e3a)

### Typography
- **System fonts** for native feel
- **13px** for body text
- **11px** for labels
- **Monospace** for code/IDs

### Layout
- **220px** left sidebar
- **Responsive** main content
- **Consistent** padding and spacing
- **Clean** table design

## 💡 Usage Patterns

### Daily Monitoring
1. Open dashboard
2. Load today's database
3. Check Monitor view for overview
4. Review Executions for any failures
5. Investigate failures with conversation comparison

### Weekly Review
1. Set time filter to "7d"
2. Check trend charts in Monitor view
3. Review Provider performance
4. Identify costly test cases
5. Optimize as needed

### Failure Investigation
1. Go to Executions view
2. Find failed execution (red badge)
3. Click to expand details
4. Review conversation comparison
5. Understand what went wrong

## 🎯 Navigation Guide

### Left Panel Items

- **📊 Monitor** - Overview with metrics and charts
- **🚀 Executions** - Complete execution history
- **🤖 Providers** - Provider comparison table
- **🧪 Test Cases** - Test case performance
- **🎯 Evaluators** - Evaluator statistics
- **📁 Datasets** - Dataset overview
- **📄 Reports** - Report history

### Time Filters (Top Bar)

- **1d** - Last 24 hours
- **3d** - Last 3 days (default)
- **7d** - Last week
- **30d** - Last month
- **All** - All time

### Interactions

- **Click nav items** - Switch views
- **Click time filters** - Change date range
- **Click execution rows** - Expand/collapse details
- **Type in search** - Filter executions table
- **Scroll** - View more data

## 🔧 Customization

### Modify Colors
Edit the CSS in the `<style>` section:

```css
/* Change accent color */
border-color: #4a90e2;  /* Blue accent */

/* Change background */
background: #fafafa;  /* Light gray */
```

### Adjust Layout
```css
/* Sidebar width */
.sidebar {
    width: 220px;  /* Adjust as needed */
}

/* Metric card size */
.metrics-grid {
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
}
```

### Chart Colors
```javascript
// In createLineChart and createBarChart functions
borderColor: '#4a90e2',  // Line color
backgroundColor: '#4a90e2cc',  // Fill/bar color
```

## 🎨 Design Choices

### Why This Design?

**Clean & Professional**
- Reduces cognitive load
- Focuses attention on data
- Matches modern tool aesthetics

**Left Navigation**
- Always visible
- Easy context switching
- Clear current location

**Minimal Colors**
- Less distraction
- Data stands out
- Professional appearance

**Small Upload Button**
- Unobtrusive
- Always accessible
- Doesn't dominate interface

**Expandable Rows**
- Compact default view
- Details on demand
- Efficient use of space

**System Fonts**
- Native platform feel
- Better readability
- Faster rendering

## 📊 Comparison with V1

### V1 (Colorful Dashboard)
- Gradient backgrounds
- Bright colors
- Tab-based navigation
- Larger UI elements
- More playful design

### V2 (Professional Monitor)
- Clean white/gray palette
- Subtle colors
- Sidebar navigation
- Compact UI elements
- Professional design

**Both versions are available! Choose based on preference.**

## 🚨 Tips & Tricks

### Performance
- Large databases (>100MB)? Filter by time range
- Use search to find specific executions
- Collapse expanded rows when done

### Workflow
1. Keep dashboard open in browser tab
2. Generate new reports throughout day
3. Reload database file to see updates
4. Use time filters to focus on recent data

### Keyboard Navigation
- Tab through interactive elements
- Enter to expand/collapse rows
- Cmd/Ctrl+F to search page

## 📚 Resources

- **Template**: `judge_llm/templates/dashboard_v2.html`
- **Generator**: `examples/06-database-reporter/generate_dashboard.py`
- **V1 Dashboard**: `judge_llm/templates/dashboard.html` (colorful version)

## 🎓 Advanced Usage

### Multiple Databases
Open dashboard in multiple browser tabs/windows to compare databases side-by-side.

### Export Data
Use browser's "Save as PDF" to export dashboard views for reports.

### Custom Queries
Open browser console (F12) and run custom SQL:

```javascript
// Custom query example
const result = db.exec(`
    SELECT COUNT(*) FROM execution_runs
    WHERE cost > 0.01
`);
console.log(result);
```

## 🤝 Which Dashboard to Use?

### Use V2 (Professional) If:
- ✅ You prefer clean, minimal design
- ✅ You want a professional monitoring tool feel
- ✅ You like left-panel navigation
- ✅ You work with data frequently
- ✅ You share dashboards in professional settings

### Use V1 (Colorful) If:
- ✅ You prefer vibrant, colorful interfaces
- ✅ You like tab-based navigation
- ✅ You want larger, more playful UI
- ✅ You're presenting to non-technical audiences

**Both are equally functional - it's purely aesthetic preference!**

---

## 🎉 Summary

The V2 Professional Dashboard provides:
- ✅ **Clean design** - Minimal colors, maximum clarity
- ✅ **Left navigation** - Easy view switching
- ✅ **Complete history** - All executions tracked
- ✅ **Time filtering** - Focus on relevant data
- ✅ **Expandable details** - Information on demand
- ✅ **100% local** - Privacy-first design

**A sophisticated monitoring tool for serious LLM evaluation! 📊**
