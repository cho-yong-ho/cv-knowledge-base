from typing import Optional
from google import genai
from google.genai import types

from agent.src.config import get_gemini_api_key, TAXONOMY_MAP
from agent.src.schemas import GeneratedDocument, ArxivPaperMetadata

SYSTEM_PROMPT = """당신은 최고 수준의 컴퓨터비전(Computer Vision) 연구원이자 기술 문서 작성자입니다.
주어진 컴퓨터비전 주제 또는 arXiv 논문 정보를 바탕으로, Quarto(.qmd) 지식 베이스용 심층 기술 문서를 생성해야 합니다.

### [필수 아키텍처 제약 및 카테고리 분류]
문서가 다루는 내용에 따라 반드시 아래 5대 카테고리 폴더 중 하나를 선택하십시오:
- `01-classical-cv`: 전통 영상처리 (Filtering, Edge, SIFT/SURF, Calibration, Epipolar 등)
- `02-backbones`: 딥러닝 백본 아키텍처 (CNN 계열, ViT, Swin, DINOv2, Mamba 등)
- `03-core-tasks`: 핵심 비전 태스크 (Detection, Segmentation, Pose, Depth, Tracking 등)
- `04-3d-rendering`: 3D Vision & Neural Rendering (NeRF, 3DGS, SLAM, Point Cloud 등)
- `05-modern-trends`: 최신 트렌드 (VLM/Multimodal, Diffusion/Flow Matching, VLA/Robotics 등)

### [문서 본문(body_markdown) 6단 작성 표준]
본문은 다음 6개 섹션 헤더(##)를 정확히 준수하여 전문적이고 심도 깊은 한국어로 작성해야 합니다:

1. ## 1. Overview & TL;DR
   - 반드시 Quarto의 `::: {.callout-note}` 블록으로 감싸십시오.
   - **해결하고자 한 문제:** 이전 기법들의 한계점 및 동기(Motivation).
   - **핵심 기여 (Core Contributions):** 모델이나 이론의 3대 핵심 혁신 요소를 번호 매겨 요약.

2. ## 2. Historical Context (등장 배경)
   - 이전 세대 기법의 구체적인 수학적/하드웨어적 한계점 서술.
   - 선행 논문들을 Quarto 인용 문법(예: `[@vaswani2017attention]`, `[@mildenhall2020nerf]`)으로 언급.

3. ## 3. Architecture & Pipeline
   - 입력 텐서 $\mathbf{I} \in \mathbb{R}^{H \times W \times C}$부터 최종 출력까지의 전체 흐름.
   - 반드시 ` ```{mermaid} ` 블록으로 시작하여 모델 파이프라인을 시각화하십시오. (유효한 mermaid 문법: `flowchart TD` 또는 `flowchart LR`).
   - 다이어그램 이후 각 단계(Step 1, Step 2 ...)별 상세 메커니즘을 구체적으로 설명.

4. ## 4. Mathematical Formulation (핵심 수식)
   - 유니코드 수학 기호(×, ÷, ± 등) 사용을 엄격히 금지하고 반드시 표준 LaTeX(`$...$`, `$$...$$`)로 작성하십시오.
   - 핵심 연산(Attention, Projection, Convolution 등)과 손실 함수(Loss Function)를 엄밀히 정의하십시오.
   - 모든 수식 직후에는 불릿 리스트(-)로 기호의 차원(Dimension)과 물리적 의미를 빠짐없이 명시하십시오 (예: * $\mathbf{x} \in \mathbb{R}^D$: 입력 특성 벡터).

5. ## 5. PyTorch / Pseudo-code Implementation
   - 핵심 모듈의 동작 원리를 보여주는 간결하고 실제 실행 가능한 형태의 PyTorch 코드 블록(```python ... ```)을 작성하십시오.
   - 명확한 타입 힌팅과 주석을 포함하십시오.

6. ## 6. Comparison & Limitations
   - 기존 SOTA 모델들과의 비교표(Markdown Table: 모델명, 핵심 특징, 추론 속도, 정량적 성능 등).
   - 이 모델의 실제 적용 시 발생하는 병목 현상, 연산 복잡도, 혹은 미해결 한계점(Limitations) 3가지를 명확히 분석.
   - 마지막에 참고문헌 블록(`## References` 및 `::: {#refs}` `:::`)을 포함하십시오.

### [BibTeX 규칙]
- `bibtex_key`: 영문소문자저자+연도+단축키 (예: `zhao2024detrs`)
- `bibtex_entry`: 표준 BibTeX 엔트리 포맷.
"""

def generate_document_from_topic_or_arxiv(
    topic: Optional[str] = None,
    paper: Optional[ArxivPaperMetadata] = None,
    model_name: str = "gemini-2.5-flash"
) -> GeneratedDocument:
    """Generate a structured QMD document using the modern google-genai SDK."""
    api_key = get_gemini_api_key()
    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY가 설정되지 않았습니다.\n"
            "프로젝트 루트의 .env 파일에 'GEMINI_API_KEY=your_key'를 등록해 주세요."
        )

    client = genai.Client(api_key=api_key)

    if paper:
        user_prompt = f"""다음 arXiv 논문 정보를 바탕으로 최고의 컴퓨터비전 기술 문서(.qmd)를 작성해 주십시오:

- **arXiv ID:** {paper.arxiv_id}
- **제목:** {paper.title}
- **저자:** {", ".join(paper.authors[:5])}
- **발행일:** {paper.published_date}
- **분류:** {paper.primary_category} ({", ".join(paper.categories)})
- **초록 (Abstract):**
{paper.abstract}
"""
    else:
        user_prompt = f"""다음 컴퓨터비전 주제에 대해 최고의 기술 문서(.qmd)를 작성해 주십시오:

- **주제/모델:** {topic}
"""

    response = client.models.generate_content(
        model=model_name,
        contents=[
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=user_prompt)]
            )
        ],
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            response_mime_type="application/json",
            response_schema=GeneratedDocument,
            temperature=0.2,
        ),
    )

    result_json = response.text
    document = GeneratedDocument.model_validate_json(result_json)
    return document

