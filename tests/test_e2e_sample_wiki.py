import shutil
from pathlib import Path

from fastapi.testclient import TestClient

from wikisrv.app import create_app

FIXTURE_ROOT = Path(__file__).parent / "fixtures" / "sample_wiki"


def sample_wiki_root(tmp_path: Path) -> Path:
    assert FIXTURE_ROOT.is_dir()

    destination = tmp_path / "sample_wiki"
    shutil.copytree(FIXTURE_ROOT, destination)
    return destination


def test_sample_wiki_index_page_matches_real_vault_shape(tmp_path: Path) -> None:
    wiki_root = sample_wiki_root(tmp_path)
    client = TestClient(create_app(wiki_root))

    response = client.get("/index.html")

    assert response.status_code == 200
    assert "<h1>Index</h1>" in response.text
    assert 'href="/overview.html"' in response.text
    assert 'href="/open-questions.html"' in response.text
    assert 'href="/pages/topics/service-architecture.html"' in response.text
    assert 'href="/pages/topics/team-operating-rhythm.html"' in response.text
    assert 'href="/pages/entities/atlas-platform.html"' in response.text
    assert 'href="/pages/sources/src-20260110-002-team-playbook.html"' in response.text


def test_sample_wiki_topic_page_renders_frontmatter_and_cross_links(tmp_path: Path) -> None:
    wiki_root = sample_wiki_root(tmp_path)
    client = TestClient(create_app(wiki_root))

    response = client.get("/pages/topics/team-operating-rhythm.html")

    assert response.status_code == 200
    assert "<h1>Current synthesis</h1>" in response.text
    assert "title: " not in response.text
    assert "source_ids" not in response.text
    assert 'href="/pages/sources/src-20260110-002-team-playbook.html"' in response.text
    assert 'href="/pages/topics/service-architecture.html"' in response.text


def test_sample_wiki_source_page_links_to_pdf_attachments_and_serves_them(tmp_path: Path) -> None:
    wiki_root = sample_wiki_root(tmp_path)
    client = TestClient(create_app(wiki_root))

    source_response = client.get("/pages/sources/src-20260110-003-rollout-documents.html")

    assert source_response.status_code == 200
    assert (
        'href="../../raw/files/attachments/2026-01-10/architecture-diagram.pdf"'
        in source_response.text
    )
    assert (
        'href="../../raw/files/attachments/2026-02-17/rollout-checklist.pdf"'
        in source_response.text
    )

    attachment_response = client.get("/raw/files/attachments/2026-01-10/architecture-diagram.pdf")

    assert attachment_response.status_code == 200
    assert attachment_response.headers["content-type"] == "application/pdf"
    assert attachment_response.content.startswith(b"%PDF-1.4")


def test_sample_wiki_includes_analysis_timeline_and_raw_mailbox_pages(tmp_path: Path) -> None:
    wiki_root = sample_wiki_root(tmp_path)
    client = TestClient(create_app(wiki_root))

    analysis_response = client.get("/pages/analyses/knowledge-base-gap-analysis.html")
    timeline_response = client.get("/pages/timelines/atlas-platform-rollout.html")
    raw_response = client.get("/raw/files/src-20260110-003-rollout-documents.html")

    assert analysis_response.status_code == 200
    assert "<h1>Question</h1>" in analysis_response.text

    assert timeline_response.status_code == 200
    assert "<h1>Timeline</h1>" in timeline_response.text

    assert raw_response.status_code == 200
    assert "Architecture diagram" in raw_response.text
    assert 'href="attachments/2026-01-10/architecture-diagram.pdf"' in raw_response.text
