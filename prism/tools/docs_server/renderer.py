"""DocsRenderer — convert documentation files to HTML.

Renders markdown to HTML with syntax highlighting and clean styling.
Falls back gracefully when optional dependencies are missing.
"""

from __future__ import annotations

import html
import re
from pathlib import Path


def render_markdown(text: str) -> str:
    """Render markdown text to HTML.

    Uses the 'markdown' library if available, otherwise falls back
    to a minimal regex-based renderer for basic formatting.
    """
    try:
        import markdown

        return markdown.markdown(
            text,
            extensions=["fenced_code", "tables", "toc", "codehilite"],
            extension_configs={"codehilite": {"guess_lang": False}},
        )
    except ImportError:
        return _fallback_render(text)


def render_file(filepath: Path) -> str:
    """Read and render a documentation file to HTML."""
    try:
        content = filepath.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return "<p>Error reading file.</p>"

    suffix = filepath.suffix.lower()
    if suffix in (".md",):
        return render_markdown(content)
    elif suffix in (".yaml", ".yml", ".json"):
        return f"<pre><code>{html.escape(content)}</code></pre>"
    elif suffix in (".rst",):
        # Basic RST: just escape and preserve structure
        return f"<pre>{html.escape(content)}</pre>"
    else:
        return f"<pre>{html.escape(content)}</pre>"


def _fallback_render(text: str) -> str:
    """Minimal markdown renderer for when the markdown library is not installed."""
    lines = text.split("\n")
    result: list[str] = []
    in_code_block = False
    in_list = False

    for line in lines:
        # Fenced code blocks
        if line.strip().startswith("```"):
            if in_code_block:
                result.append("</code></pre>")
                in_code_block = False
            else:
                result.append("<pre><code>")
                in_code_block = True
            continue

        if in_code_block:
            result.append(html.escape(line))
            continue

        stripped = line.strip()

        # Headings
        if stripped.startswith("######"):
            result.append(f"<h6>{html.escape(stripped[6:].strip())}</h6>")
        elif stripped.startswith("#####"):
            result.append(f"<h5>{html.escape(stripped[5:].strip())}</h5>")
        elif stripped.startswith("####"):
            result.append(f"<h4>{html.escape(stripped[4:].strip())}</h4>")
        elif stripped.startswith("###"):
            result.append(f"<h3>{html.escape(stripped[3:].strip())}</h3>")
        elif stripped.startswith("##"):
            result.append(f"<h2>{html.escape(stripped[2:].strip())}</h2>")
        elif stripped.startswith("#"):
            result.append(f"<h1>{html.escape(stripped[1:].strip())}</h1>")
        # Unordered list items
        elif stripped.startswith("- ") or stripped.startswith("* "):
            if not in_list:
                result.append("<ul>")
                in_list = True
            result.append(f"<li>{_inline_format(stripped[2:])}</li>")
        # Horizontal rule
        elif stripped in ("---", "***", "___"):
            if in_list:
                result.append("</ul>")
                in_list = False
            result.append("<hr>")
        # Empty line
        elif not stripped:
            if in_list:
                result.append("</ul>")
                in_list = False
            result.append("")
        # Paragraph
        else:
            if in_list:
                result.append("</ul>")
                in_list = False
            result.append(f"<p>{_inline_format(stripped)}</p>")

    if in_list:
        result.append("</ul>")
    if in_code_block:
        result.append("</code></pre>")

    return "\n".join(result)


def _inline_format(text: str) -> str:
    """Apply inline markdown formatting (bold, italic, code, links)."""
    escaped = html.escape(text)
    # Bold
    escaped = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", escaped)
    # Italic
    escaped = re.sub(r"\*(.+?)\*", r"<em>\1</em>", escaped)
    # Inline code
    escaped = re.sub(r"`(.+?)`", r"<code>\1</code>", escaped)
    # Links
    escaped = re.sub(r"\[(.+?)\]\((.+?)\)", r'<a href="\2">\1</a>', escaped)
    return escaped
