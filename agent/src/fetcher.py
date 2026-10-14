import re
import html
import httpx
from agent.src.schemas import ArxivPaperMetadata

def extract_arxiv_id(query: str) -> str:
    """Extract clean arXiv ID from URL or raw string (e.g. '2304.08069v1' -> '2304.08069')."""
    query = query.strip()
    pattern = r"(?:arxiv\.org/(?:abs|pdf)/)?(\d{4}\.\d{4,5})(?:v\d+)?"
    match = re.search(pattern, query)
    if match:
        return match.group(1)
    return query

def fetch_arxiv_via_abs_page(arxiv_id: str) -> ArxivPaperMetadata:
    """Fetch metadata directly from arxiv.org/abs/<id> via high-speed HTTP request."""
    url = f"https://arxiv.org/abs/{arxiv_id}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    with httpx.Client(timeout=15.0, follow_redirects=True) as client:
        resp = client.get(url, headers=headers)
        if resp.status_code != 200:
            raise ValueError(f"HTTP {resp.status_code} error fetching arXiv page for {arxiv_id}")
        html_text = resp.text

    # Extract title
    title_m = re.search(r'<meta name="citation_title" content="([^"]+)"', html_text)
    title = html.unescape(title_m.group(1).replace("\n", " ").strip()) if title_m else "Untitled Paper"

    # Extract authors
    authors = [html.unescape(a) for a in re.findall(r'<meta name="citation_author" content="([^"]+)"', html_text)]

    # Extract published date
    date_m = re.search(r'<meta name="citation_date" content="([^"]+)"', html_text)
    published_date = date_m.group(1).replace("/", "-") if date_m else "2024-01-01"

    # Extract PDF URL
    pdf_m = re.search(r'<meta name="citation_pdf_url" content="([^"]+)"', html_text)
    pdf_url = pdf_m.group(1) if pdf_m else f"https://arxiv.org/pdf/{arxiv_id}.pdf"

    # Extract abstract
    abs_m = re.search(r'<blockquote class="abstract mathjax">(?:<span class="descriptor">Abstract:</span>)?(.*?)</blockquote>', html_text, re.DOTALL)
    if abs_m:
        raw_abs = abs_m.group(1)
        # Strip HTML tags
        clean_abs = re.sub(r'<[^>]+>', '', raw_abs)
        abstract = html.unescape(clean_abs).replace("\n", " ").strip()
    else:
        abstract = ""

    # Extract subject
    subj_m = re.search(r'<span class="primary-subject">([^<]+)</span>', html_text)
    primary_category = subj_m.group(1).strip() if subj_m else "cs.CV"

    return ArxivPaperMetadata(
        arxiv_id=arxiv_id,
        title=title,
        authors=authors if authors else ["Unknown Author"],
        published_date=published_date,
        abstract=abstract,
        pdf_url=pdf_url,
        primary_category=primary_category,
        categories=[primary_category]
    )

def fetch_arxiv_paper(query_or_id: str) -> ArxivPaperMetadata:
    """Fetch structured metadata for a given arXiv paper (fast HTTP with fallback)."""
    arxiv_id = extract_arxiv_id(query_or_id)
    try:
        return fetch_arxiv_via_abs_page(arxiv_id)
    except Exception as e:
        # Fallback to arxiv client package
        import arxiv
        client = arxiv.Client()
        search = arxiv.Search(id_list=[arxiv_id])
        results = list(client.results(search))
        if not results:
            search = arxiv.Search(query=query_or_id, max_results=1)
            results = list(client.results(search))
            if not results:
                raise ValueError(f"arXiv 논문을 찾을 수 없습니다: '{query_or_id}' (오류: {e})")

        paper = results[0]
        return ArxivPaperMetadata(
            arxiv_id=paper.get_short_id(),
            title=paper.title.replace("\n", " ").strip(),
            authors=[author.name for author in paper.authors],
            published_date=paper.published.strftime("%Y-%m-%d"),
            abstract=paper.summary.replace("\n", " ").strip(),
            pdf_url=paper.pdf_url,
            primary_category=paper.primary_category,
            categories=paper.categories
        )
