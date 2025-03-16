#!/usr/bin/env python3
"""Entry point for mcp-mac-info."""

import sys


def main():
    """Run the main application."""
    # Import functionality here to avoid exposing it at package level
    from .server import start_server

    # You can add argument parsing here if needed
    return start_server()


if __name__ == "__main__":
    sys.exit(main())
