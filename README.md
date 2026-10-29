# AI Computer Vision Knowledge Base & Autonomous Agent

이 프로젝트는 **컴퓨터 비전(Computer Vision)의 고전 알고리즘부터 최신 트렌드(VLM, 3D Vision, Embodied AI 등)까지 체계적으로 정리하는 기술 위키**이자, **최신 논문을 수집·요약하여 문서를 자동으로 생성 및 배포하는 AI 에이전트 시스템**입니다.

GitHub Actions를 통해 Quarto 기반 정적 사이트가 GitHub Pages에 자동 빌드 및 배포됩니다.

---

## 💻 다른 컴퓨터 / 새 환경에서 이어서 작업하기 (Getting Started)

새로운 PC나 노트북 환경에서 이 프로젝트를 클론하여 바로 작업을 재개할 수 있도록 안내합니다.

### 1. 사전 필수 도구 설치

새 컴퓨터에 아래 도구들이 설치되어 있어야 합니다.

| 도구 | 권장 버전 | 설명 및 다운로드 링크 |
| :--- | :--- | :--- |
| **Git** | 최신 버전 | 버전 관리 도구 ([git-scm.com](https://git-scm.com/)) |
| **Python** | 3.11 이상 | 에이전트 런타임 ([python.org](https://www.python.org/)) |
| **Quarto CLI** | 최신 버전 (v1.4+) | 문서 빌드 및 로컬 프리뷰 엔진 ([quarto.org](https://quarto.org/docs/get-started/)) |
| **uv** *(권장)* | 최신 버전 | 고속 Python 패키지 매니저 (`pip install uv`) |

---

### 2. 저장소 복제 (Clone)

터미널(또는 PowerShell / Bash)을 열고 프로젝트를 다운로드합니다.

```bash
git clone https://github.com/cho-yong-ho/cv-knowledge-base.git
cd cv-knowledge-base
```

---

### 3. 환경 변수 설정 (`.env`)

보안 정책상 실제 API 키는 Git에 포함되지 않습니다. `.env.example`을 복사하여 `.env` 파일을 생성하고 키를 설정합니다.

* **Windows PowerShell:**
  ```powershell
  Copy-Item .env.example .env
  ```
* **macOS / Linux / Git Bash:**
  ```bash
  cp .env.example .env
  ```

`.env` 파일을 열고 본인의 API 키를 입력합니다:
```ini
# Gemini API Configuration (필수: 논문 요약 에이전트용)
GEMINI_API_KEY=your_gemini_api_key_here

# GitHub Token (선택: 에이전트의 자동 푸시 사용 시)
GITHUB_TOKEN=your_github_token_here
```

---

### 4. 파이썬 가상환경 및 패키지 설치

에이전트 모듈 실행 및 테스트를 위해 의존성을 설치합니다.

#### 방법 A: `uv` 사용 시 (권장)
```bash
cd agent
uv sync
```

#### 방법 B: 기본 `pip` 및 `venv` 사용 시
```bash
# 프로젝트 루트 디렉토리에서
python -m venv .venv

# 가상환경 활성화
# Windows:
.venv\Scripts\activate
# macOS / Linux:
source .venv/bin/activate

# 의존성 설치
pip install -r requirements.txt
```

---

### 5. 로컬 개발 및 실행 확인

#### ① Quarto 기술 위키 로컬 프리뷰
문서 수정 내용을 실시간으로 브라우저에서 확인하려면:
```bash
# 프로젝트 루트에서 실행
quarto preview
```
> 로컬 웹 서버(`http://localhost:XXXX`)가 자동 실행되며, `.qmd` 문서 변경 시 핫 리로딩(Live Reloading)됩니다.

#### ② 에이전트 실행 및 테스트
```bash
# uv 사용 시
cd agent
uv run pytest                         # 단위 테스트 검증
uv run python -m src.main             # 논문 수집 및 생성 에이전트 실행
```

---

### 6. 작업 내용 반영 및 자동 배포

작업이 완료되면 `main` 브랜치에 커밋하고 푸시합니다.

```bash
git add .
git commit -m "docs: Add new vision paper summary or notes"
git push origin main
```

> **자동 배포 안내:** `main` 브랜치로 푸시되면 `.github/workflows/publish.yml`에 의해 GitHub Actions가 자동으로 Quarto 사이트를 렌더링하고 GitHub Pages로 즉시 배포합니다.

---

## 📂 프로젝트 구조 (Directory Structure)

```text
cv-knowledge-base/
├── AGENTS.md                   # AI 코딩 에이전트 아키텍처 규칙 및 지침서
├── README.md                   # 본 환경 설정 및 프로젝트 안내서
├── _quarto.yml                 # Quarto 전역 설정 및 네비게이션
├── index.qmd                   # 메인 대시보드 및 리스팅 페이지
├── references.bib              # 논문 인용 BibTeX 데이터베이스
├── styles.css                  # 웹사이트 커스텀 스타일시트
├── docs/                       # 지식 베이스 콘텐츠 영역 (.qmd)
│   ├── 01-classical-cv/        # 전통 컴퓨터비전
│   ├── 02-backbones/           # 딥러닝 백본 (CNN, ViT 등)
│   ├── 03-core-tasks/          # 핵심 비전 태스크 (Detection, Segmentation 등)
│   ├── 04-3d-rendering/        # 3D Vision & NeRF / 3DGS
│   └── 05-modern-trends/       # 최신 트렌드 (VLM, Diffusion 등)
├── assets/                     # 이미지 및 다이어그램 리소스
└── agent/                      # 논문 자동 수집 및 문서 생성 에이전트
    ├── pyproject.toml          # uv 패키지 설정
    ├── src/                    # 에이전트 소스코드 (fetcher, writer, publisher 등)
    └── tests/                  # 파이프라인 테스트 코드
```

---

## 📌 문서 작성 규칙 요약
새로운 문서를 작성하거나 에이전트를 확장할 때는 [AGENTS.md](AGENTS.md)의 규격을 준수합니다.
* 모든 수식은 유니코드 대신 **LaTeX 문법**(`$...$`, `$$...$$`) 사용
* 아키텍처 및 파이프라인은 **Mermaid.js**(` ```{mermaid} `)로 시각화
* 새 논문 인용 시 루트의 `references.bib`에 BibTeX 추가 후 `[@citekey]`로 인용
