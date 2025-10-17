#!/bin/bash
#
# Safety Evaluation Example - Multiple Evalsets & Long Conversations
# Uses Google Gemini as the LLM provider
#
# This script demonstrates running safety evaluations using the judge-llm CLI
#

set -e  # Exit on error

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if .env file exists in project root and load it
if [ -f "../../.env" ]; then
    echo "Loading environment variables from .env..."
    set -a
    source ../../.env
    set +a
fi

# Check if GEMINI_API_KEY is set
if [ -z "$GEMINI_API_KEY" ]; then
    echo "ERROR: GEMINI_API_KEY environment variable is not set"
    echo ""
    echo "Please set your Gemini API key:"
    echo "  export GEMINI_API_KEY=\"your-api-key-here\""
    echo ""
    echo "Or add it to ../../.env file:"
    echo "  echo \"GEMINI_API_KEY=your-api-key-here\" >> ../../.env"
    echo ""
    echo "Get your API key from: https://aistudio.google.com/app/apikey"
    exit 1
fi

echo "======================================================================"
echo "SAFETY EVALUATION - Multiple Evalsets & Long Conversations"
echo "Using Google Gemini (gemini-2.0-flash-exp)"
echo "======================================================================"
echo ""
echo "This example demonstrates:"
echo "  • Loading multiple evalset files"
echo "  • Long multi-turn conversations (3-6 invocations)"
echo "  • Real LLM provider (Google Gemini)"
echo "  • Custom safety evaluator with multiple checks"
echo "  • Per-test-case evaluator configuration"
echo ""
echo "----------------------------------------------------------------------"
echo ""

# Option 1: Run using judge-llm CLI with config file
echo "Running evaluation using judge-llm CLI with Gemini provider..."
echo "Note: This will make real API calls to Google Gemini and incur costs"
echo ""

judge-llm run --config config.yaml

echo ""
echo "======================================================================"
echo "Evaluation completed!"
echo ""
echo "Reports generated in: ../../reports/04-safety-long-conversation/"
echo ""
echo "To view the HTML report, open:"
echo "  ../../reports/04-safety-long-conversation/safety_report.html"
echo ""
echo "======================================================================"

# Option 2: Run using Python script (commented out - uncomment to use)
# echo "Alternative: Running using Python script..."
# python run_evaluation.py

# Option 3: Run programmatically (commented out - uncomment to use)
# echo "Alternative: Running programmatically..."
# python run_evaluation.py --programmatic
