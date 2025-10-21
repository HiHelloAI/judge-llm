"""JSON reporter"""

import json
from pathlib import Path
from judge_llm.core.models import EvaluationReport
from judge_llm.reporters.base import BaseReporter
from judge_llm.utils.logger import get_logger


class JSONReporter(BaseReporter):
    """Report evaluation results to JSON file"""

    def __init__(self, output_path: str):
        """Initialize JSON reporter

        Args:
            output_path: Path to output JSON file
        """
        self.output_path = Path(output_path).expanduser().resolve()
        self.logger = get_logger()

    def generate_report(self, report: EvaluationReport):
        """Generate JSON report

        Args:
            report: EvaluationReport object
        """
        self.logger.debug(f"Generating JSON report at {self.output_path}")

        try:
            # Convert report to dictionary
            report_dict = report.model_dump(mode='json')

            # Write to file with streaming for memory efficiency
            self.output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(self.output_path, 'w', encoding='utf-8') as f:
                json.dump(report_dict, f, indent=2, ensure_ascii=False)

            self.logger.info(f"📊 JSON report saved: {self.output_path}")

        except Exception as e:
            self.logger.error(f"Error generating JSON report: {e}")
            raise

    def cleanup(self):
        """Cleanup resources"""
        pass
