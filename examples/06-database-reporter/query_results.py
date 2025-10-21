#!/usr/bin/env python3
"""
Query and analyze results from the database

This script demonstrates various SQL queries you can run against
the evaluation results database.
"""

import sqlite3
import json
from pathlib import Path


def query_database(db_path: str):
    """Query and display database contents"""

    db_file = Path(db_path)
    if not db_file.exists():
        print(f"❌ Database not found: {db_path}")
        print(f"\nPlease run the evaluation first:")
        print(f"  python run_evaluation.py")
        return

    conn = sqlite3.connect(str(db_file))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    print("=" * 80)
    print(f"📊 Math Tutor Evaluation Results")
    print("=" * 80)

    # Query 1: Overall summary
    print("\n📋 OVERALL SUMMARY")
    print("-" * 80)
    cursor.execute("""
        SELECT
            COUNT(DISTINCT report_id) as total_reports,
            COUNT(*) as total_runs,
            SUM(CASE WHEN overall_success = 1 THEN 1 ELSE 0 END) as successful_runs,
            SUM(cost) as total_cost,
            SUM(time_taken) as total_time,
            AVG(cost) as avg_cost,
            AVG(time_taken) as avg_time
        FROM execution_runs
    """)

    row = cursor.fetchone()
    if row and row['total_runs'] > 0:
        success_rate = (row['successful_runs'] / row['total_runs'] * 100)
        print(f"Total evaluation reports: {row['total_reports']}")
        print(f"Total test executions: {row['total_runs']}")
        print(f"Successful executions: {row['successful_runs']} ({success_rate:.1f}%)")
        print(f"\nCost metrics:")
        print(f"  Total cost: ${row['total_cost']:.4f}")
        print(f"  Average cost per run: ${row['avg_cost']:.4f}")
        print(f"\nTime metrics:")
        print(f"  Total time: {row['total_time']:.2f}s")
        print(f"  Average time per run: {row['avg_time']:.2f}s")

    # Query 2: Results by test case
    print("\n\n📝 RESULTS BY TEST CASE")
    print("-" * 80)
    cursor.execute("""
        SELECT
            eval_case_id,
            COUNT(*) as runs,
            SUM(CASE WHEN overall_success = 1 THEN 1 ELSE 0 END) as passed,
            AVG(cost) as avg_cost,
            AVG(time_taken) as avg_time
        FROM execution_runs
        GROUP BY eval_case_id
        ORDER BY eval_case_id
    """)

    for row in cursor.fetchall():
        pass_rate = (row['passed'] / row['runs'] * 100) if row['runs'] > 0 else 0
        status = "✅" if pass_rate == 100 else "⚠️" if pass_rate > 0 else "❌"
        print(f"\n{status} {row['eval_case_id']}")
        print(f"   Runs: {row['runs']} | Passed: {row['passed']} ({pass_rate:.0f}%)")
        print(f"   Avg Cost: ${row['avg_cost']:.4f} | Avg Time: {row['avg_time']:.2f}s")

    # Query 3: Evaluator performance
    print("\n\n🎯 EVALUATOR PERFORMANCE")
    print("-" * 80)
    cursor.execute("""
        SELECT
            evaluator_name,
            evaluator_type,
            COUNT(*) as total,
            SUM(CASE WHEN passed = 1 THEN 1 ELSE 0 END) as passed,
            AVG(score) as avg_score,
            MIN(score) as min_score,
            MAX(score) as max_score
        FROM evaluator_results
        WHERE score IS NOT NULL
        GROUP BY evaluator_name, evaluator_type
    """)

    for row in cursor.fetchall():
        pass_rate = (row['passed'] / row['total'] * 100) if row['total'] > 0 else 0
        print(f"\nEvaluator: {row['evaluator_name']} ({row['evaluator_type']})")
        print(f"  Total evaluations: {row['total']}")
        print(f"  Pass rate: {row['passed']}/{row['total']} ({pass_rate:.1f}%)")
        if row['avg_score'] is not None:
            print(f"  Score range: {row['min_score']:.2f} - {row['max_score']:.2f} (avg: {row['avg_score']:.2f})")

    # Query 4: Recent evaluation runs
    print("\n\n📅 RECENT EVALUATION RUNS (Last 5)")
    print("-" * 80)
    cursor.execute("""
        SELECT
            report_id,
            generated_at,
            total_cost,
            total_time,
            success_rate,
            overall_success
        FROM reports
        ORDER BY generated_at DESC
        LIMIT 5
    """)

    for i, row in enumerate(cursor.fetchall(), 1):
        status = "✅" if row['overall_success'] else "❌"
        print(f"\n{i}. {status} {row['report_id']}")
        print(f"   Generated: {row['generated_at']}")
        print(f"   Success rate: {row['success_rate']:.1%}")
        print(f"   Cost: ${row['total_cost']:.4f} | Time: {row['total_time']:.2f}s")

    # Query 5: Trend analysis (if multiple runs)
    print("\n\n📈 TREND ANALYSIS")
    print("-" * 80)
    cursor.execute("""
        SELECT
            DATE(generated_at) as date,
            COUNT(*) as num_reports,
            SUM(total_cost) as daily_cost,
            AVG(success_rate) as avg_success_rate
        FROM reports
        GROUP BY DATE(generated_at)
        ORDER BY date DESC
        LIMIT 10
    """)

    rows = cursor.fetchall()
    if len(rows) > 0:
        print("\nDaily summary:")
        for row in rows:
            print(f"  {row['date']}: {row['num_reports']} report(s), "
                  f"${row['daily_cost']:.4f} cost, "
                  f"{row['avg_success_rate']:.1%} success rate")
    else:
        print("\nNot enough data for trend analysis. Run evaluations multiple times!")

    # Query 6: Sample a detailed result
    print("\n\n🔍 SAMPLE DETAILED RESULT")
    print("-" * 80)
    cursor.execute("""
        SELECT
            execution_id,
            eval_case_id,
            provider_type,
            overall_success,
            cost,
            time_taken,
            token_usage_json
        FROM execution_runs
        ORDER BY RANDOM()
        LIMIT 1
    """)

    row = cursor.fetchone()
    if row:
        print(f"\nExecution: {row['execution_id']}")
        print(f"Test case: {row['eval_case_id']}")
        print(f"Provider: {row['provider_type']}")
        print(f"Status: {'✅ Success' if row['overall_success'] else '❌ Failed'}")
        print(f"Cost: ${row['cost']:.4f}")
        print(f"Time: {row['time_taken']:.2f}s")

        if row['token_usage_json']:
            try:
                token_usage = json.loads(row['token_usage_json'])
                print(f"Token usage: {token_usage}")
            except:
                pass

    conn.close()
    print("\n" + "=" * 80)


def main():
    """Main function"""
    import sys

    # Use default database path
    default_db = Path(__file__).parent.parent.parent / "reports" / "06-database-reporter" / "results.db"

    if len(sys.argv) > 1:
        db_path = sys.argv[1]
    else:
        db_path = str(default_db)

    query_database(db_path)

    print("\nTip: You can also query the database using:")
    print(f"  sqlite3 {db_path}")
    print("\nOr use a GUI tool like DB Browser for SQLite")
    print()


if __name__ == "__main__":
    main()
