#!/usr/bin/env python3
"""
Main entry point for LlamaVerifier
"""
import sys
from typing import List, Optional

from .cli.commands import app


def main(args: Optional[List[str]] = None) -> None:
    """
    Main entry point for the LlamaVerifier CLI

    Args:
        args: Command-line arguments (defaults to sys.argv[1:])
    """
    try:
        if args is None:
            app()
        else:
            app(args)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
