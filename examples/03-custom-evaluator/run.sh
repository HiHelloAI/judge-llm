#!/bin/bash

# Quickstart example using CLI

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to the script directory
cd "$SCRIPT_DIR"

# Load environment variables from .env file if it exists
if [ -f "../../.env" ]; then
    echo "Loading environment variables from .env file..."
    # Export all variables from .env file
    set -a
    source ../../.env
    set +a
    echo "✓ Environment variables loaded"
else
    echo "⚠ No .env file found (optional)"
fi

echo ""
echo "Running Judge LLM Quickstart Example via CLI"
echo "=============================================="
echo "Working directory: $(pwd)"
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
