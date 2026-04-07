from __future__ import annotations

import re
from pathlib import PurePosixPath
from urllib.parse import quote

from markdown_it import MarkdownIt

OBSIDIAN_LINK_RE = re.compile(r"\[\[([^\]|#]+)(?:#([^\]|]+))?(?:\|([^\]]+))?\]\]")

MARKDOWN = MarkdownIt("commonmark", {"html": True, "linkify": True})


def strip_frontmatter(markdown_text: str) -> str:
    if not markdown_text.startswith("---\n"):
        return markdown_text

    _, _, remainder = markdown_text.partition("\n---\n")
    return remainder or markdown_text


def rewrite_obsidian_links(markdown_text: str) -> str:
    def replacement(match: re.Match[str]) -> str:
        raw_target = match.group(1).strip()
        raw_heading = match.group(2)
        raw_label = match.group(3)

        target_path = PurePosixPath(raw_target)
        encoded_path = quote(target_path.as_posix())
        href = f"/{encoded_path}.html"

        if raw_heading is not None:
            href = f"{href}#{slugify(raw_heading)}"

        label = raw_label or raw_target
        return f"[{label}]({href})"

    return OBSIDIAN_LINK_RE.sub(replacement, markdown_text)


def render_markdown(markdown_text: str) -> str:
    without_frontmatter = strip_frontmatter(markdown_text)
    rewritten_links = rewrite_obsidian_links(without_frontmatter)
    return MARKDOWN.render(rewritten_links)


def slugify(text: str) -> str:
    normalized = re.sub(r"[^\w\s-]", "", text.lower())
    collapsed = re.sub(r"[-\s]+", "-", normalized).strip("-")
    return collapsed
