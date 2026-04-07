# wikisrv

Serve an Obsidian-style Markdown knowledge base as HTML.

## Features

- renders `*.md` pages as `*.html`
- rewrites Obsidian `[[links]]` into HTML links
- serves linked assets such as PDFs directly from the wiki tree

## Requirements

- Python 3.12+
- `uv`

## Install

```bash
uv sync --dev
```

## Run

```bash
uv run wikisrv --wiki-root /path/to/wiki
```

If `--wiki-root` is omitted, `wikisrv` uses `$WIKISRV_WIKI_ROOT` when set, otherwise the current working directory.

## Tooling

```bash
just analyze
just test
just release-check
```

`just release-check` runs the static checks, test suite, and package build used for release prep.

## Security Model

`wikisrv` is intentionally a thin server over a local wiki tree.

- It serves arbitrary files under the configured wiki root, not just rendered pages or selected asset types.
- Markdown is rendered with raw HTML enabled, so embedded HTML is passed through to the output.

Only point `wikisrv` at content you intend to expose as-is. It is not designed to sanitize untrusted content or enforce a publish-time privacy boundary.

## Sample Data

The fixture under `tests/fixtures/sample_wiki/` is synthetic. It is only intended to exercise routing, frontmatter handling, cross-links, and linked binary assets.
