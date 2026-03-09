"""Docs Server — local documentation portal for workspace projects.

Scans the workspace, discovers READMEs and docs, renders them as HTML,
and serves a brandable welcome page. Configurable via prism_config.branding.

Usage:
    python -m prism.tools.docs_server.server [--workspace ~/workspace] [--port 5556]
"""

from __future__ import annotations

import argparse
import html
import sys
from pathlib import Path

from flask import Flask, abort, request

from prism.tools.docs_server.discovery import DocsDiscoveryEngine, ProjectInfo
from prism.tools.docs_server.renderer import render_file


def create_docs_app(
    workspace_root: Path,
    branding: dict | None = None,
) -> Flask:
    """Create the docs server Flask app.

    Args:
        workspace_root: Path to the workspace to scan for docs.
        branding: Optional branding config dict with keys like
            logo_text, tagline, primary_color, links.
    """
    app = Flask(__name__)
    branding = branding or {}

    engine = DocsDiscoveryEngine()

    @app.route("/")
    def index():
        projects = engine.discover(workspace_root)
        return _render_welcome(projects, branding, workspace_root)

    @app.route("/project/<project_name>")
    def project_page(project_name: str):
        projects = engine.discover(workspace_root)
        project = next((p for p in projects if p.name == project_name), None)
        if not project:
            abort(404)
        return _render_project(project, branding)

    @app.route("/doc/<project_name>/<path:doc_path>")
    def doc_page(project_name: str, doc_path: str):
        projects = engine.discover(workspace_root)
        project = next((p for p in projects if p.name == project_name), None)
        if not project:
            abort(404)
        doc = next((d for d in project.docs if d.relative_path == doc_path), None)
        if not doc:
            abort(404)
        rendered = render_file(doc.path)
        return _render_doc_page(doc.title, rendered, project_name, branding)

    @app.route("/search")
    def search():
        query = request.args.get("q", "").strip()
        if not query:
            return _render_search_results(query, [], branding)
        projects = engine.discover(workspace_root)
        results = _search_docs(projects, query)
        return _render_search_results(query, results, branding)

    @app.route("/api/projects")
    def api_projects():
        projects = engine.discover(workspace_root)
        return [
            {
                "name": p.name,
                "path": str(p.path),
                "has_readme": p.has_readme,
                "languages": p.languages,
                "doc_count": len(p.docs),
            }
            for p in projects
        ]

    return app


# ------------------------------------------------------------------
# Search
# ------------------------------------------------------------------


def _search_docs(projects: list[ProjectInfo], query: str) -> list[dict]:
    """Search documentation content for a query string."""
    results = []
    query_lower = query.lower()
    for project in projects:
        for doc in project.docs:
            try:
                content = doc.path.read_text(encoding="utf-8", errors="ignore")
                if query_lower in content.lower():
                    # Find context around match
                    idx = content.lower().index(query_lower)
                    start = max(0, idx - 80)
                    end = min(len(content), idx + len(query) + 80)
                    snippet = content[start:end].strip()
                    results.append(
                        {
                            "title": doc.title,
                            "project": doc.project,
                            "path": doc.relative_path,
                            "snippet": snippet,
                        }
                    )
            except OSError:
                continue
    return results


# ------------------------------------------------------------------
# HTML rendering
# ------------------------------------------------------------------


def _brand_css(branding: dict) -> str:
    """Generate CSS custom properties from branding config."""
    primary = branding.get("primary_color", "#7c3aed")
    return f"""
    :root {{
        --primary: {primary};
        --primary-light: {primary}22;
        --bg: #ffffff;
        --surface: #f8f9fa;
        --text: #1a1a2e;
        --text-muted: #6c757d;
        --border: #e9ecef;
    }}
    """


def _nav_html(branding: dict) -> str:
    """Generate navigation bar HTML."""
    logo_text = html.escape(branding.get("logo_text", "Docs"))
    tagline = html.escape(branding.get("tagline", ""))
    links_html = ""
    for link in branding.get("links", []):
        label = html.escape(link.get("label", ""))
        url = html.escape(link.get("url", "#"))
        links_html += f'<a href="{url}" class="nav-link">{label}</a>'

    return f"""
    <nav class="navbar">
        <div class="nav-brand">
            <a href="/">{logo_text}</a>
            {f'<span class="tagline">{tagline}</span>' if tagline else ''}
        </div>
        <div class="nav-links">
            <form action="/search" method="get" class="search-form">
                <input type="text" name="q" placeholder="Search docs..." class="search-input">
            </form>
            {links_html}
        </div>
    </nav>
    """


