"""Command-line interface for embeddoor."""

import argparse
import webbrowser
from threading import Timer

from embeddoor.app import create_app


def open_browser(url):
    """Open the browser after a short delay."""
    webbrowser.open(url)


def main():
    """Main entry point for the embeddoor CLI."""
    parser = argparse.ArgumentParser(
        description="Embeddoor - Embedding Visualization and Analysis Tool"
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host to bind to (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=5000,
        help="Port to bind to (default: 5000)",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode",
    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Don't open browser automatically",
    )

    args = parser.parse_args()

    app = create_app()

    url = f"http://{args.host}:{args.port}"
    print(f"Starting Embeddoor on {url}")
    print("Press CTRL+C to quit")

    # Open browser after a short delay
    if not args.no_browser:
        Timer(1.5, open_browser, args=[url]).start()

    app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    main()
