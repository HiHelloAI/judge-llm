#!/bin/bash

# Run script for Google ADK Agent example
# This script runs the evaluation using the Judge LLM CLI

set -e

echo "=========================================="
echo "Google ADK Agent Evaluation Example"
echo "=========================================="
echo ""

# Check for API key
if [ -z "$GOOGLE_API_KEY" ]; then
    echo "Warning: GOOGLE_API_KEY environment variable is not set"
    echo "Please set it with: export GOOGLE_API_KEY='your-key-here'"
    echo ""
    read -p "Do you want to continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "Working directory: $SCRIPT_DIR"
echo "Config file: config.yaml"
echo ""

# Change to script directory
cd "$SCRIPT_DIR"

# Run evaluation
echo "Running evaluation..."
echo ""

judge-llm run --config config.yaml

echo ""
echo "=========================================="
echo "Evaluation Complete!"
echo "=========================================="
echo ""
echo "Check the reports in: ../../reports/09-google-adk-agent/"
echo ""
