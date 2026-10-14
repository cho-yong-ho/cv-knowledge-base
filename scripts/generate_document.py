#!/usr/bin/env python3
"""
Autonomous Document Generator for Computer Vision Knowledge Base
Usage:
    python scripts/generate_document.py --arxiv 2304.08069
    python scripts/generate_document.py --topic "Segment Anything 2 (SAM 2)"
    python scripts/generate_document.py (Interactive Mode)
"""

import sys
import argparse
from pathlib import Path

# Add project root to sys.path so agent modules can be imported
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from agent.src.config import get_gemini_api_key, TAXONOMY_MAP
from agent.src.fetcher import fetch_arxiv_paper
from agent.src.writer import generate_document_from_topic_or_arxiv
from agent.src.publisher import publish_document

console = Console()

def parse_args():
    parser = argparse.ArgumentParser(
        description="컴퓨터비전 논문 및 주제 기반 Quarto 문서 자동 생성 에이전트"
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--arxiv", "-a",
        type=str,
        help="arXiv 논문 ID 또는 URL (예: 2304.08069 또는 https://arxiv.org/abs/2304.08069)"
    )
    group.add_argument(
        "--topic", "-t",
        type=str,
        help="컴퓨터비전 주제 또는 모델명 (예: 'DINOv2: Learning Robust Visual Features')"
    )
    parser.add_argument(
        "--model", "-m",
        type=str,
        default="gemini-2.5-flash",
        help="사용할 Gemini 모델명 (기본값: gemini-2.5-flash)"
    )
    parser.add_argument(
        "--skip-render",
        action="store_true",
        help="문서 생성 후 Quarto 렌더링 검증 건너뛰기"
    )
    return parser.parse_args()

def interactive_prompt() -> tuple[str, str]:
    """Prompt user interactively if no CLI arguments are supplied."""
    console.print(Panel.fit(
        "[bold cyan]AI Computer Vision Knowledge Base[/bold cyan]\n"
        "[dim]자율형 기술 문서 및 논문 분석 생성 에이전트[/dim]",
        border_style="cyan"
    ))
    console.print("[bold yellow]입력 방식을 선택해 주세요:[/bold yellow]")
    console.print("  [bold 1]1.[/bold 1] arXiv 논문 ID 또는 URL 입력")
    console.print("  [bold 2]2.[/bold 2] 자유 형식의 컴퓨터비전 주제/모델명 입력")
    
    choice = input("\n선택 (1 또는 2, 기본값 1): ").strip()
    if choice == "2":
        topic = input("분석할 컴퓨터비전 주제나 모델명을 입력하세요: ").strip()
        if not topic:
            console.print("[red]오류: 주제가 입력되지 않았습니다.[/red]")
            sys.exit(1)
        return "topic", topic
    else:
        arxiv_id = input("arXiv ID 또는 URL을 입력하세요 (예: 2304.08069): ").strip()
        if not arxiv_id:
            console.print("[red]오류: arXiv ID가 입력되지 않았습니다.[/red]")
            sys.exit(1)
        return "arxiv", arxiv_id

def main():
    args = parse_args()
    
    # 1. Check API Key
    api_key = get_gemini_api_key()
    if not api_key:
        console.print(Panel(
            "[bold red]❌ GEMINI_API_KEY가 설정되지 않았습니다![/bold red]\n\n"
            "프로젝트 루트의 [cyan].env[/cyan] 파일에 아래와 같이 API 키를 설정해 주세요:\n"
            "[green]GEMINI_API_KEY=your_gemini_api_key_here[/green]\n\n"
            "[dim]키 발급: https://aistudio.google.com/app/apikey[/dim]",
            title="환경변수 설정 필요",
            border_style="red"
        ))
        sys.exit(1)

    # 2. Determine target input
    input_type = None
    input_val = None
    if args.arxiv:
        input_type = "arxiv"
        input_val = args.arxiv
    elif args.topic:
        input_type = "topic"
        input_val = args.topic
    else:
        input_type, input_val = interactive_prompt()

    paper_meta = None
    topic_str = None

    # 3. Fetch metadata if arXiv
    if input_type == "arxiv":
        with console.status(f"[bold cyan]arXiv 메타데이터 수집 중: {input_val}...[/bold cyan]"):
            try:
                paper_meta = fetch_arxiv_paper(input_val)
            except Exception as e:
                console.print(f"[bold red]❌ arXiv 메타데이터 수집 실패:[/bold red] {e}")
                sys.exit(1)

        console.print(Panel(
            f"[bold]제목:[/bold] {paper_meta.title}\n"
            f"[bold]저자:[/bold] {', '.join(paper_meta.authors[:4])}\n"
            f"[bold]일자:[/bold] {paper_meta.published_date} | [bold]분류:[/bold] {paper_meta.primary_category}",
            title=f"arXiv Paper: {paper_meta.arxiv_id}",
            border_style="blue"
        ))
    else:
        topic_str = input_val
        console.print(f"[cyan]ℹ 분석 주제:[/cyan] [bold]{topic_str}[/bold]")

    # 4. Generate structured document via Gemini SDK
    with console.status(f"[bold magenta]Gemini ({args.model}) 호출 및 6단 기술 문서 생성 중...[/bold magenta]"):
        try:
            doc = generate_document_from_topic_or_arxiv(
                topic=topic_str,
                paper=paper_meta,
                model_name=args.model
            )
        except Exception as e:
            console.print(f"[bold red]❌ 문서 생성 실패:[/bold red] {e}")
            sys.exit(1)

    console.print(f"[green]✔ 문서 생성 완료:[/green] [bold]{doc.frontmatter.title}[/bold]")

    # 5. Publish to designated category folder and update references.bib
    with console.status("[bold yellow]파일 저장 및 references.bib 동기화 중...[/bold yellow]"):
        pub_result = publish_document(
            doc=doc,
            run_render_check=not args.skip_render
        )

    # 6. Display results
    cat_info = TAXONOMY_MAP.get(pub_result["category"], {"title": pub_result["category"]})
    
    table = Table(title="문서 생성 및 배포 결과", border_style="green")
    table.add_column("항목", style="bold cyan")
    table.add_column("내용", style="white")

    table.add_row("제목", doc.frontmatter.title)
    table.add_row("부제목", doc.frontmatter.subtitle)
    table.add_row("배치 카테고리", f"{pub_result['category']} ({cat_info['title']})")
    table.add_row("저장 파일 경로", str(pub_result["path"]))
    table.add_row("BibTeX 키", f"[@{doc.bibtex_key}]")
    table.add_row("BibTeX 추가 여부", "새로 추가됨" if pub_result["bibtex_added"] else "이미 존재함 (중복 방지)")

    if not args.skip_render:
        status_text = "[bold green]성공 (Valid)[/bold green]" if pub_result["render_ok"] else "[bold red]실패 (Warning/Error)[/bold red]"
        table.add_row("Quarto 렌더링 검증", status_text)
        if not pub_result["render_ok"]:
            console.print(Panel(pub_result["render_message"], title="렌더링 오류 로그", border_style="red"))

    console.print(table)
    console.print(f"\n[bold green]✨ 작업 완료![/bold green] 실시간 프리뷰 서버([cyan]http://localhost:4848/[/cyan])에서 확인하실 수 있습니다.")

if __name__ == "__main__":
    main()

