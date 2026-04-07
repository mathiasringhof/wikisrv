from __future__ import annotations

import argparse
from pathlib import Path

import uvicorn

from wikisrv.app import WIKI_ROOT_ENV_VAR, create_app, default_wiki_root


def main() -> None:
    parser = argparse.ArgumentParser(description="Serve an Obsidian-style markdown wiki as HTML.")
    parser.add_argument(
        "--wiki-root",
        type=Path,
        default=default_wiki_root(),
        help=f"Path to the wiki root directory. Defaults to ${WIKI_ROOT_ENV_VAR} or the current directory.",
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    uvicorn.run(create_app(args.wiki_root), host=args.host, port=args.port)