def _page_shell(title: str, body: str, branding: dict) -> str:
    """Wrap content in a full HTML page."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html.escape(title)}</title>
    <style>
    {_brand_css(branding)}
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
           color: var(--text); background: var(--bg); line-height: 1.6; }}
    .navbar {{ display: flex; align-items: center; justify-content: space-between;
              padding: 0.75rem 2rem; background: var(--surface); border-bottom: 1px solid var(--border); }}
    .nav-brand a {{ font-size: 1.25rem; font-weight: 700; color: var(--primary);
                   text-decoration: none; }}
    .tagline {{ font-size: 0.8rem; color: var(--text-muted); margin-left: 1rem; }}
    .nav-links {{ display: flex; align-items: center; gap: 1rem; }}
    .nav-link {{ color: var(--text-muted); text-decoration: none; font-size: 0.9rem; }}
    .nav-link:hover {{ color: var(--primary); }}
    .search-form {{ display: inline; }}
    .search-input {{ padding: 0.4rem 0.8rem; border: 1px solid var(--border);
                    border-radius: 4px; font-size: 0.85rem; width: 200px; }}
    .container {{ max-width: 1100px; margin: 0 auto; padding: 2rem; }}
    .hero {{ text-align: center; padding: 3rem 0 2rem; }}
    .hero h1 {{ font-size: 2rem; color: var(--primary); margin-bottom: 0.5rem; }}
    .hero p {{ color: var(--text-muted); font-size: 1.1rem; }}
    .projects-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
                     gap: 1.5rem; margin-top: 2rem; }}
    .project-card {{ background: var(--surface); border: 1px solid var(--border);
                    border-radius: 8px; padding: 1.5rem; transition: box-shadow 0.2s; }}
    .project-card:hover {{ box-shadow: 0 2px 12px rgba(0,0,0,0.08); }}
    .project-card h3 {{ margin-bottom: 0.5rem; }}
    .project-card h3 a {{ color: var(--text); text-decoration: none; }}
    .project-card h3 a:hover {{ color: var(--primary); }}
    .badge {{ display: inline-block; padding: 0.15rem 0.5rem; font-size: 0.75rem;
             border-radius: 3px; background: var(--primary-light); color: var(--primary);
             margin-right: 0.4rem; }}
    .doc-count {{ color: var(--text-muted); font-size: 0.85rem; }}
    .doc-list {{ list-style: none; margin-top: 1rem; }}
    .doc-list li {{ padding: 0.4rem 0; border-bottom: 1px solid var(--border); }}
    .doc-list a {{ color: var(--primary); text-decoration: none; }}
    .doc-list a:hover {{ text-decoration: underline; }}
    .breadcrumb {{ margin-bottom: 1.5rem; color: var(--text-muted); font-size: 0.9rem; }}
    .breadcrumb a {{ color: var(--primary); text-decoration: none; }}
    .doc-content {{ line-height: 1.8; }}
    .doc-content h1, .doc-content h2, .doc-content h3 {{ margin-top: 1.5rem; margin-bottom: 0.5rem; }}
    .doc-content pre {{ background: var(--surface); padding: 1rem; border-radius: 6px;
                       overflow-x: auto; border: 1px solid var(--border); margin: 1rem 0; }}
    .doc-content code {{ font-family: 'SF Mono', Menlo, monospace; font-size: 0.9em; }}
    .doc-content p {{ margin-bottom: 0.75rem; }}
    .doc-content ul, .doc-content ol {{ margin: 0.5rem 0 0.5rem 1.5rem; }}
    .doc-content table {{ border-collapse: collapse; width: 100%; margin: 1rem 0; }}
    .doc-content th, .doc-content td {{ border: 1px solid var(--border); padding: 0.5rem 0.75rem;
                                       text-align: left; }}
    .doc-content th {{ background: var(--surface); }}
    .search-results {{ margin-top: 1rem; }}
    .search-result {{ padding: 1rem; border-bottom: 1px solid var(--border); }}
    .search-result h3 a {{ color: var(--primary); text-decoration: none; }}
    .snippet {{ color: var(--text-muted); font-size: 0.9rem; margin-top: 0.25rem; }}
    .empty-state {{ text-align: center; padding: 3rem; color: var(--text-muted); }}
    </style>
</head>
<body>
    {_nav_html(branding)}
    <div class="container">
        {body}
    </div>
</body>
</html>"""


def _render_welcome(projects: list[ProjectInfo], branding: dict, workspace_root: Path) -> str:
    """Render the welcome page with project cards."""
    logo_text = html.escape(branding.get("logo_text", "Documentation Portal"))
    tagline = html.escape(branding.get("tagline", f"Your workspace at {workspace_root}"))

    hero = f"""
    <div class="hero">
        <h1>{logo_text}</h1>
        <p>{tagline}</p>
    </div>
    """

    if not projects:
        body = hero + '<div class="empty-state"><p>No projects with documentation found in your workspace.</p></div>'
        return _page_shell(logo_text, body, branding)

    cards = ""
    for project in projects:
        langs = "".join(f'<span class="badge">{html.escape(lang)}</span>' for lang in project.languages)
        doc_count = len(project.docs)
        cards += f"""
        <div class="project-card">
            <h3><a href="/project/{html.escape(project.name)}">{html.escape(project.name)}</a></h3>
            <div>{langs}</div>
            <div class="doc-count">{doc_count} doc{'s' if doc_count != 1 else ''}</div>
        </div>
        """

    body = hero + f'<div class="projects-grid">{cards}</div>'
    return _page_shell(f"{logo_text} — Home", body, branding)


