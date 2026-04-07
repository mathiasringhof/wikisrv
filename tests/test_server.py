from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from wikisrv.app import create_app, default_wiki_root


def write_page(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_default_wiki_root_uses_current_directory(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("WIKISRV_WIKI_ROOT", raising=False)

    assert default_wiki_root() == tmp_path.resolve()


def test_index_html_serves_index_markdown_and_rewrites_obsidian_links(tmp_path: Path) -> None:
    write_page(
        tmp_path / "index.md",
        """# Index

- [[overview]]
- [[pages/topics/service-architecture]]
""",
    )
    write_page(tmp_path / "overview.md", "# Overview\n")
    write_page(
        tmp_path / "pages/topics/service-architecture.md",
        "# Service architecture\n",
    )

    client = TestClient(create_app(tmp_path))

    response = client.get("/index.html")

    assert response.status_code == 200
    assert "<h1>Index</h1>" in response.text
    assert 'href="/overview.html"' in response.text
    assert ">overview</a>" in response.text
    assert 'href="/pages/topics/service-architecture.html"' in response.text
    assert ">pages/topics/service-architecture</a>" in response.text


def test_obsidian_link_alias_still_overrides_default_path_label(tmp_path: Path) -> None:
    write_page(
        tmp_path / "index.md",
        """# Index

- [[pages/topics/service-architecture|Service Architecture]]
""",
    )
    write_page(tmp_path / "pages/topics/service-architecture.md", "# Service architecture\n")

    client = TestClient(create_app(tmp_path))

    response = client.get("/index.html")

    assert response.status_code == 200
    assert 'href="/pages/topics/service-architecture.html"' in response.text
    assert ">Service Architecture</a>" in response.text


def test_nested_markdown_page_is_served_as_html_and_strips_frontmatter(tmp_path: Path) -> None:
    write_page(
        tmp_path / "pages/topics/service-architecture.md",
        """---
title: "Service architecture"
type: topic
---

# Current synthesis

See [[overview]].
""",
    )
    write_page(tmp_path / "overview.md", "# Overview\n")

    client = TestClient(create_app(tmp_path))

    response = client.get("/pages/topics/service-architecture.html")

    assert response.status_code == 200
    assert "<h1>Current synthesis</h1>" in response.text
    assert 'href="/overview.html"' in response.text
    assert "title: " not in response.text


def test_missing_markdown_page_returns_404(tmp_path: Path) -> None:
    write_page(tmp_path / "index.md", "# Index\n")

    client = TestClient(create_app(tmp_path))

    response = client.get("/does-not-exist.html")

    assert response.status_code == 404
