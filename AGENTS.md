# Project Overview: AI Computer Vision Knowledge Base & Autonomous Agent

이 프로젝트는 **컴퓨터비전(Computer Vision)의 고전 알고리즘부터 최신 트렌드(VLM, 3D Vision, Embodied AI 등)까지 체계적으로 정리하는 개인용 기술 위키**이자, **최신 논문을 수집·요약하여 문서를 자동으로 생성 및 배포하는 AI 에이전트 시스템**입니다.

Antigravity 에이전트는 본 지침(`AGENTS.md`)을 최우선 아키텍처 제약 조건 및 코딩 표준으로 삼아 모든 파일 생성, 문서 작성, 파이썬 에이전트 스크립트 개발을 수행해야 합니다.

---

## 1. Tech Stack & Architecture Constraints

* **Documentation Engine:** [Quarto](https://quarto.org/) (`.qmd` 포맷 기반의 과학·기술 출판 프레임워크)
* **Math & Diagrams:** 
  * 모든 수식은 **LaTeX 표준 문법**(`$...$` 및 `$$...$$`)으로 작성하며, 유니코드 수학 기호 사용을 엄격히 금지합니다.
  * 모델 파이프라인 및 신경망 아키텍처 다이어그램은 반드시 **Mermaid.js** (` ```{mermaid} `) 블록을 사용하여 시각화합니다.
* **Agent Backend (Python):**
  * **Python Version:** 3.11+ (패키지 및 가상환경 관리는 `uv` 사용을 기본으로 함)
  * **Core Libraries:** `google-genai` (최신 Gemini SDK), `pydantic` (Structured Output 및 Frontmatter 검증), `arxiv` / `httpx` (논문 메타데이터 및 초록 수집), `GitPython` (자동 커밋 유틸리티)
* **Hosting & CI/CD:** GitHub Actions를 통한 빌드 자동화 및 Cloudflare Pages (또는 GitHub Pages) 정적 배포

---

## 2. Directory Structure & Taxonomy Rules

에이전트가 새로운 개념 문서나 논문 요약본을 생성할 때는 반드시 아래의 디렉토리 구조(Taxonomy)를 준수하여 알맞은 경로에 배치해야 합니다. 임의의 루트 폴더 생성을 금지합니다.

```text
cv-knowledge-base/
├── AGENTS.md                   # Antigravity 에이전트 프로젝트 지침서 (현재 파일)
├── _quarto.yml                 # Quarto 전역 설정 및 네비게이션 구성
├── index.qmd                   # 메인 대시보드 및 최근 업데이트 목록 (Quarto Listing 활용)
├── references.bib              # 모든 문서에서 공유하는 논문 인용 BibTeX 데이터베이스
├── docs/                       # [지식 베이스 콘텐츠 영역]
│   ├── 01-classical-cv/        # 전통 영상처리 (Filtering, Edge, SIFT, Calibration, Epipolar 등)
│   ├── 02-backbones/           # 딥러닝 백본 아키텍처 (CNN 계열, ViT, Swin, DINOv2, Mamba 등)
│   ├── 03-core-tasks/          # 핵심 비전 태스크 (Detection, Segmentation, Pose, Depth, Tracking)
│   ├── 04-3d-rendering/        # 3D Vision & Neural Rendering (NeRF, 3DGS, SLAM, Point Cloud)
│   └── 05-modern-trends/       # 최신 트렌드 (VLM/Multimodal, Diffusion/Flow Matching, VLA/Robotics)
├── assets/                     # 이미지 및 다이어그램 리소스 (문서 경로와 매칭되는 하위 폴더 사용)
└── agent/                      # [자동화 파이썬 에이전트 영역]
    ├── pyproject.toml          # uv 패키지 설정 파일
    ├── src/
    │   ├── config.py           # 환경변수 및 경로 설정
    │   ├── schemas.py          # 문서 Frontmatter 및 논문 요약 구조체에 대한 Pydantic 모델
    │   ├── fetcher.py          # arXiv API, HuggingFace Papers 등 논문/트렌드 데이터 수집기
    │   ├── writer.py           # LLM 호출을 통한 .qmd 마크다운 문서 및 BibTeX 생성기
    │   └── publisher.py        # references.bib 병합, Quarto 렌더링 검증 및 Git 커밋 자동화
    └── tests/                  # 에이전트 파이프라인 단위 테스트
```

---

## 3. Content Authoring Rules (`.qmd` 문서 작성 표준)

Antigravity 에이전트가 직접 컴퓨터비전 문서를 작성하거나, 문서를 생성하는 파이썬 프롬프트를 설계할 때는 다음 규칙을 강제합니다.

### 3.1. YAML Frontmatter 필수 스키마
모든 `.qmd` 문서는 최상단에 아래 형식의 YAML Frontmatter를 반드시 포함해야 합니다.

```yaml
---
title: "논문 또는 개념의 명확한 제목 (예: 3D Gaussian Splatting 심층 분석)"
subtitle: "핵심 한 줄 요약"
date: "YYYY-MM-DD"
categories: ["3D Vision", "Neural Rendering"] # 대분류 및 중분류
tags: ["3DGS", "Real-time Rendering", "Point Cloud", "SIGGRAPH 2023"]
bibliography: ../../references.bib
format:
  html:
    toc: true
    code-fold: true
---
```

### 3.2. 컴퓨터비전 문서 본문 템플릿 구조
문서 본문은 독자(개발자 본인)가 직관적으로 빠르게 핵심을 파악할 수 있도록 다음 6단 구조를 따릅니다.

1. **Overview & TL;DR:** Quarto의 `::: {.callout-note}` 블록을 사용하여 해당 기술/논문이 해결하고자 한 문제와 핵심 기여(Contribution) 3가지를 요약합니다.
2. **Historical Context (등장 배경):** 이전 세대 기법의 한계점과 이 기법이 등장하게 된 맥락을 설명합니다 (예: `NeRF의 느린 MLP 샘플링 속도를 극복하기 위해 등장`).
3. **Architecture & Pipeline:** 입력 텐서(예: $\mathbf{I} \in \mathbb{R}^{H \times W \times 3}$)가 어떤 연산 과정을 거쳐 출력으로 변환되는지 ` ```{mermaid} ` 다이어그램으로 먼저 도식화하고 단계별로 설명합니다.
4. **Mathematical Formulation (핵심 수식):** 
   * 핵심 연산 및 손실 함수(Loss Function)를 LaTeX 수식으로 엄밀하게 정의합니다.
   * 수식에 등장하는 모든 변수와 기호는 수식 직후에 불릿 리스트로 차원(Dimension)과 의미를 명시합니다.
5. **PyTorch / Pseudo-code Implementation:** 개념 이해를 돕기 위해 핵심 모듈(예: Cross-Attention 블록, RoPE, Focal Loss 등)을 간결하고 실행 가능한 PyTorch 스타일 코드로 작성합니다.
6. **Comparison & Limitations:** 기존 SOTA 모델과의 정량적/정성적 차이점을 표(Markdown Table)로 비교하고, 현재 기법의 병목 현상이나 한계점을 명시합니다.

### 3.3. 참고문헌 및 BibTeX 규칙
* 논문을 언급할 때는 하드코딩된 링크 대신 Quarto 인용 문법(예: `[@mildenhall2020nerf]`)을 사용합니다.
* 새로운 논문을 인용할 경우, 반드시 루트 경로의 `@references.bib` 파일에 해당 논문의 BibTeX 엔트리를 중복 없이 추가해야 합니다.

---

## 4. Python Agent Coding Standards (`/agent` 디렉토리 규칙)

자동화 에이전트 코드를 작성하거나 수정할 때는 다음 엔지니어링 규칙을 준수합니다.

1. **SDK 및 모델 규격:**
   * 레거시 `google-generativeai` 패키지를 절대 사용하지 마십시오. 반드시 최신 표준인 **`google-genai` SDK** (`from google import genai`)를 사용합니다.
   * LLM 출력 결과물의 파싱 오류를 방지하기 위해 `Pydantic` 스키마(`schemas.py`)와 Gemini의 `response_schema` (Structured Outputs) 기능을 결합하여 메타데이터와 본문을 안전하게 추출합니다.
2. **타입 힌팅 및 검증:**
   * 모든 파이썬 함수와 메서드에는 Python 3.11+ 표준 Type Hinting(`list[str]`, `dict[str, Any]`, `Path` 등)을 필수 적용합니다.
   * 파일 경로 처리는 문자열 결합 대신 반드시 `pathlib.Path` 객체를 사용합니다.
3. **Quarto Listing 연동 설계:**
   * 새 글이 추가될 때마다 `_quarto.yml`을 복잡하게 파싱해서 수정하는 방식 대신, 각 카테고리 폴더의 `index.qmd`에 Quarto의 **Listing 기능**(`contents: "*.qmd"`)을 설정하여 파일 생성만으로 자동 인덱싱되도록 구현합니다.
4. **안전한 파일 쓰기 및 빌드 검증:**
   * 에이전트가 `.qmd` 파일을 생성한 직후에는 `subprocess`를 통해 `quarto render <파일경로>`를 테스트 실행하여 문법 오류(잘못된 LaTeX 수식이나 깨진 Mermaid 구문)가 없는지 검증하는 방어 로직을 포함합니다.

---

## 5. Development Workflow & Execution Commands

Antigravity 에이전트는 작업 수행 시 다음 순서와 명령어를 활용합니다.

* **Step 1 (계획 수립):** 대규모 기능 추가나 에이전트 파이프라인 수정 시 코드를 바로 작성하지 말고, 먼저 구현 계획(Implementation Plan)을 세워 변경할 파일 목록을 브리핑합니다.
* **Step 2 (Quarto 로컬 프리뷰 및 빌드 검증):**
  * 전체 사이트 빌드 확인: `quarto render`
  * 로컬 실시간 프리뷰 서버 실행: `quarto preview`
* **Step 3 (Python 에이전트 환경 실행):**
  * 의존성 설치 및 동기화: `cd agent && uv sync`
  * 에이전트 스크립트 실행: `cd agent && uv run python -m src.main`
  * 테스트 실행: `cd agent && uv run pytest`
* **보안 주의사항:** `.env` 파일에 저장된 `GEMINI_API_KEY` 등의 민감 정보는 절대 코드에 하드코딩하거나 Git에 커밋하지 않으며, `.gitignore`에 반드시 등록되어 있는지 확인합니다.