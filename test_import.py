#!/usr/bin/env python
"""Test script to verify judge_llm imports work correctly."""

import sys
print("=" * 70)
print("IMPORT TEST")
print("=" * 70)
print(f"\nPython executable: {sys.executable}")
print(f"Python version: {sys.version}")

print("\nTest 1: Import judge_llm")
try:
    import judge_llm
    print("✓ SUCCESS: judge_llm imported")
    if hasattr(judge_llm, '__file__'):
        print(f"  Location: {judge_llm.__file__}")
except ImportError as e:
    print(f"✗ FAILED: {e}")
    sys.exit(1)

print("\nTest 2: Import evaluate function")
try:
    from judge_llm import evaluate
    print("✓ SUCCESS: evaluate function imported")
except ImportError as e:
    print(f"✗ FAILED: {e}")
    sys.exit(1)

print("\nTest 3: Import GeminiProvider")
try:
    from judge_llm.providers.gemini_provider import GeminiProvider
    print("✓ SUCCESS: GeminiProvider imported")
except ImportError as e:
    print(f"✗ FAILED: {e}")
    print("  Note: This requires 'google-genai' to be installed")
    print("  Run: pip install google-genai")

print("\nTest 4: Check provider registration")
try:
    from judge_llm.core.registry import get_provider_registry
    registry = get_provider_registry()
    providers = registry.list_providers()
    print(f"✓ SUCCESS: Registered providers: {providers}")
except Exception as e:
    print(f"✗ FAILED: {e}")
    sys.exit(1)

print("\n" + "=" * 70)
print("ALL TESTS PASSED ✓")
print("=" * 70)
print("\nYour judge_llm package is correctly installed and importable!")
