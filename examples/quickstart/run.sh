#!/bin/bash

# Quickstart example using CLI

echo "Running Judge LLM Quickstart Example via CLI"
echo "=============================================="
echo ""

# Option 1: Run from config file
echo "Option 1: Running from config.yaml..."
judge-llm run --config config.yaml

# Option 2: Run with CLI arguments
# Uncomment to test
# echo ""
# echo "Option 2: Running with CLI arguments..."
# judge-llm run \
#   --dataset ./sample.evalset.json \
#   --provider mock \
#   --agent-id news_agent \
#   --num-runs 1 \
#   --log-level INFO \
#   --report console \
#   --report json \
#   --output ./cli_report.json

# List available providers and evaluators
echo ""
echo "Available providers:"
judge-llm list providers

echo ""
echo "Available evaluators:"
judge-llm list evaluators
