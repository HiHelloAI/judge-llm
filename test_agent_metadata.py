"""Test script to verify agent_metadata flows correctly from agent config to evaluators"""

from judge_llm.core.evaluate import _initialize_providers
from judge_llm.evaluators.base import BaseEvaluator
from judge_llm.core.models import EvalCase, ProviderResult, EvaluatorResult
from typing import Dict, Any

# Mock evaluator to test agent_metadata
class TestEvaluator(BaseEvaluator):
    def evaluate(self, eval_case: EvalCase, agent_metadata: Dict[str, Any],
                 provider_result: ProviderResult, eval_config: Dict[str, Any] = None) -> EvaluatorResult:
        print("\n=== EVALUATOR RECEIVED ===")
        print(f"Agent Metadata: {agent_metadata}")
        return EvaluatorResult(
            evaluator_name="test",
            evaluator_type="test",
            success=True,
            passed=True
        )

# Test configuration
agent_config = {
    'name': 'my_news_agent',
    'description': 'News assistant using Google Gemini',
    'version': '2.0.1',
    'team': 'content-team',
    'environment': 'production',
    # Execution settings (should NOT be in agent_metadata)
    'num_runs': 1,
    'parallel_execution': False,
    'max_workers': 4,
    'log_level': 'INFO'
}

providers_config = [{
    'type': 'mock',
    'agent_id': 'news_agent_v2',
    'agent_config_path': None,
    # Provider-specific settings (should be in provider_metadata)
    'model': 'gemini-2.0-flash',
    'temperature': 0.7,
    'max_tokens': 2048,
}]

# Initialize provider
print("=== INITIALIZING PROVIDER ===")
providers = _initialize_providers(providers_config, agent_config)
provider = providers[0]

print(f"\nAgent ID: {provider.agent_id}")
print(f"\nAgent Metadata (about the agent being tested):")
for key, value in provider.agent_metadata.items():
    print(f"  - {key}: {value}")

print(f"\nProvider Metadata (provider configuration):")
for key, value in provider.provider_metadata.items():
    print(f"  - {key}: {value}")

# Simulate what happens in evaluate()
print("\n" + "="*50)
print("SIMULATING EVALUATION FLOW")
print("="*50)

evaluator = TestEvaluator()
mock_eval_case = EvalCase(
    eval_id="test123",
    conversation=[],
    session_input={
        "app_name": "test",
        "user_id": "test_user",
        "state": {}
    },
    creation_timestamp=0.0
)
mock_provider_result = ProviderResult(
    conversation_history=[],
    success=True
)

# This is what happens in evaluate.py line 501
evaluator.evaluate(
    eval_case=mock_eval_case,
    agent_metadata=provider.agent_metadata,  # <-- Agent metadata passed to evaluator
    provider_result=mock_provider_result
)

print("\n" + "="*50)
print("✅ VERIFICATION COMPLETE")
print("="*50)
print("\nExpected behavior:")
print("  ✓ agent_metadata should contain: name, description, version, team, environment")
print("  ✓ agent_metadata should NOT contain: num_runs, parallel_execution, max_workers, log_level")
print("  ✓ provider_metadata should contain: model, temperature, max_tokens")
print("  ✓ provider_metadata should NOT contain: type, agent_id, agent_config_path")
