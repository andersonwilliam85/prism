"""prism ui — launch the web-based installer UI."""

from __future__ import annotations

import sys
import threading
import webbrowser
from argparse import Namespace, _SubParsersAction


def register(subparsers: _SubParsersAction) -> None:
    """Register the ``ui`` subcommand."""
    p = subparsers.add_parser(
        "ui",
        help="Launch the web-based installer UI",
        description="Start a local web server for interactive prism installation.",
    )
    p.add_argument("--port", type=int, default=5555, help="Port to serve on (default: 5555)")
    p.add_argument("--host", default="localhost", help="Host to bind to (default: localhost)")
    p.add_argument("--no-browser", action="store_true", help="Don't auto-open the browser")
    p.set_defaults(func=_run)


def _run(args: Namespace) -> None:
    """Launch the Flask web UI."""
    try:
        from prism.ui.app import create_app
    except ImportError:
        print("Error: Flask is required for the web UI.")
        print("Install it with: pip install prism-dx[ui]")
        sys.exit(1)

    app = create_app()
    url = f"http://{args.host}:{args.port}"

    if not args.no_browser:

        def _open_browser() -> None:
            import time

            time.sleep(1.5)
            webbrowser.open(url)

        threading.Thread(target=_open_browser, daemon=True).start()

    print(f"\n  Prism UI running at {url}\n")
    app.run(host=args.host, port=args.port, debug=False)
