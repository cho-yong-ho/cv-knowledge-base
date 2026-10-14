import re
import subprocess
from pathlib import Path

from agent.src.config import DOCS_DIR, REFERENCES_BIB, get_quarto_env
from agent.src.schemas import GeneratedDocument

def add_bibtex_entry_if_missing(bibtex_key: str, bibtex_entry: str) -> bool:
    """Add a new BibTeX entry to references.bib without duplicates."""
    REFERENCES_BIB.parent.mkdir(parents=True, exist_ok=True)
    existing_text = ""
    if REFERENCES_BIB.exists():
        existing_text = REFERENCES_BIB.read_text(encoding="utf-8")

    # Check if key already exists (e.g. @article{key, or @inproceedings{key,)
    pattern = rf"@\w+\s*\{{\s*{re.escape(bibtex_key)}\s*,"
    if re.search(pattern, existing_text, re.IGNORECASE):
        return False  # Already exists

    clean_entry = bibtex_entry.strip()
    with open(REFERENCES_BIB, "a", encoding="utf-8") as f:
        f.write("\n\n" + clean_entry + "\n")
    return True

def format_yaml_frontmatter(doc: GeneratedDocument) -> str:
    """Construct standard Quarto YAML frontmatter."""
    fm = doc.frontmatter
    categories_str = "[" + ", ".join(f'"{c}"' for c in fm.categories) + "]"
    tags_str = "[" + ", ".join(f'"{t}"' for t in fm.tags) + "]"
    
    yaml_lines = [
        "---",
        f'title: "{fm.title}"',
        f'subtitle: "{fm.subtitle}"',
        f'date: "{fm.date}"',
        f'categories: {categories_str}',
        f'tags: {tags_str}',
        f'bibliography: {fm.bibliography}',
        "format:",
        "  html:",
        "    toc: true",
        "    code-fold: true",
        "---",
        ""
    ]
    return "\n".join(yaml_lines)

def save_document(doc: GeneratedDocument) -> Path:
    """Save the generated document into the designated category directory."""
    target_dir = DOCS_DIR / doc.category_folder
    target_dir.mkdir(parents=True, exist_ok=True)

    slug = re.sub(r"[^a-zA-Z0-9_-]", "-", doc.file_slug).lower().strip("-")
    if not slug:
        slug = "untitled-document"
    
    target_file = target_dir / f"{slug}.qmd"

    # Assemble full file content
    frontmatter_yaml = format_yaml_frontmatter(doc)
    full_content = frontmatter_yaml + "\n" + doc.body_markdown.strip() + "\n"

    target_file.write_text(full_content, encoding="utf-8")
    return target_file

def validate_quarto_render(target_file: Path) -> tuple[bool, str]:
    """Execute 'quarto render <file>' via subprocess to verify math and syntax integrity."""
    env = get_quarto_env()
    cmd = ["quarto", "render", str(target_file)]
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            env=env,
            check=False,
            timeout=60
        )
        if result.returncode == 0:
            return True, "Quarto render test succeeded!"
        else:
            return False, f"Quarto render error:\n{result.stderr or result.stdout}"
    except Exception as e:
        return False, f"Failed to execute quarto command: {e}"

def publish_document(doc: GeneratedDocument, run_render_check: bool = True) -> dict[str, any]:
    """Complete publication pipeline: BibTeX sync, file saving, and Quarto validation."""
    # 1. Update references.bib
    bib_added = add_bibtex_entry_if_missing(doc.bibtex_key, doc.bibtex_entry)

    # 2. Save .qmd file
    saved_path = save_document(doc)

    # 3. Optional Quarto validation
    render_ok = None
    render_msg = ""
    if run_render_check:
        render_ok, render_msg = validate_quarto_render(saved_path)

    return {
        "path": saved_path,
        "category": doc.category_folder,
        "bibtex_added": bib_added,
        "render_ok": render_ok,
        "render_message": render_msg
    }

