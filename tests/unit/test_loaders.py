"""Unit tests for dataset loaders."""

import json
import tempfile
from pathlib import Path
import pytest

from judge_llm.loaders.local_file_loader import LocalFileLoader
from judge_llm.loaders.directory_loader import DirectoryLoader


class TestLocalFileLoader:
    """Test LocalFileLoader class."""

    def test_loader_creation(self, temp_dir):
        """Test LocalFileLoader instantiation."""
        file_path = temp_dir / "test.json"
        file_path.write_text("{}")

        loader = LocalFileLoader(str(file_path))
        assert loader is not None
        # Resolve both paths to handle symlinks (e.g., /var -> /private/var on macOS)
        assert loader.file_path.resolve() == file_path.resolve()

    def test_load_valid_json_file(self, sample_eval_set_json):
        """Test loading valid JSON evaluation set."""
        loader = LocalFileLoader(str(sample_eval_set_json))

        eval_sets = loader.load()

        assert eval_sets is not None
        assert len(eval_sets) == 1
        assert eval_sets[0].name == "test_set"
        assert len(eval_sets[0].eval_cases) == 2

    def test_load_json_with_cases(self, temp_dir):
        """Test loading JSON with multiple cases."""
        eval_set_data = {
            "eval_set_id": "set123",
            "name": "test_set",
            "description": "Test evaluation set",
            "creation_timestamp": 1234567890.0,
            "eval_cases": [
                {
                    "eval_id": f"case_{i}",
                    "conversation": [],
                    "session_input": {
                        "app_name": "test",
                        "user_id": f"user{i}"
                    },
                    "creation_timestamp": 1234567890.0
                }
                for i in range(5)
            ]
        }

        file_path = temp_dir / "test.json"
        with open(file_path, "w") as f:
            json.dump(eval_set_data, f)

        loader = LocalFileLoader(str(file_path))
        eval_sets = loader.load()

        assert len(eval_sets) == 1
        assert len(eval_sets[0].eval_cases) == 5

    def test_load_file_not_found(self):
        """Test loading from non-existent file."""
        loader = LocalFileLoader("/nonexistent/path/file.json")

        with pytest.raises(FileNotFoundError):
            loader.load()

    def test_load_invalid_json(self, temp_dir):
        """Test loading invalid JSON file."""
        file_path = temp_dir / "invalid.json"
        with open(file_path, "w") as f:
            f.write("{ invalid json content")

        loader = LocalFileLoader(str(file_path))

        with pytest.raises(json.JSONDecodeError):
            loader.load()

    def test_load_json_missing_required_fields(self, temp_dir):
        """Test loading JSON with missing required fields."""
        # Missing 'name' field
        eval_set_data = {
            "eval_set_id": "set123",
            "creation_timestamp": 1234567890.0,
            "eval_cases": []
        }

        file_path = temp_dir / "invalid.json"
        with open(file_path, "w") as f:
            json.dump(eval_set_data, f)

        loader = LocalFileLoader(str(file_path))

        with pytest.raises(Exception):  # Should raise validation error
            loader.load()

    def test_load_with_complex_conversation(self, temp_dir):
        """Test loading eval set with complex conversation history."""
        eval_set_data = {
            "eval_set_id": "set123",
            "name": "complex_test",
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
                            "intermediate_data": {
                                "tool_uses": [],
                                "intermediate_responses": []
                            },
                            "creation_timestamp": 1234567890.0
                        }
                    ]
                }
            ]
        }

        file_path = temp_dir / "complex.json"
        with open(file_path, "w") as f:
            json.dump(eval_set_data, f)

        loader = LocalFileLoader(str(file_path))
        eval_sets = loader.load()

        assert len(eval_sets) == 1
        assert len(eval_sets[0].eval_cases) == 1
        assert len(eval_sets[0].eval_cases[0].conversation) == 1

    def test_load_with_evaluator_config(self, temp_dir):
        """Test loading eval set with per-case evaluator config."""
        eval_set_data = {
            "eval_set_id": "set123",
            "name": "config_test",
            "creation_timestamp": 1234567890.0,
            "eval_cases": [
                {
                    "eval_id": "case1",
                    "session_input": {"app_name": "test", "user_id": "user1"},
                    "creation_timestamp": 1234567890.0,
                    "conversation": [],
                    "evaluator_config": {
                        "response": {
                            "threshold": 0.95
                        }
                    }
                }
            ]
        }

        file_path = temp_dir / "config.json"
        with open(file_path, "w") as f:
            json.dump(eval_set_data, f)

        loader = LocalFileLoader(str(file_path))
        eval_sets = loader.load()

        assert eval_sets[0].eval_cases[0].evaluator_config is not None
        assert eval_sets[0].eval_cases[0].evaluator_config["response"]["threshold"] == 0.95

    def test_load_with_caching(self, temp_dir):
        """Test that loader caches results."""
        eval_set_data = {
            "eval_set_id": "set123",
            "name": "test_set",
            "creation_timestamp": 1234567890.0,
            "eval_cases": []
        }

        file_path = temp_dir / "test.json"
        with open(file_path, "w") as f:
            json.dump(eval_set_data, f)

        loader = LocalFileLoader(str(file_path))

        # Load once
        eval_sets1 = loader.load()

        # Load again - should use cache
        eval_sets2 = loader.load()

        # Should be the same object (cached)
        assert eval_sets1 is eval_sets2


