"""Directory loader for eval sets"""

import json
from pathlib import Path
from typing import List
from judge_llm.core.models import EvalSet
from judge_llm.loaders.base import BaseLoader
from judge_llm.utils.logger import get_logger


class DirectoryLoader(BaseLoader):
    """Load eval sets from all JSON files in a directory"""

    def __init__(self, directory_path: str, pattern: str = "*.json"):
        """Initialize directory loader

        Args:
            directory_path: Path to the directory containing eval set files
            pattern: File pattern to match (default: *.json)
        """
        self.directory_path = Path(directory_path).expanduser().resolve()
        self.pattern = pattern
        self.logger = get_logger()
        self._cache = None

    def load(self) -> List[EvalSet]:
        """Load evaluation sets from all matching files in directory

        Returns:
            List of EvalSet objects
        """
        if self._cache is not None:
            self.logger.debug(f"Returning cached eval sets from {self.directory_path}")
            return self._cache

        self.logger.info(f"Loading eval sets from directory {self.directory_path}")

        if not self.directory_path.exists():
            raise FileNotFoundError(f"Directory not found: {self.directory_path}")

        if not self.directory_path.is_dir():
            raise ValueError(f"Path is not a directory: {self.directory_path}")

        eval_sets = []
        files = list(self.directory_path.glob(self.pattern))

        if not files:
            self.logger.warning(
                f"No files matching pattern '{self.pattern}' found in {self.directory_path}"
            )
            return eval_sets

        self.logger.info(f"Found {len(files)} files matching pattern '{self.pattern}'")

        for file_path in files:
            try:
                self.logger.debug(f"Loading eval set from {file_path}")

                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # Parse JSON data into EvalSet model
                eval_set = EvalSet(**data)
                eval_sets.append(eval_set)

                self.logger.info(
                    f"Loaded eval set '{eval_set.name}' with {len(eval_set.eval_cases)} cases from {file_path.name}"
                )

            except json.JSONDecodeError as e:
                self.logger.error(f"Invalid JSON in file {file_path}: {e}")
                continue
            except Exception as e:
                self.logger.error(f"Error loading eval set from {file_path}: {e}")
                continue

        self._cache = eval_sets
        self.logger.info(f"Loaded {len(eval_sets)} eval sets from directory")

        return eval_sets

    def cleanup(self):
        """Cleanup resources"""
        self._cache = None
        self.logger.debug(f"Cleaned up cache for {self.directory_path}")