def _render_project(project: ProjectInfo, branding: dict) -> str:
    """Render a project's documentation listing."""
    breadcrumb = f'<div class="breadcrumb"><a href="/">Home</a> / {html.escape(project.name)}</div>'

    langs = "".join(f'<span class="badge">{html.escape(lang)}</span>' for lang in project.languages)
    header = f"<h1>{html.escape(project.name)}</h1><div>{langs}</div>"

    # Render README inline if present
    readme_html = ""
    readme_doc = next((d for d in project.docs if d.category == "readme"), None)
    if readme_doc:
        readme_html = f'<div class="doc-content">{render_file(readme_doc.path)}</div><hr>'

    # List other docs
    other_docs = [d for d in project.docs if d.category != "readme"]
    docs_list = ""
    if other_docs:
        items = ""
        for doc in other_docs:
            cat_badge = f'<span class="badge">{html.escape(doc.category)}</span>'
            link = f"/doc/{html.escape(project.name)}/{html.escape(doc.relative_path)}"
            items += f'<li>{cat_badge} <a href="{link}">{html.escape(doc.title)}</a></li>'
        docs_list = f'<h2>Documentation</h2><ul class="doc-list">{items}</ul>'

    body = f"{breadcrumb}{header}{readme_html}{docs_list}"
    return _page_shell(f"{project.name} — Docs", body, branding)


def _render_doc_page(title: str, rendered_content: str, project_name: str, branding: dict) -> str:
    """Render a single documentation page."""
    breadcrumb = (
        f'<div class="breadcrumb">'
        f'<a href="/">Home</a> / '
        f'<a href="/project/{html.escape(project_name)}">{html.escape(project_name)}</a> / '
        f"{html.escape(title)}</div>"
    )
    body = f'{breadcrumb}<div class="doc-content">{rendered_content}</div>'
    return _page_shell(f"{title} — {project_name}", body, branding)


def _render_search_results(query: str, results: list[dict], branding: dict) -> str:
    """Render search results page."""
    if not query:
        body = '<div class="empty-state"><p>Enter a search term to find documentation.</p></div>'
        return _page_shell("Search", body, branding)

    if not results:
        body = f'<h2>Search: {html.escape(query)}</h2><div class="empty-state"><p>No results found.</p></div>'
        return _page_shell(f"Search: {query}", body, branding)

    items = ""
    for r in results:
        link = f"/doc/{html.escape(r['project'])}/{html.escape(r['path'])}"
        items += f"""
        <div class="search-result">
            <h3><a href="{link}">{html.escape(r['title'])}</a></h3>
            <span class="badge">{html.escape(r['project'])}</span>
            <div class="snippet">{html.escape(r['snippet'])}</div>
        </div>
        """

    body = f'<h2>Search: {html.escape(query)}</h2><div class="search-results">{items}</div>'
    return _page_shell(f"Search: {query}", body, branding)


# ------------------------------------------------------------------
# CLI entry point
# ------------------------------------------------------------------


def main():
    """Run the docs server from the command line."""
    parser = argparse.ArgumentParser(description="Prism Documentation Server")
    parser.add_argument(
        "--workspace",
        "-w",
        default=str(Path.home() / "workspace"),
        help="Workspace directory to scan",
    )
    parser.add_argument("--port", "-p", type=int, default=5556, help="Port to serve on")
    parser.add_argument("--host", default="localhost", help="Host to bind to")
    parser.add_argument("--logo", default="", help="Logo text for branding")
    parser.add_argument("--tagline", default="", help="Tagline for branding")
    parser.add_argument("--color", default="#7c3aed", help="Primary brand color")
    args = parser.parse_args()

    workspace = Path(args.workspace).expanduser()
    if not workspace.is_dir():
        print(f"Error: workspace directory not found: {workspace}")
        sys.exit(1)

    branding = {}
    if args.logo:
        branding["logo_text"] = args.logo
    if args.tagline:
        branding["tagline"] = args.tagline
    if args.color != "#7c3aed":
        branding["primary_color"] = args.color

    app = create_docs_app(workspace, branding)

    print("Prism Docs Server")
    print(f"  Workspace: {workspace}")
    print(f"  URL: http://{args.host}:{args.port}")
    print()

    app.run(host=args.host, port=args.port, debug=False)


if __name__ == "__main__":
    main()
