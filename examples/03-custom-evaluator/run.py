"""Custom evaluator example - Register and use custom evaluators"""

from judge_llm import evaluate, register_evaluator
from evaluators.sentiment_evaluator import SentimentEvaluator

if __name__ == "__main__":
    print("Custom Evaluator Example\n")
    print("=" * 60)

    # Option 1: Run from config file with custom evaluator
    print("\nOption 1: Running from config file (custom evaluator loaded from file)...")
    report = evaluate(config="config.yaml")

    print(f"\nEvaluation completed!")
    print(f"Total executions: {len(report.execution_runs)}")
    print(f"Success rate: {report.success_rate:.1%}")

    # Check custom evaluator results
    for exec_run in report.execution_runs:
        print(f"\nEval case: {exec_run.eval_case_id}")
        for eval_result in exec_run.evaluator_results:
            if eval_result.evaluator_type == "sentiment":
                print(f"  Sentiment score: {eval_result.score:.2f}")
                print(f"  Positive words: {eval_result.details.get('total_positive_words', 0)}")
                print(f"  Negative words: {eval_result.details.get('total_negative_words', 0)}")

    # Option 2: Register custom evaluator programmatically
    print("\n\nOption 2: Programmatic registration...")
    register_evaluator("sentiment", SentimentEvaluator)

    report = evaluate(
        agent={
            "log_level": "INFO",
            "num_runs": 1,
        },
        dataset={
            "loader": "local_file",
            "paths": ["./sample.evalset.json"]
        },
        providers=[{"type": "mock", "agent_id": "news_agent"}],
        evaluators=[
            {
                "type": "sentiment",
                "enabled": True,
                "config": {"min_positive_sentiment": 0.3},
            }
        ],
        reporters=[{"type": "console"}]
    )

    print(f"\nEvaluation completed!")
    print(f"Success rate: {report.success_rate:.1%}")
