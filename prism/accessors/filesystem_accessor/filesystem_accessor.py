"""FilesystemAccessor — mkdir, copy, rmtree, exists, write, read.

Pure I/O translation over pathlib and shutil. No business logic.
"""

from __future__ import annotations

import shutil
from pathlib import Path


class FilesystemAccessor:
    """Concrete implementation of IFilesystemAccessor."""

    def mkdir(self, path: Path, parents: bool = True) -> None:
        """Create a directory, optionally including parents.

        Args:
            path: Directory path to create.
            parents: If True, create parent directories as needed.

        Raises:
            OSError: If the directory cannot be created.
        """
        path.mkdir(parents=parents, exist_ok=True)

    def copy(self, src: Path, dst: Path) -> None:
        """Copy a file or directory tree from src to dst.

        If src is a directory, copies the entire tree.
        If src is a file, copies the single file.

        Args:
            src: Source path (file or directory).
            dst: Destination path.

        Raises:
            FileNotFoundError: If src does not exist.
            OSError: If the copy operation fails.
        """
        if not src.exists():
            raise FileNotFoundError(f"Source not found: {src}")
        if src.is_dir():
            shutil.copytree(src, dst)
        else:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)

    def rmtree(self, path: Path) -> None:
        """Remove a directory tree.

        Args:
            path: Directory to remove.

        Raises:
            FileNotFoundError: If the path does not exist.
            OSError: If the removal fails.
        """
        if not path.exists():
            raise FileNotFoundError(f"Path not found: {path}")
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()

    def exists(self, path: Path) -> bool:
        """Check whether a path exists.

        Args:
            path: Path to check.

        Returns:
            True if the path exists, False otherwise.
        """
        return path.exists()

    def write_text(self, path: Path, content: str) -> None:
        """Write text content to a file, creating parent dirs as needed.

        Args:
            path: File path.
            content: String content to write.

        Raises:
            OSError: If the file cannot be written.
        """
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def read_text(self, path: Path) -> str:
        """Read text content from a file.

        Args:
            path: File path.

        Returns:
            File content as a string.

        Raises:
            FileNotFoundError: If the file does not exist.
        """
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        return path.read_text(encoding="utf-8")
