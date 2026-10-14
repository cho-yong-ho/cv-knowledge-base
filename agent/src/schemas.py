from typing import Literal
from pydantic import BaseModel, Field

CategoryType = Literal[
    "01-classical-cv",
    "02-backbones",
    "03-core-tasks",
    "04-3d-rendering",
    "05-modern-trends"
]

class DocumentFrontmatter(BaseModel):
    title: str = Field(description="명확하고 정돈된 기술 문서 제목 (예: DINOv2: 대규모 자기지도 학습 기반 비전 백본)")
    subtitle: str = Field(description="핵심 아키텍처 및 기여를 요약한 한 줄 부제목")
    date: str = Field(description="문서 작성일 (YYYY-MM-DD)")
    categories: list[str] = Field(description="대분류 및 중분류 카테고리 (예: ['Deep Learning Backbones', 'Self-Supervised Learning'])")
    tags: list[str] = Field(description="핵심 키워드 및 학회 태그 (예: ['DINOv2', 'Vision Transformer', 'SSL', 'Meta AI'])")
    bibliography: str = Field(default="../../references.bib", description="상대 경로 BibTeX 참조 경로")

class GeneratedDocument(BaseModel):
    category_folder: CategoryType = Field(description="AGENTS.md 규칙에 정의된 5대 카테고리 디렉토리 중 가장 적합한 하나")
    file_slug: str = Field(description="영문 소문자 및 하이픈으로 구성된 파일명 (확장자 제외, 예: dinov2-vision-backbone)")
    frontmatter: DocumentFrontmatter = Field(description="문서 상단 YAML Frontmatter 메타데이터")
    body_markdown: str = Field(description="AGENTS.md 6단 템플릿(TL;DR, 등장배경, Mermaid 파이프라인, LaTeX 수식, PyTorch 코드, 비교표)을 철저히 준수한 본문 마크다운")
    bibtex_key: str = Field(description="논문 인용 고유 키 (예: oquab2023dinov2)")
    bibtex_entry: str = Field(description="표준 BibTeX 엔트리 전체 텍스트 (@article{key, ...})")

class ArxivPaperMetadata(BaseModel):
    arxiv_id: str
    title: str
    authors: list[str]
    published_date: str
    abstract: str
    pdf_url: str
    primary_category: str
    categories: list[str]

