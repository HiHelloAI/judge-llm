"""Local file loader for eval sets"""

import json
from pathlib import Path
from typing import List
from judge_llm.core.models import EvalSet
from judge_llm.loaders.base import BaseLoader
from judge_llm.utils.logger import get_logger


class LocalFileLoader(BaseLoader):
    """Load eval sets from local JSON files"""

    def __init__(self, file_path: str):
        """Initialize local file loader

        Args:
            file_path: Path to the JSON eval set file
        """
        self.file_path = Path(file_path).expanduser().resolve()
        self.logger = get_logger()
        self._cache = None

    def load(self) -> List[EvalSet]:
        """Load evaluation sets from file

        Returns:
            List of EvalSet objects
        """
        if self._cache is not None:
            self.logger.debug(f"Returning cached eval set from {self.file_path}")
            return self._cache

        self.logger.info(f"Loading eval set from {self.file_path}")

        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Parse JSON data into EvalSet model
            eval_set = EvalSet(**data)
            self._cache = [eval_set]

            self.logger.info(
                f"Loaded eval set '{eval_set.name}' with {len(eval_set.eval_cases)} cases"
            )

            return self._cache

        except FileNotFoundError:
            self.logger.error(f"Eval set file not found: {self.file_path}")
            raise
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in eval set file: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error loading eval set: {e}")
            raise

    def cleanup(self):
        """Cleanup resources"""
        self._cache = None
        self.logger.debug(f"Cleaned up cache for {self.file_path}")
