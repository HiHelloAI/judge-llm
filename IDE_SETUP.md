# IDE Setup Guide

## Resolving "Unresolved reference 'judge_llm'" Warning

If your IDE (PyCharm, VS Code, etc.) shows "Unresolved reference 'judge_llm'" warnings, follow these steps:

### For PyCharm

1. **Mark as Sources Root:**
   - Right-click on the project root directory
   - Select "Mark Directory as" → "Sources Root"

2. **Invalidate Caches:**
   - Go to `File` → `Invalidate Caches...`
   - Check "Invalidate and Restart"
   - Click "Invalidate and Restart"

3. **Configure Python Interpreter:**
   - Go to `File` → `Settings` → `Project: judge_llm` → `Python Interpreter`
   - Ensure your virtual environment is selected
   - Click the refresh button to reload packages
   - Verify `judge-llm` appears in the package list

4. **Reinstall in Editable Mode:**
   ```bash
   pip uninstall judge-llm
   pip install -e .
   ```

5. **Check Project Structure:**
   - Go to `File` → `Project Structure`
   - Ensure the project root is marked as "Sources"
   - Ensure `judge_llm` folder is included

### For VS Code

1. **Select Python Interpreter:**
   - Press `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Windows/Linux)
   - Type "Python: Select Interpreter"
   - Choose your virtual environment

2. **Reload Window:**
   - Press `Cmd+Shift+P` / `Ctrl+Shift+P`
   - Type "Developer: Reload Window"

3. **Install in Editable Mode:**
   ```bash
   pip install -e .
   ```

4. **Configure Python Path:**
   - Create/edit `.vscode/settings.json`:
   ```json
   {
     "python.analysis.extraPaths": [
       "${workspaceFolder}"
     ],
     "python.autoComplete.extraPaths": [
       "${workspaceFolder}"
     ]
   }
   ```

## Verification

After setup, verify the installation:

```bash
# Check package is installed
pip list | grep judge-llm

# Test imports
python -c "import judge_llm; print('✓ Success')"

# Test CLI
judge-llm list providers
```

Expected output:
```
Available Providers:
  - gemini
  - mock
```

## Package Structure

The package is installed in editable mode, so the structure is:

```
judge_llm/              # Source code (editable)
├── __init__.py         # Exports evaluate, register_*
├── core/               # Core functionality
├── providers/          # Provider implementations
│   ├── gemini_provider.py  # ← Your Gemini provider
│   └── ...
├── evaluators/         # Evaluator implementations
└── ...
```

## Common Issues

### Issue 1: "No module named 'judge_llm'"
**Solution:** Install in editable mode:
```bash
cd /path/to/judge_llm
pip install -e .
```

### Issue 2: "No module named 'google.genai'"
**Solution:** Install Gemini dependencies:
```bash
pip install google-genai
# Or with package extras:
pip install -e ".[gemini]"
```

### Issue 3: IDE still shows warnings after installation
**Solution:**
1. Restart IDE completely
2. Rebuild project indexes
3. Check Python interpreter is correct

### Issue 4: CLI command not found
**Solution:** Reinstall and check PATH:
```bash
pip install -e .
which judge-llm
```

## Environment Setup

For best results, use a virtual environment:

```bash
# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate  # Mac/Linux
# or
venv\Scripts\activate  # Windows

# Install package
pip install -e .

# Install with Gemini support
pip install -e ".[gemini]"
```

## IDE Configuration Files

### PyCharm
The `.idea/` directory contains PyCharm settings. If issues persist:
1. Close PyCharm
2. Delete `.idea/` directory
3. Reopen project (PyCharm will recreate settings)

### VS Code
Create `.vscode/settings.json`:
```json
{
  "python.pythonPath": "${workspaceFolder}/venv/bin/python",
  "python.analysis.extraPaths": ["${workspaceFolder}"],
  "python.autoComplete.extraPaths": ["${workspaceFolder}"],
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": false,
  "python.linting.flake8Enabled": true
}
```

## Testing Installation

Run the verification script:

```bash
python -c "
import sys
print('Python:', sys.version)
print('Path:', sys.executable)
print()

import judge_llm
print('✓ judge_llm imported')

from judge_llm import evaluate
print('✓ evaluate function available')

from judge_llm.providers.gemini_provider import GeminiProvider
print('✓ GeminiProvider available')

from judge_llm.core.registry import get_provider_registry
registry = get_provider_registry()
print('✓ Providers:', registry.list_providers())
"
```

Expected output:
```
Python: 3.x.x
Path: /path/to/venv/bin/python

✓ judge_llm imported
✓ evaluate function available
✓ GeminiProvider available
✓ Providers: ['mock', 'gemini']
```

## Quick Fix Script

Run this script to fix most common issues:

```bash
#!/bin/bash
echo "Fixing judge_llm IDE setup..."

# Reinstall package
pip uninstall -y judge-llm
pip install -e .

# Install Gemini support
pip install google-genai

# Verify installation
python -c "import judge_llm; print('✓ Installation successful')"

# List providers
python -m judge_llm.cli list providers

echo "Done! Restart your IDE now."
```

Save as `fix_ide.sh` and run:
```bash
chmod +x fix_ide.sh
./fix_ide.sh
```

## Support

If issues persist:
1. Check Python version: `python --version` (requires Python 3.9+)
2. Check pip version: `pip --version`
3. Verify virtual environment is activated
4. Check system PATH includes Python scripts directory
5. Try creating a fresh virtual environment

## Success Criteria

Your setup is correct when:
- ✅ `import judge_llm` works without errors
- ✅ `judge-llm list providers` shows gemini and mock
- ✅ IDE autocomplete works for judge_llm imports
- ✅ No red underlines in Python files
- ✅ Go-to-definition works for judge_llm classes
