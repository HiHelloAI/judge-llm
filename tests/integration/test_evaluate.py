"""Integration tests for the main evaluate function."""

import json
import tempfile
from pathlib import Path
import pytest

from judge_llm.core.evaluate import evaluate
from judge_llm.core.models import EvalSet, EvalCase, SessionInput, Invocation, Content, Part, IntermediateData


class TestEvaluateIntegration:
    """Integration tests for evaluate function."""

    def test_evaluate_with_mock_provider(self, temp_dir):
        """Test end-to-end evaluation with mock provider."""
        # Create eval set file
        eval_set_data = {
            "eval_set_id": "integration_test",
            "name": "Integration Test",
            "creation_timestamp": 1234567890.0,
            "eval_cases": [
                {
                    "eval_id": "case1",
                    "session_input": {"app_name": "test", "user_id": "user1"},
                    "creation_timestamp": 1234567890.0,
                    "conversation": [
                        {
                            "invocation_id": "inv1",
                            "user_content": {
                                "role": "user",
                                "parts": [{"text": "Hello"}]
                            },
                            "final_response": {
                                "role": "model",
                                "parts": [{"text": "Hi there!"}]
                            },
                            "intermediate_data": {"tool_uses": [], "intermediate_responses": []},
                            "creation_timestamp": 1234567890.0
                        }
                    ]
                }
            ]
        }

        eval_set_path = temp_dir / "test_eval.json"
        with open(eval_set_path, "w") as f:
            json.dump(eval_set_data, f)

        # Create config
        config = {
            "agent": {
                "num_runs": 1,
                "parallel_execution": False
            },
            "dataset": {
                "loader": "local_file",
                "paths": [str(eval_set_path)]
            },
            "providers": [
                {
                    "name": "mock",
                    "type": "mock",
                    "agent_id": "test_agent",
                    "config": {}
                }
            ],
            "evaluators": [
                {
                    "type": "response_evaluator",
                    "config": {
                        "match_type": "exact",
                        "similarity_threshold": 0.8
                    }
                }
            ],
            "reporters": [
                {"type": "console"}
            ]
        }

        # Run evaluation
        report = evaluate(config)

        # Verify report
        assert report is not None
        assert len(report.execution_runs) > 0
        assert report.overall_success is not None

    def test_evaluate_with_multiple_evaluators(self, temp_dir):
        """Test evaluation with multiple evaluators."""
        eval_set_data = {
            "eval_set_id": "multi_eval_test",
            "name": "Multi Evaluator Test",
            "creation_timestamp": 1234567890.0,
            "eval_cases": [
                {
                    "eval_id": "case1",
                    "session_input": {"app_name": "test", "user_id": "user1"},
                    "creation_timestamp": 1234567890.0,
                    "conversation": [
                        {
                            "invocation_id": "inv1",
                            "user_content": {
                                "role": "user",
                                "parts": [{"text": "Test"}]
                            },
                            "final_response": {
                                "role": "model",
                                "parts": [{"text": "Response"}]
                            },
                            "intermediate_data": {"tool_uses": [], "intermediate_responses": []},
                            "creation_timestamp": 1234567890.0
                        }
                    ]
                }
            ]
        }

        eval_set_path = temp_dir / "test_eval.json"
        with open(eval_set_path, "w") as f:
            json.dump(eval_set_data, f)

        config = {
            "agent": {"num_runs": 1},
            "dataset": {
                "loader": "local_file",
                "paths": [str(eval_set_path)]
            },
            "providers": [{"name": "mock", "type": "mock", "agent_id": "test_agent"}],
            "evaluators": [
                {"type": "response_evaluator", "config": {"similarity_threshold": 0.5}},
                {"type": "cost_evaluator", "config": {"max_cost_per_case": 1.0}},
                {"type": "latency_evaluator", "config": {"max_latency_seconds": 10.0}}
            ],
            "reporters": [{"type": "console"}]
        }

        report = evaluate(config)

        assert report is not None
        # Verify multiple evaluators ran
        if len(report.execution_runs) > 0:
            run = report.execution_runs[0]
            assert len(run.evaluator_results) >= 3

    def test_evaluate_with_json_reporter(self, temp_dir):
        """Test evaluation with JSON reporter output."""
        eval_set_data = {
            "eval_set_id": "json_test",
            "name": "JSON Reporter Test",
            "creation_timestamp": 1234567890.0,
            "eval_cases": [
                {
                    "eval_id": "case1",
                    "session_input": {"app_name": "test", "user_id": "user1"},
                    "creation_timestamp": 1234567890.0,
                    "conversation": []
                }
            ]
        }

        eval_set_path = temp_dir / "test_eval.json"
        with open(eval_set_path, "w") as f:
            json.dump(eval_set_data, f)

        output_path = temp_dir / "report.json"

        config = {
            "agent": {"num_runs": 1},
            "dataset": {
                "loader": "local_file",
                "paths": [str(eval_set_path)]
            },
            "providers": [{"name": "mock", "type": "mock", "agent_id": "test_agent"}],
            "evaluators": [
                {"type": "response_evaluator", "config": {"similarity_threshold": 0.5}}
            ],
            "reporters": [
                {
                    "type": "json",
                    "output_path": str(output_path)
                }
            ]
        }

        report = evaluate(config)

        # Verify JSON file was created
        assert output_path.exists()

        # Verify JSON is valid
        with open(output_path, 'r') as f:
            data = json.load(f)

        assert data is not None

    def test_evaluate_with_database_reporter(self, temp_dir):
        """Test evaluation with database reporter."""
        eval_set_data = {
            "eval_set_id": "db_test",
            "name": "Database Test",
            "creation_timestamp": 1234567890.0,
            "eval_cases": [
                {
                    "eval_id": "case1",
                    "session_input": {"app_name": "test", "user_id": "user1"},
                    "creation_timestamp": 1234567890.0,
                    "conversation": []
                }
            ]
        }

        eval_set_path = temp_dir / "test_eval.json"
        with open(eval_set_path, "w") as f:
            json.dump(eval_set_data, f)

        db_path = temp_dir / "results.db"

        config = {
            "agent": {"num_runs": 1},
            "dataset": {
                "loader": "local_file",
                "paths": [str(eval_set_path)]
            },
            "providers": [{"name": "mock", "type": "mock", "agent_id": "test_agent"}],
            "evaluators": [
                {"type": "response_evaluator", "config": {"similarity_threshold": 0.5}}
            ],
            "reporters": [
                {
                    "type": "database",
                    "db_path": str(db_path)
                }
            ]
        }

        report = evaluate(config)

        # Verify database file was created
        assert db_path.exists()

    def test_evaluate_with_multiple_cases(self, temp_dir):
        """Test evaluation with multiple test cases."""
        eval_set_data = {
            "eval_set_id": "multi_case_test",
            "name": "Multi Case Test",
            "creation_timestamp": 1234567890.0,
            "eval_cases": [
                {
                    "eval_id": f"case{i}",
                    "session_input": {"app_name": "test", "user_id": f"user{i}"},
                    "creation_timestamp": 1234567890.0,
                    "conversation": [
                        {
                            "invocation_id": "inv1",
                            "user_content": {
                                "role": "user",
                                "parts": [{"text": f"Test {i}"}]
                            },
                            "final_response": {
                                "role": "model",
                                "parts": [{"text": f"Response {i}"}]
                            },
                            "intermediate_data": {"tool_uses": [], "intermediate_responses": []},
                            "creation_timestamp": 1234567890.0
                        }
                    ]
                }
                for i in range(5)
            ]
        }

        eval_set_path = temp_dir / "test_eval.json"
        with open(eval_set_path, "w") as f:
            json.dump(eval_set_data, f)

        config = {
            "agent": {"num_runs": 1},
            "dataset": {
                "loader": "local_file",
                "paths": [str(eval_set_path)]
            },
            "providers": [{"name": "mock", "type": "mock", "agent_id": "test_agent"}],
            "evaluators": [
                {"type": "response_evaluator", "config": {"similarity_threshold": 0.5}}
            ],
            "reporters": [{"type": "console"}]
        }

        report = evaluate(config)

        # Verify all cases were evaluated
        assert len(report.execution_runs) >= 5

    def test_evaluate_with_parallel_execution(self, temp_dir):
        """Test evaluation with parallel execution enabled."""
        eval_set_data = {
            "eval_set_id": "parallel_test",
            "name": "Parallel Test",
            "creation_timestamp": 1234567890.0,
            "eval_cases": [
                {
                    "eval_id": f"case{i}",
                    "session_input": {"app_name": "test", "user_id": f"user{i}"},
                    "creation_timestamp": 1234567890.0,
                    "conversation": []
                }
                for i in range(10)
            ]
        }

        eval_set_path = temp_dir / "test_eval.json"
        with open(eval_set_path, "w") as f:
            json.dump(eval_set_data, f)

        config = {
            "agent": {
                "num_runs": 1,
                "parallel_execution": True,
                "max_workers": 4
            },
            "dataset": {
                "loader": "local_file",
                "paths": [str(eval_set_path)]
            },
            "providers": [{"name": "mock", "type": "mock", "agent_id": "test_agent"}],
            "evaluators": [
                {"type": "response_evaluator", "config": {"similarity_threshold": 0.5}}
            ],
            "reporters": [{"type": "console"}]
        }

        report = evaluate(config)

        # Should complete successfully
        assert report is not None
        assert len(report.execution_runs) >= 10

    def test_evaluate_with_per_case_config_override(self, temp_dir):
        """Test evaluation with per-case evaluator config overrides."""
        eval_set_data = {
            "eval_set_id": "override_test",
            "name": "Override Test",
            "creation_timestamp": 1234567890.0,
            "eval_cases": [
                {
                    "eval_id": "case1",
                    "session_input": {"app_name": "test", "user_id": "user1"},
                    "creation_timestamp": 1234567890.0,
                    "conversation": [
                        {
                            "invocation_id": "inv1",
                            "user_content": {
                                "role": "user",
                                "parts": [{"text": "Test"}]
                            },
                            "final_response": {
                                "role": "model",
                                "parts": [{"text": "Response"}]
                            },
                            "intermediate_data": {"tool_uses": [], "intermediate_responses": []},
                            "creation_timestamp": 1234567890.0
                        }
                    ],
                    "evaluator_config": {
                        "response": {
                            "similarity_threshold": 0.95
                        }
                    }
                }
            ]
        }

        eval_set_path = temp_dir / "test_eval.json"
        with open(eval_set_path, "w") as f:
            json.dump(eval_set_data, f)

        config = {
            "agent": {"num_runs": 1},
            "dataset": {
                "loader": "local_file",
                "paths": [str(eval_set_path)]
            },
            "providers": [{"name": "mock", "type": "mock", "agent_id": "test_agent"}],
            "evaluators": [
                {"type": "response_evaluator", "config": {"similarity_threshold": 0.5}}
            ],
            "reporters": [{"type": "console"}]
        }

        report = evaluate(config)

        # Verify evaluation ran with overridden config
        assert report is not None

    def test_evaluate_summary_statistics(self, temp_dir):
        """Test that evaluation report contains summary statistics."""
        eval_set_data = {
            "eval_set_id": "stats_test",
            "name": "Statistics Test",
            "creation_timestamp": 1234567890.0,
            "eval_cases": [
                {
                    "eval_id": f"case{i}",
                    "session_input": {"app_name": "test", "user_id": f"user{i}"},
                    "creation_timestamp": 1234567890.0,
                    "conversation": []
                }
                for i in range(3)
            ]
        }

        eval_set_path = temp_dir / "test_eval.json"
        with open(eval_set_path, "w") as f:
            json.dump(eval_set_data, f)

        config = {
            "agent": {"num_runs": 1},
            "dataset": {
                "loader": "local_file",
                "paths": [str(eval_set_path)]
            },
            "providers": [{"name": "mock", "type": "mock", "agent_id": "test_agent"}],
            "evaluators": [
                {"type": "response_evaluator", "config": {"similarity_threshold": 0.5}}
            ],
            "reporters": [{"type": "console"}]
        }

        report = evaluate(config)

        # Verify summary statistics
        assert hasattr(report, "summary")
        assert hasattr(report, "total_cost")
        assert hasattr(report, "total_time")
        assert hasattr(report, "success_rate")

    def test_evaluate_error_handling(self, temp_dir):
        """Test evaluation error handling."""
        # Create config with invalid dataset path
        config = {
            "agent": {"num_runs": 1},
            "dataset": {
                "loader": "local_file",
                "paths": ["/nonexistent/file.json"]
            },
            "providers": [{"name": "mock", "type": "mock", "agent_id": "test_agent"}],
            "evaluators": [
                {"type": "response_evaluator", "config": {"similarity_threshold": 0.5}}
            ],
            "reporters": [{"type": "console"}]
        }

        # Should raise appropriate error
        with pytest.raises(Exception):
            evaluate(config)
