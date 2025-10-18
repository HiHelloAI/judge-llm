#!/usr/bin/env python3
"""Test script for database reporter"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from judge_llm.core.evaluate import evaluate

def main():
    """Run evaluation with database reporter"""
    print("Testing Database Reporter...")
    print("-" * 50)

    config_path = Path(__file__).parent / "config.yaml"

    try:
        # Run evaluation
        report = evaluate(config=str(config_path))

        print("\n" + "=" * 50)
        print("Evaluation completed successfully!")
        print(f"Total runs: {len(report.execution_runs)}")
        print(f"Success rate: {report.success_rate:.2%}")
        print(f"Database file should be created at: ./test_results.db")
        print("=" * 50)

        # Check if database file was created
        db_path = Path(__file__).parent / "test_results.db"
        if db_path.exists():
            print(f"\n✅ Database file created: {db_path}")
            print(f"   File size: {db_path.stat().st_size} bytes")
        else:
            print(f"\n❌ Database file NOT found at: {db_path}")

        return 0

    except Exception as e:
        print(f"\n❌ Error during evaluation: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
