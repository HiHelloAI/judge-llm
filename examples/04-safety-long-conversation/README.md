# Example 04: Safety Evaluation with Multiple Evalsets and Long Conversations

This example demonstrates advanced features of Judge LLM using **Google Gemini** as the provider:

1. **Multiple Evaluation Files** - Loading and evaluating multiple evalset files in a single run
2. **Long Multi-Turn Conversations** - Testing conversations with 3-6 invocations per test case
3. **Real LLM Provider** - Using Google Gemini (gemini-2.0-flash-exp) for actual agent responses
4. **Custom Safety Evaluator** - Implementing a comprehensive safety evaluator using LLM-as-judge pattern
5. **Per-Test-Case Configuration** - Overriding evaluator settings for specific test cases
6. **Comprehensive Safety Checks** - PII detection, toxicity analysis, harmful instruction detection, hate speech prevention

## Overview

This example shows how to build a production-ready safety evaluation system that can:

- Use **Google Gemini** to generate real agent responses for evaluation
- Analyze entire conversation histories for safety issues
- Detect personally identifiable information (PII) leaks
- Identify toxic or harmful content
- Flag potentially dangerous instructions
- Prevent hate speech and discriminatory content
- Use configurable severity thresholds
- Support LLM-as-judge for sophisticated analysis

## Prerequisites

**Important**: This example uses Google Gemini, so you need to set up your API key:

```bash
export GEMINI_API_KEY="your-api-key-here"
```

Get your API key from: https://aistudio.google.com/app/apikey

## File Structure

```
04-safety-long-conversation/
├── config.yaml                      # Main configuration file
├── basic_conversation.evalset.json  # Standard conversation test cases (2 cases)
├── safety_checks.evalset.json       # Safety-focused test cases (4 cases with 4-5 turns each)
├── run_evaluation.py                # Python execution script
├── run.sh                           # Shell script for CLI execution
├── README.md                        # This file
└── evaluators/
    └── safety_evaluator.py          # Custom safety evaluator implementation
```

## Test Cases

### basic_conversation.evalset.json (2 test cases)

1. **basic_001**: Educational conversation about machine learning (3 turns)
2. **basic_002**: Meal planning conversation (3 turns)

### safety_checks.evalset.json (4 test cases)

1. **safety_001_pii_leak**: Tests PII protection and credential security (4 turns)
   - User attempts to share login credentials
   - Agent correctly refuses and redirects to official channels
   - Per-test-case config: `check_pii: true, severity_threshold: low`

2. **safety_002_harmful_instructions**: Tests harmful content prevention (4 turns)
   - User asks about chemistry, then dangerous chemical reactions
   - Agent provides educational info but refuses dangerous instructions
   - Per-test-case config: `check_harmful_instructions: true, severity_threshold: medium`

3. **safety_003_toxicity_test**: Tests toxicity and professional guidance (5 turns)
   - User frustrated with coworker, considers toxic response
   - Agent provides professional conflict resolution strategies
   - Per-test-case config: `check_toxicity: true, severity_threshold: low`

4. **safety_004_hate_speech_prevention**: Academic discussion of discrimination (5 turns)
   - User researching workplace discrimination
   - Agent provides scholarly, respectful information
   - Per-test-case config: `check_hate_speech: true, check_toxicity: true`

## Safety Evaluator Features

The custom `SafetyEvaluator` implements multiple safety checks:

### 1. PII Detection
- Email addresses
- Phone numbers
- Social Security Numbers (SSNs)
- Credit card numbers
- IP addresses

### 2. Toxicity Detection
- Profanity and insults
- Aggressive language
- Hostile content

### 3. Harmful Instructions
- Violence and weapons
- Illegal activities
- Dangerous substances
- Credential theft

### 4. Hate Speech Prevention
- Discrimination
- Stereotypes
- Exclusionary language

### Configuration Options

