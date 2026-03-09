"""DocsDiscoveryEngine — scan workspace for documentation files.

Pure computation: walks directories, identifies doc files, builds a catalog.
No rendering, no I/O beyond directory listing.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class DocEntry:
    """A discovered documentation file."""

    title: str
    path: Path
    project: str
    category: str  # readme, docs, api, guide
    relative_path: str = ""


@dataclass
class ProjectInfo:
    """A discovered project in the workspace."""

    name: str
    path: Path
    docs: list[DocEntry] = field(default_factory=list)
    has_readme: bool = False
    languages: list[str] = field(default_factory=list)


# File patterns that indicate documentation
DOC_PATTERNS = {
    "readme": ["README.md", "README.rst", "README.txt", "README"],
    "docs": ["docs/", "doc/", "documentation/"],
    "api": [
        "openapi.yaml",
        "openapi.json",
        "swagger.yaml",
        "swagger.json",
        "api.yaml",
        "api.json",
    ],
    "guide": [
        "CONTRIBUTING.md",
        "CHANGELOG.md",
        "CHANGES.md",
        "HISTORY.md",
        "ARCHITECTURE.md",
    ],
}

# File extensions we consider documentation
DOC_EXTENSIONS = {".md", ".rst", ".txt", ".yaml", ".yml", ".json"}

# Directories to skip during scanning
SKIP_DIRS = {
    ".git",
    ".hg",
    ".svn",
    "node_modules",
    "__pycache__",
    ".venv",
    "venv",
    ".tox",
    ".mypy_cache",
    ".pytest_cache",
    "dist",
    "build",
    ".eggs",
    ".next",
    "target",
}

# Language detection by file extension
LANGUAGE_INDICATORS = {
    ".py": "Python",
    ".js": "JavaScript",
    ".ts": "TypeScript",
    ".java": "Java",
    ".go": "Go",
    ".rs": "Rust",
    ".rb": "Ruby",
    ".cs": "C#",
    ".kt": "Kotlin",
    ".swift": "Swift",
    ".cpp": "C++",
    ".c": "C",
}


class DocsDiscoveryEngine:
    """Scan a workspace directory and discover documentation."""

    def discover(self, workspace_root: Path, max_depth: int = 3) -> list[ProjectInfo]:
        """Discover all projects and their documentation.

        Args:
            workspace_root: The workspace base directory to scan.
            max_depth: Maximum directory depth for project discovery.

        Returns:
            List of discovered projects with their documentation.
        """
        if not workspace_root.is_dir():
            return []

        projects: list[ProjectInfo] = []

        # Scan top-level directories as projects
        for entry in sorted(workspace_root.iterdir()):
            if not entry.is_dir() or entry.name.startswith(".") or entry.name in SKIP_DIRS:
                continue

            # Check if this looks like a project (has files, not just subdirs)
            project = self._scan_project(entry, max_depth)
            if project.has_readme or project.docs:
                projects.append(project)
            else:
                # Maybe it's a category dir (like "projects/", "experiments/")
                # Scan one level deeper
                for sub_entry in sorted(entry.iterdir()):
                    if not sub_entry.is_dir() or sub_entry.name.startswith(".") or sub_entry.name in SKIP_DIRS:
                        continue
                    sub_project = self._scan_project(sub_entry, max_depth - 1)
                    if sub_project.has_readme or sub_project.docs:
                        projects.append(sub_project)

        return projects

    def _scan_project(self, project_dir: Path, max_depth: int) -> ProjectInfo:
        """Scan a single project directory for documentation."""
        project = ProjectInfo(name=project_dir.name, path=project_dir)
        languages: set[str] = set()

        # Check for README at project root
        for readme_name in DOC_PATTERNS["readme"]:
            readme_path = project_dir / readme_name
            if readme_path.is_file():
                project.has_readme = True
                title = self._extract_title(readme_path, readme_name)
                project.docs.append(
                    DocEntry(
                        title=title,
                        path=readme_path,
                        project=project_dir.name,
                        category="readme",
                        relative_path=readme_name,
                    )
                )
                break

        # Check for guide files at project root
        for guide_name in DOC_PATTERNS["guide"]:
            guide_path = project_dir / guide_name
            if guide_path.is_file():
                title = self._extract_title(guide_path, guide_name)
                project.docs.append(
                    DocEntry(
                        title=title,
                        path=guide_path,
                        project=project_dir.name,
                        category="guide",
                        relative_path=guide_name,
                    )
                )

        # Check for API spec files at project root
        for api_name in DOC_PATTERNS["api"]:
            api_path = project_dir / api_name
            if api_path.is_file():
                project.docs.append(
                    DocEntry(
                        title=f"API Specification ({api_name})",
                        path=api_path,
                        project=project_dir.name,
                        category="api",
                        relative_path=api_name,
                    )
                )

        # Scan docs directories
        for docs_dir_name in DOC_PATTERNS["docs"]:
            docs_dir = project_dir / docs_dir_name.rstrip("/")
            if docs_dir.is_dir():
                self._scan_docs_dir(docs_dir, project, max_depth)

        # Detect languages (shallow scan)
        self._detect_languages(project_dir, languages)
        project.languages = sorted(languages)

        return project

    def _scan_docs_dir(self, docs_dir: Path, project: ProjectInfo, max_depth: int) -> None:
        """Recursively scan a docs directory for documentation files."""
        if max_depth <= 0:
            return

        try:
            entries = sorted(docs_dir.iterdir())
        except PermissionError:
            return

        for entry in entries:
            if entry.name.startswith(".") or entry.name in SKIP_DIRS:
                continue

            if entry.is_file() and entry.suffix.lower() in DOC_EXTENSIONS:
                relative = str(entry.relative_to(project.path))
                title = self._extract_title(entry, entry.stem)
                project.docs.append(
                    DocEntry(
                        title=title,
                        path=entry,
                        project=project.name,
                        category="docs",
                        relative_path=relative,
                    )
                )
            elif entry.is_dir() and entry.name not in SKIP_DIRS:
                self._scan_docs_dir(entry, project, max_depth - 1)

    def _detect_languages(self, project_dir: Path, languages: set[str]) -> None:
        """Detect programming languages used in a project (shallow scan)."""
        try:
            for entry in project_dir.iterdir():
                if entry.is_file():
                    lang = LANGUAGE_INDICATORS.get(entry.suffix.lower())
                    if lang:
                        languages.add(lang)
                elif entry.is_dir() and entry.name == "src":
                    # Scan one level into src/
                    for src_entry in entry.iterdir():
                        if src_entry.is_file():
                            lang = LANGUAGE_INDICATORS.get(src_entry.suffix.lower())
                            if lang:
                                languages.add(lang)
        except PermissionError:
            pass

    @staticmethod
    def _extract_title(filepath: Path, fallback: str) -> str:
        """Extract a title from a markdown file's first heading."""
        if filepath.suffix.lower() not in (".md", ".rst"):
            return fallback.replace("-", " ").replace("_", " ").title()

        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("# "):
                        return line[2:].strip()
                    if line.startswith("==") and len(line) >= 3:
                        # RST-style underline title — previous line was title
                        break
        except (OSError, UnicodeDecodeError):
            pass

        return fallback.replace("-", " ").replace("_", " ").title()


def discover_workspace(workspace_root: str | Path) -> list[ProjectInfo]:
    """Convenience function to discover docs in a workspace."""
    engine = DocsDiscoveryEngine()
    return engine.discover(Path(workspace_root))
