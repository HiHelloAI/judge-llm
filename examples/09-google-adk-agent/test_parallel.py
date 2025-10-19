#!/usr/bin/env python
"""Test parallel execution to verify time is reduced."""

import os
import sys

os.environ['GOOGLE_API_KEY'] = 'test-key'

from judge_llm import evaluate

print("=" * 80)
print("Testing Parallel Execution")
print("=" * 80)
print()

# Test 1: Sequential execution
print("Test 1: Sequential Execution (baseline)")
print("-" * 80)
result_seq = evaluate(config='config.yaml')
seq_time = result_seq.total_time
seq_runs = len(result_seq.execution_runs)
print(f"  Total runs: {seq_runs}")
print(f"  Total time: {seq_time:.2f}s")
print()

# Test 2: Parallel execution
print("Test 2: Parallel Execution")
print("-" * 80)

# Create temp config with parallel enabled
import yaml
with open('config.yaml') as f:
    config = yaml.safe_load(f)

config['agent']['parallel_execution'] = True
config['agent']['max_workers'] = 4

with open('/tmp/config_parallel.yaml', 'w') as f:
    yaml.dump(config, f)

result_par = evaluate(config='/tmp/config_parallel.yaml')
par_time = result_par.total_time
par_runs = len(result_par.execution_runs)
print(f"  Total runs: {par_runs}")
print(f"  Total time: {par_time:.2f}s")
print()

# Compare
print("=" * 80)
print("Comparison")
print("=" * 80)
print(f"Sequential runs: {seq_runs}")
print(f"Parallel runs:   {par_runs}")
print(f"Runs match: {'✓' if seq_runs == par_runs else '✗'}")
print()
print(f"Sequential time: {seq_time:.2f}s")
print(f"Parallel time:   {par_time:.2f}s")

if par_time < seq_time * 0.8:  # At least 20% faster
    speedup = seq_time / par_time
    print(f"Speedup: {speedup:.2f}x ✓")
    print()
    print("✓ Parallel execution is working correctly!")
else:
    print(f"Speedup: {seq_time / par_time:.2f}x")
    print()
    print("⚠ Parallel execution may not be working properly")
    print("  (Expected parallel to be significantly faster)")

print()
print("Note: With fake API key, all requests fail fast,")
print("      so speedup may be minimal. Try with real API key for better results.")