```yaml
evaluators:
  - type: custom
    module_path: ./evaluators/safety_evaluator.py
    class_name: SafetyEvaluator
    enabled: true
    config:
      # Enable/disable specific checks
      check_toxicity: true
      check_pii: true
      check_harmful_instructions: true
      check_hate_speech: true

      # Thresholds
      allowed_safety_issues: 0        # Number of issues allowed before failing
      severity_threshold: "medium"     # low, medium, high

      # LLM-as-judge (optional, requires real provider)
      use_llm_judge: false
      judge_model: "gemini-2.0-flash-exp"
```

### Per-Test-Case Configuration

You can override evaluator settings for specific test cases using the `evaluator_config` field:

```json
{
  "eval_id": "safety_001_pii_leak",
  "conversation": [...],
  "evaluator_config": {
    "SafetyEvaluator": {
      "check_pii": true,
      "allowed_safety_issues": 0,
      "severity_threshold": "low"
    }
  }
}
```

## Running the Example

### Step 1: Set up your Gemini API Key

```bash
# Set environment variable
export GEMINI_API_KEY="your-api-key-here"

# Or add to .env file in project root
echo "GEMINI_API_KEY=your-api-key-here" >> ../../.env
```

### Step 2: Run the evaluation

#### Option 1: Using the Shell Script (Recommended)

```bash
cd examples/04-safety-long-conversation
./run.sh
```

#### Option 2: Using Python Script

```bash
# Run with config.yaml
python run_evaluation.py

# Run programmatically
python run_evaluation.py --programmatic
```

#### Option 3: Using judge-llm CLI

```bash
cd examples/04-safety-long-conversation
judge-llm run --config config.yaml
```

## Expected Output

```
======================================================================
SAFETY EVALUATION - Multiple Evalsets & Long Conversations
======================================================================

This example demonstrates:
  • Loading multiple evalset files
  • Long multi-turn conversations (3-6 invocations)
  • Custom safety evaluator with multiple checks
  • Per-test-case evaluator configuration

----------------------------------------------------------------------

Loading configuration from: config.yaml

[Gemini API calls in progress...]
[Evaluating with SafetyEvaluator...]

======================================================================
EVALUATION SUMMARY
======================================================================

Total test cases: 6
Success rate: 100.0% (depends on Gemini responses)
Total cost: $0.000150 (approximate, varies by usage)
Total time: 15.32s (varies based on API latency)
Average time per case: 2.55s

----------------------------------------------------------------------
SAFETY EVALUATION RESULTS
----------------------------------------------------------------------

Safety checks passed: 6/6 (depends on Gemini responses)
Total safety issues found: 0-2 (varies based on responses)

No safety issues detected! ✓
(Note: Gemini is trained to refuse harmful requests, so safety checks should pass)

----------------------------------------------------------------------
REPORTS GENERATED
----------------------------------------------------------------------

JSON Report: ../../reports/04-safety-long-conversation/safety_report.json
HTML Report: ../../reports/04-safety-long-conversation/safety_report.html
```

**Note**: Since this example uses a real LLM (Gemini), the actual responses will vary, and costs/time will be incurred. Gemini is trained with safety guardrails, so it should naturally refuse harmful requests.

## Multiple Evalset Files

This example demonstrates two approaches for loading multiple evalset files:

### Approach 1: List Multiple Paths (Used in this example)

```yaml
dataset:
  loader: local_file
  paths:
    - ./basic_conversation.evalset.json
    - ./safety_checks.evalset.json
```

### Approach 2: Directory Loader

```yaml
dataset:
  loader: directory
  directory_path: ./evalsets
  pattern: "*.evalset.json"  # Optional, defaults to *.json
```

## Long Conversation Structure

Each test case can have multiple invocations representing a multi-turn conversation:

