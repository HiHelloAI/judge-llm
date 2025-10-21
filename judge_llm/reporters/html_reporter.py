"""HTML reporter"""

import json
from pathlib import Path
from jinja2 import Template
from judge_llm.core.models import EvaluationReport
from judge_llm.reporters.base import BaseReporter
from judge_llm.utils.logger import get_logger


class HTMLReporter(BaseReporter):
    """Report evaluation results to HTML file"""

    def __init__(self, output_path: str):
        """Initialize HTML reporter

        Args:
            output_path: Path to output HTML file
        """
        self.output_path = Path(output_path).expanduser().resolve()
        self.logger = get_logger()

        # Load template
        template_path = Path(__file__).parent.parent / "templates" / "report.html"
        with open(template_path, 'r', encoding='utf-8') as f:
            self.template = Template(f.read())

    def generate_report(self, report: EvaluationReport):
        """Generate HTML report

        Args:
            report: EvaluationReport object
        """
        self.logger.debug(f"Generating HTML report at {self.output_path}")

        try:
            # Convert report to dictionary
            report_dict = report.model_dump(mode='json')

            # Convert to JSON string for embedding in HTML
            report_json = json.dumps(report_dict, ensure_ascii=False)

            # Render template
            html_content = self.template.render(report_data=report_json)

            # Write to file
            self.output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(self.output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)

            self.logger.info(f"📄 HTML report saved: {self.output_path}")

        except Exception as e:
            self.logger.error(f"Error generating HTML report: {e}")
            raise

    def cleanup(self):
        """Cleanup resources"""
        pass
