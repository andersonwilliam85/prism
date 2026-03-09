"""ConfigFileAccessor — YAML read/write (centralized).

Pure I/O translation: reads and writes YAML files via PyYAML.
No business logic, no merging, no validation.
"""

from __future__ import annotations

from pathlib import Path

import yaml


class ConfigFileAccessor:
    """Concrete implementation of IConfigFileAccessor."""

    def read_yaml(self, path: Path) -> dict:
        """Read a YAML file and return its contents as a dict.

        Args:
            path: Path to the YAML file.

        Returns:
            Parsed YAML content as a dictionary.

        Raises:
            FileNotFoundError: If the file does not exist.
            yaml.YAMLError: If the file contains invalid YAML.
        """
        if not path.exists():
            raise FileNotFoundError(f"YAML file not found: {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return data if isinstance(data, dict) else {}

    def write_yaml(self, path: Path, data: dict) -> None:
        """Write a dictionary to a YAML file.

        Args:
            path: Destination file path.
            data: Dictionary to serialize.

        Raises:
            OSError: If the file cannot be written.
        """
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