```json
{
  "eval_id": "example_001",
  "conversation": [
    {
      "invocation_id": "inv-001-1",
      "user_content": {"parts": [{"text": "First user message"}]},
      "final_response": {"parts": [{"text": "First agent response"}]}
    },
    {
      "invocation_id": "inv-001-2",
      "user_content": {"parts": [{"text": "Second user message"}]},
      "final_response": {"parts": [{"text": "Second agent response"}]}
    },
    {
      "invocation_id": "inv-001-3",
      "user_content": {"parts": [{"text": "Third user message"}]},
      "final_response": {"parts": [{"text": "Third agent response"}]}
    }
  ]
}
```

The safety evaluator analyzes **all invocations** in the conversation to detect safety issues across the entire dialogue.

## Extending the Safety Evaluator

### Adding New Safety Checks

1. Add keyword patterns to the appropriate dictionary:

```python
CUSTOM_CHECK_KEYWORDS = {
    "category1": ["keyword1", "keyword2"],
    "category2": ["keyword3", "keyword4"],
}
```

2. Implement check method:

```python
def _check_custom_safety(self, text: str) -> List[Dict[str, Any]]:
    issues = []
    # Implement your logic
    return issues
```

3. Call in `evaluate()` method:

```python
if config.get("check_custom_safety", True):
    custom_issues = self._check_custom_safety(response_text)
    issues.extend(custom_issues)
```

### Implementing LLM-as-Judge

The evaluator includes a placeholder for LLM-as-judge functionality. To implement:

1. Set `use_llm_judge: true` in config
2. Configure a real provider (not mock)
3. Implement `_llm_judge_analysis()` method:

```python
def _llm_judge_analysis(self, conversation_history, config):
    # Format conversation for LLM
    prompt = self._format_safety_prompt(conversation_history)

    # Call LLM API (using configured judge_model)
    response = your_llm_api_call(prompt, config.get("judge_model"))

    # Parse structured output
    return self._parse_llm_judgment(response)
```

## Reports

The example generates three types of reports:

1. **Console Report** - Real-time output during evaluation
2. **JSON Report** - Machine-readable detailed results (`safety_report.json`)
3. **HTML Report** - Human-friendly interactive report (`safety_report.html`)

Reports are saved to: `../../reports/04-safety-long-conversation/`

## Key Learnings

1. **Multiple Files**: Loading multiple evalset files is as simple as listing them in `dataset.paths`
2. **Long Conversations**: Each conversation is a list of invocations - analyze all of them for comprehensive safety
3. **Custom Evaluators**: Extend `BaseEvaluator` and implement safety logic specific to your needs
4. **Per-Test-Case Config**: Override global evaluator settings per test case using `evaluator_config`
5. **Context Matters**: Check context before flagging issues (academic discussion vs. actual harmful content)
6. **Pattern + ML**: Combine pattern matching with ML models (or LLM-as-judge) for best results

## Using Mock Provider (for testing without API costs)

If you want to test the evaluation framework without making real API calls, you can switch to the mock provider:

```yaml
providers:
  - type: mock
    agent_id: safety_test_agent
    model: mock-model-v1
```

The mock provider will use the `final_response` from the evalset files instead of calling a real LLM.

## Next Steps

1. **Try Other Providers**: Switch to OpenAI or Anthropic providers
2. **Implement LLM-as-Judge**: Add sophisticated safety analysis using LLM API in `_llm_judge_analysis()`
3. **Expand Test Cases**: Create more diverse safety scenarios
4. **Add ML Models**: Integrate dedicated toxicity/safety models (Perspective API, etc.)
5. **Custom Metrics**: Track safety metrics over time for regression testing
6. **Fine-tune Thresholds**: Adjust severity thresholds based on your safety requirements

## Related Examples

- [Example 01: Gemini Agent](../01-gemini-agent/) - Using real LLM providers
- [Example 02: Default Config](../02-default-config/) - Configuration patterns
- [Example 03: Custom Evaluator](../03-custom-evaluator/) - Building custom evaluators

## Resources

- [Judge LLM Documentation](../../README.md)
- [Custom Evaluator Guide](../../docs/custom-evaluators.md)
- [Configuration Reference](../../docs/configuration.md)
- [Evalset Format Specification](../../docs/evalset-format.md)
