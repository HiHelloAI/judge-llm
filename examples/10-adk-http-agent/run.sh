#!/bin/bash
# Run ADK HTTP Agent Evaluation
#
# Usage:
#   ./run.sh                    # Run with default config
#   ./run.sh --dry-run          # Validate config without running
#   ADK_API_KEY=xxx ./run.sh    # Run with API key

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Create reports directory if it doesn't exist
mkdir -p ../../reports/10-adk-http-agent

# Check if ADK_API_KEY is set (if using authentication)
if [ -z "$ADK_API_KEY" ]; then
    echo "Note: ADK_API_KEY not set. If your endpoint requires authentication, set it with:"
    echo "  export ADK_API_KEY=your_api_key"
    echo ""
fi

# Run the evaluation
echo "Running ADK HTTP Agent Evaluation..."
echo "Config: config.yaml"
echo "Dataset: sample.evalset.yaml"
echo ""

judge-llm run --config config.yaml "$@"
