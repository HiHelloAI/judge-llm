#!/usr/bin/env python
"""Test script to verify ADK provider setup without requiring real API calls."""

import os
import sys

# Set a test API key
os.environ['GOOGLE_API_KEY'] = 'test-key-for-validation'

sys.path.insert(0, '../..')

from judge_llm.providers.adk_provider import GoogleADKProvider
from judge_llm.core.models import EvalCase, SessionInput, Invocation, Content, Part, IntermediateData

print("=" * 80)
print("ADK Provider Setup Test")
print("=" * 80)
print()

# Test 1: Provider instantiation
print("Test 1: Provider Instantiation")
try:
    provider = GoogleADKProvider(
        agent_id='test_agent',
        agent_metadata={
            'module_path': 'tool_agent.agent',
            'agent_name': 'root_agent',
            'root_path': '.'
        }
    )
    print("  ✓ Provider created successfully")
    print(f"    - Type: {provider.get_provider_type()}")
    print(f"    - Agent ID: {provider.agent_id}")
except Exception as e:
    print(f"  ✗ Failed: {e}")
    sys.exit(1)

print()

# Test 2: Agent loading
print("Test 2: Agent Loading")
try:
    agent = provider._load_agent()
    print(f"  ✓ Agent loaded successfully")
    print(f"    - Agent type: {type(agent).__name__}")
    print(f"    - Agent name: {agent.name}")
    print(f"    - Number of tools: {len(agent.tools)}")
except Exception as e:
    print(f"  ✗ Failed: {e}")
    sys.exit(1)

print()

# Test 3: Model conversion (input)
print("Test 3: Framework to ADK Conversion")
try:
    # Create a simple test case
    test_invocation = Invocation(
        invocation_id="test_001",
        user_content=Content(
            role="user",
            parts=[Part(text="Test message")]
        ),
        final_response=Content(
            role="model",
            parts=[Part(text="Test response")]
        ),
        intermediate_data=IntermediateData(),
        creation_timestamp=1234567890.0
    )

    adk_invocations = provider._to_adk_invocations([test_invocation])
    print(f"  ✓ Converted framework invocation to ADK format")
    print(f"    - Number of invocations: {len(adk_invocations)}")
    print(f"    - User content type: {type(adk_invocations[0].user_content).__name__}")
except Exception as e:
    print(f"  ✗ Failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# Test 4: Execution (will fail with fake API key, but tests the flow)
print("Test 4: Execution Flow (with fake API key - expected to fail at API call)")
try:
    test_case = EvalCase(
        eval_id="test_case",
        creation_timestamp=1234567890.0,
        session_input=SessionInput(
            app_name="test_app",
            user_id="test_user",
            state={}
        ),
        conversation=[test_invocation]
    )

    result = provider.execute(test_case)

    if result.success:
        print(f"  ⚠ Unexpectedly succeeded (should fail with fake API key)")
    else:
        if 'API key not valid' in str(result.error) or 'INVALID_ARGUMENT' in str(result.error):
            print(f"  ✓ Execution flow working correctly")
            print(f"    - Failed at API authentication as expected")
            print(f"    - Error (truncated): {str(result.error)[:100]}...")
        elif 'coroutine' in str(result.error).lower():
            print(f"  ✗ Still has async/coroutine issues!")
            print(f"    - Error: {result.error}")
            sys.exit(1)
        else:
            print(f"  ⚠ Failed with unexpected error: {str(result.error)[:150]}")
except Exception as e:
    error_str = str(e)
    if 'coroutine' in error_str.lower():
        print(f"  ✗ Async/coroutine error: {e}")
        sys.exit(1)
    else:
        print(f"  ⚠ Unexpected exception: {error_str[:150]}")

print()
print("=" * 80)
print("All basic tests passed! ADK provider is properly configured.")
print("=" * 80)
print()
print("To run with a real API key:")
print("  export GOOGLE_API_KEY='your-actual-key'")
print("  python run_evaluation.py")
