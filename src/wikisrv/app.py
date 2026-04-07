from __future__ import annotations

import os
from collections.abc import Awaitable, Callable
from html import escape
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse

from wikisrv.markdown import render_markdown

WIKI_ROOT_ENV_VAR = "WIKISRV_WIKI_ROOT"


def create_app(wiki_root: Path | None = None) -> FastAPI:
    resolved_root = (wiki_root or default_wiki_root()).resolve()
    app = FastAPI(title="wikisrv")
    app.add_api_route("/", redirect_to_index, include_in_schema=False)
    app.add_api_route(
        "/{page_path:path}.html",
        create_page_endpoint(resolved_root),
        response_class=HTMLResponse,
    )
    app.add_api_route(
        "/{asset_path:path}",
        create_asset_endpoint(resolved_root),
        response_class=FileResponse,
        include_in_schema=False,
    )

    return app


def default_wiki_root() -> Path:
    configured_root = os.environ.get(WIKI_ROOT_ENV_VAR)
    if configured_root:
        return Path(configured_root).expanduser().resolve()

    return Path.cwd().resolve()


async def redirect_to_index() -> RedirectResponse:
    return RedirectResponse(url="/index.html")


def create_page_endpoint(wiki_root: Path) -> Callable[[str], Awaitable[HTMLResponse]]:
    async def endpoint(page_path: str) -> HTMLResponse:
        markdown_path = resolve_wiki_path(wiki_root, page_path, suffix=".md")
        if not markdown_path.is_file():
            raise HTTPException(status_code=404, detail="Page not found")

        content = markdown_path.read_text(encoding="utf-8")
        html = render_markdown(content)
        title = page_title(page_path)
        document = render_document(title=title, body=html)
        return HTMLResponse(content=document)

    return endpoint


def create_asset_endpoint(wiki_root: Path) -> Callable[[str], Awaitable[FileResponse]]:
    async def endpoint(asset_path: str) -> FileResponse:
        asset_file = resolve_wiki_path(wiki_root, asset_path)
        if not asset_file.is_file():
            raise HTTPException(status_code=404, detail="Page not found")

        return FileResponse(asset_file)

    return endpoint


def resolve_markdown_path(wiki_root: Path, page_path: str) -> Path:
    return resolve_wiki_path(wiki_root, page_path, suffix=".md")


def resolve_wiki_path(wiki_root: Path, relative_path: str, *, suffix: str | None = None) -> Path:
    candidate = wiki_root / Path(relative_path)
    if suffix is not None:
        candidate = candidate.with_suffix(suffix)
    candidate = candidate.resolve()
    try:
        candidate.relative_to(wiki_root)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail="Page not found") from exc
    return candidate


def render_document(*, title: str, body: str) -> str:
    escaped_title = escape(title)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escaped_title}</title>
  <style>
    :root {{
      color-scheme: light;
      font-family: ui-sans-serif, system-ui, sans-serif;
      line-height: 1.5;
    }}
    body {{
      margin: 0;
      background: #f5f2ea;
      color: #1f2937;
    }}
    main {{
      box-sizing: border-box;
      max-width: 56rem;
      margin: 0 auto;
      padding: 3rem 1.5rem 4rem;
    }}
    article {{
      background: #fffdf8;
      border: 1px solid #d6d3d1;
      border-radius: 1rem;
      padding: 2rem;
      box-shadow: 0 1.5rem 3rem -2rem rgba(31, 41, 55, 0.35);
    }}
    a {{
      color: #9a3412;
    }}
    code {{
      background: #f3f0eb;
      border-radius: 0.25rem;
      padding: 0.1rem 0.3rem;
    }}
  </style>
</head>
<body>
  <main>
    <article>
      {body}
    </article>
  </main>
</body>
</html>
"""


def page_title(page_path: str) -> str:
    return Path(page_path).name or "index"