class TestDirectoryLoader:
    """Test DirectoryLoader class."""

    def test_loader_creation(self, temp_dir):
        """Test DirectoryLoader instantiation."""
        loader = DirectoryLoader(str(temp_dir))
        assert loader is not None
        # Resolve both paths to handle symlinks (e.g., /var -> /private/var on macOS)
        assert loader.directory_path.resolve() == temp_dir.resolve()

    def test_load_directory_with_json_files(self, temp_dir):
        """Test loading multiple JSON files from directory."""
        # Create multiple JSON files
        for i in range(3):
            eval_set_data = {
                "eval_set_id": f"set{i}",
                "name": f"test_set_{i}",
                "creation_timestamp": 1234567890.0,
                "eval_cases": [
                    {
                        "eval_id": f"case_{i}",
                        "conversation": [],
                        "session_input": {"app_name": "test", "user_id": f"user{i}"},
                        "creation_timestamp": 1234567890.0
                    }
                ]
            }

            file_path = temp_dir / f"test{i}.json"
            with open(file_path, "w") as f:
                json.dump(eval_set_data, f)

        loader = DirectoryLoader(str(temp_dir))
        eval_sets = loader.load()

        assert len(eval_sets) == 3
        assert all(eval_set.name.startswith("test_set_") for eval_set in eval_sets)

    def test_load_empty_directory(self, temp_dir):
        """Test loading from empty directory."""
        loader = DirectoryLoader(str(temp_dir))
        eval_sets = loader.load()

        assert eval_sets == []

    def test_load_directory_not_found(self):
        """Test loading from non-existent directory."""
        loader = DirectoryLoader("/nonexistent/directory")

        with pytest.raises(FileNotFoundError):
            loader.load()

    def test_load_directory_with_pattern(self, temp_dir):
        """Test loading with file pattern filter."""
        # Create JSON files with different names
        for i in range(3):
            eval_set_data = {
                "eval_set_id": f"set{i}",
                "name": f"test_set_{i}",
                "creation_timestamp": 1234567890.0,
                "eval_cases": []
            }

            file_path = temp_dir / f"eval{i}.json"
            with open(file_path, "w") as f:
                json.dump(eval_set_data, f)

        # Create a file that shouldn't match
        other_path = temp_dir / "other.json"
        other_path.write_text('{"other": "data"}')

        loader = DirectoryLoader(str(temp_dir), pattern="eval*.json")
        eval_sets = loader.load()

        # Should load 3 eval files, not the 'other.json'
        assert len(eval_sets) == 3

    def test_load_directory_mixed_files(self, temp_dir):
        """Test loading directory with JSON and non-JSON files."""
        # Create valid JSON file
        eval_set_data = {
            "eval_set_id": "set1",
            "name": "test_set",
            "creation_timestamp": 1234567890.0,
            "eval_cases": []
        }

        json_path = temp_dir / "valid.json"
        with open(json_path, "w") as f:
            json.dump(eval_set_data, f)

        # Create text file
        txt_path = temp_dir / "readme.txt"
        with open(txt_path, "w") as f:
            f.write("This is not JSON")

        loader = DirectoryLoader(str(temp_dir))
        eval_sets = loader.load()

        # Should load only valid JSON file (pattern is *.json by default)
        assert len(eval_sets) == 1

    def test_load_directory_with_invalid_files(self, temp_dir):
        """Test loading directory with some invalid JSON files."""
        # Create valid JSON
        eval_set_data = {
            "eval_set_id": "set1",
            "name": "test_set",
            "creation_timestamp": 1234567890.0,
            "eval_cases": []
        }

        valid_path = temp_dir / "valid.json"
        with open(valid_path, "w") as f:
            json.dump(eval_set_data, f)

        # Create invalid JSON
        invalid_path = temp_dir / "invalid.json"
        with open(invalid_path, "w") as f:
            f.write("{ invalid json")

        loader = DirectoryLoader(str(temp_dir))
        eval_sets = loader.load()

        # Should load only valid files (invalid files are skipped with warning)
        assert len(eval_sets) == 1

    def test_load_with_caching(self, temp_dir):
        """Test that directory loader caches results."""
        eval_set_data = {
            "eval_set_id": "set1",
            "name": "test_set",
            "creation_timestamp": 1234567890.0,
            "eval_cases": []
        }

        json_path = temp_dir / "valid.json"
        with open(json_path, "w") as f:
            json.dump(eval_set_data, f)

        loader = DirectoryLoader(str(temp_dir))

        # Load once
        eval_sets1 = loader.load()

        # Load again - should use cache
        eval_sets2 = loader.load()

        # Should be the same object (cached)
        assert eval_sets1 is eval_sets2

    def test_cleanup(self, temp_dir):
        """Test cleanup clears cache."""
        eval_set_data = {
            "eval_set_id": "set1",
            "name": "test_set",
            "creation_timestamp": 1234567890.0,
            "eval_cases": []
        }

        json_path = temp_dir / "valid.json"
        with open(json_path, "w") as f:
            json.dump(eval_set_data, f)

        loader = DirectoryLoader(str(temp_dir))

        # Load and cache
        loader.load()
        assert loader._cache is not None

        # Cleanup
        loader.cleanup()
        assert loader._cache is None
