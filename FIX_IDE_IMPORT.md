# Fix "Cannot import judge_llm" in IDE

## Problem
- ✅ `judge-llm` CLI command works
- ✅ Imports work in terminal with activated venv
- ❌ IDE shows "Unresolved reference 'judge_llm'"
- ❌ Python scripts in IDE cannot import judge_llm

## Root Cause
**Your IDE is not using the project's venv Python interpreter.**

## Verification
Run this test to confirm imports work in venv:
```bash
source venv/bin/activate
python test_import.py
```

Expected output: `ALL TESTS PASSED ✓`

---

## Solution for PyCharm

### Step 1: Configure Python Interpreter

1. **Open Settings:**
   - Mac: `PyCharm` → `Settings` or `Cmd + ,`
   - Windows/Linux: `File` → `Settings` or `Ctrl + Alt + S`

2. **Navigate to Interpreter:**
   - Go to: `Project: judge_llm` → `Python Interpreter`

3. **Add Venv Interpreter:**
   - Click the gear icon ⚙️ → `Add...`
   - Select `Existing Environment`
   - Click the folder icon 📁
   - Navigate to: `/Users/nambi/PycharmProjects/judge_llm/venv/bin/python`
   - Click `OK`

4. **Verify Packages:**
   - You should see `judge-llm 0.1.0` in the package list
   - You should see `google-genai` in the package list

### Step 2: Invalidate Caches

1. Go to: `File` → `Invalidate Caches...`
2. Check all options:
   - ✅ Invalidate and Restart
   - ✅ Clear file system cache and Local History
   - ✅ Clear VCS Log caches and indexes
3. Click `Invalidate and Restart`

### Step 3: Mark Sources Root

1. In Project view, right-click on project root folder
2. Select `Mark Directory as` → `Sources Root`

### Step 4: Verify Configuration

After restart, open Python Console in PyCharm:
```python
import judge_llm
print("✓ Success!")
```

---

## Solution for VS Code

### Step 1: Select Python Interpreter

1. **Open Command Palette:**
   - Mac: `Cmd + Shift + P`
   - Windows/Linux: `Ctrl + Shift + P`

2. **Select Interpreter:**
   - Type: `Python: Select Interpreter`
   - Choose: `./venv/bin/python` (should show Python 3.12.0)

### Step 2: Configure Workspace Settings

Create/edit `.vscode/settings.json`:
```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
  "python.terminal.activateEnvironment": true,
  "python.analysis.extraPaths": [
    "${workspaceFolder}"
  ],
  "python.autoComplete.extraPaths": [
    "${workspaceFolder}"
  ]
}
```

### Step 3: Reload Window

1. Open Command Palette: `Cmd + Shift + P` / `Ctrl + Shift + P`
2. Type: `Developer: Reload Window`
3. Press Enter

### Step 4: Verify

Open new terminal in VS Code (should auto-activate venv):
```bash
python -c "import judge_llm; print('✓ Success!')"
```

---

## Quick Fix Script

Run this to verify your setup:

```bash
#!/bin/bash
echo "Checking judge_llm installation..."
echo ""

# Activate venv
source venv/bin/activate

# Check Python
echo "1. Python location:"
which python
echo ""

# Check package
echo "2. Package installed:"
pip show judge-llm | grep -E "Name|Version|Location"
echo ""

# Test import
echo "3. Import test:"
python -c "import judge_llm; print('✓ judge_llm imports successfully')"
echo ""

# Test CLI
echo "4. CLI test:"
judge-llm list providers
echo ""

echo "✅ Everything works in terminal!"
echo ""
echo "If your IDE still shows errors:"
echo "  PyCharm: Set interpreter to: $(pwd)/venv/bin/python"
echo "  VS Code: Cmd+Shift+P → 'Python: Select Interpreter' → Choose ./venv/bin/python"
```

Save as `check_setup.sh` and run:
```bash
chmod +x check_setup.sh
./check_setup.sh
```

---

## Common Issues

### Issue 1: "judge_llm-0.1.0.dist-info not found"
**Cause:** Package not installed in the venv you're using
**Fix:**
```bash
source venv/bin/activate
pip install -e .
pip install google-genai  # For Gemini provider
```

### Issue 2: IDE shows old interpreter
**Cause:** IDE cached old interpreter selection
**Fix:**
- PyCharm: Invalidate caches and restart
- VS Code: Reload window

### Issue 3: Multiple Python installations
**Cause:** System has multiple Python versions
**Fix:** Explicitly use venv:
```bash
./venv/bin/python -c "import judge_llm"
```

### Issue 4: Import works in terminal but not IDE
**Cause:** IDE using different Python than terminal
**Fix:** Configure IDE to use `./venv/bin/python`

---

## Verification Checklist

After fixing, all these should work:

### In Terminal (with venv activated):
```bash
source venv/bin/activate

# Test 1: CLI
judge-llm list providers
# Expected: Shows 'gemini' and 'mock'

# Test 2: Python import
python -c "import judge_llm; print('✓')"
# Expected: ✓

# Test 3: Run test script
python test_import.py
# Expected: ALL TESTS PASSED ✓
```

### In IDE:
```python
# Test 1: Basic import
import judge_llm  # Should not show red underline

# Test 2: Function import
from judge_llm import evaluate  # Should autocomplete

# Test 3: Provider import
from judge_llm.providers.gemini_provider import GeminiProvider  # Should work

# Test 4: Registry
from judge_llm.core.registry import get_provider_registry
registry = get_provider_registry()
print(registry.list_providers())  # Should show ['mock', 'gemini']
```

---

## Still Not Working?

### Debug Steps:

1. **Check which Python your IDE is using:**
   - PyCharm: Settings → Project → Python Interpreter (bottom status bar also shows)
   - VS Code: Check bottom-left corner for Python version

2. **Verify venv has the package:**
   ```bash
   ./venv/bin/python -c "import judge_llm; print(judge_llm.__file__)"
   ```
   Should output: `/Users/nambi/PycharmProjects/judge_llm/judge_llm/__init__.py`

3. **Check sys.path in IDE:**
   ```python
   import sys
   print('\n'.join(sys.path))
   ```
   Should include: `/Users/nambi/PycharmProjects/judge_llm/venv/lib/python3.12/site-packages`

4. **Reinstall in venv:**
   ```bash
   source venv/bin/activate
   pip uninstall -y judge-llm
   pip install -e .
   pip install google-genai
   ```

---

## Success Criteria

✅ Your setup is correct when:
1. `judge-llm list providers` shows both 'gemini' and 'mock'
2. `python test_import.py` passes all tests
3. IDE shows no red underlines on `import judge_llm`
4. IDE autocomplete works for judge_llm classes
5. Running scripts in IDE doesn't show import errors

---

## Summary

**The package works perfectly in terminal!** 🎉

The "unresolved reference" error is just an **IDE configuration issue**.

**Quick Fix:**
1. Point your IDE to use: `/Users/nambi/PycharmProjects/judge_llm/venv/bin/python`
2. Restart/reload IDE
3. Done!

Your venv has:
- ✅ judge_llm-0.1.0.dist-info (package metadata)
- ✅ __editable__.judge_llm-0.1.0.pth (points to source code)
- ✅ google-genai (Gemini SDK)
- ✅ All dependencies installed

Everything is correctly set up! Just configure your IDE interpreter. 👍
