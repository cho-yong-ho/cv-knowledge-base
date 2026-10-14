from pathlib import Path
from agent.src.fetcher import extract_arxiv_id, fetch_arxiv_paper
from agent.src.schemas import GeneratedDocument, DocumentFrontmatter
from agent.src.publisher import add_bibtex_entry_if_missing, format_yaml_frontmatter

def test_extract_arxiv_id():
    assert extract_arxiv_id("2304.08069") == "2304.08069"
    assert extract_arxiv_id("2304.08069v2") == "2304.08069"
    assert extract_arxiv_id("https://arxiv.org/abs/2304.08069") == "2304.08069"

def test_fetch_arxiv_paper():
    paper = fetch_arxiv_paper("2304.08069")
    assert "DETRs Beat YOLOs" in paper.title
    assert len(paper.authors) > 0
    assert paper.published_date.startswith("2023")

def test_yaml_frontmatter_format():
    doc = GeneratedDocument(
        category_folder="03-core-tasks",
        file_slug="test-doc",
        frontmatter=DocumentFrontmatter(
            title="Test Title",
            subtitle="Test Subtitle",
            date="2026-10-15",
            categories=["Core Tasks", "Testing"],
            tags=["Test", "CV"],
            bibliography="../../references.bib"
        ),
        body_markdown="## 1. Overview & TL;DR\nContent",
        bibtex_key="test2026",
        bibtex_entry="@article{test2026, title={Test}}"
    )
    yaml = format_yaml_frontmatter(doc)
    assert 'title: "Test Title"' in yaml
    assert 'categories: ["Core Tasks", "Testing"]' in yaml
    assert 'bibliography: ../../references.bib' in yaml

