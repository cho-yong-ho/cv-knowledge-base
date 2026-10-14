import os
from pathlib import Path
from dotenv import load_dotenv

# Base paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DOCS_DIR = PROJECT_ROOT / "docs"
REFERENCES_BIB = PROJECT_ROOT / "references.bib"
ENV_FILE = PROJECT_ROOT / ".env"

# Load environment variables
load_dotenv(ENV_FILE)

# Taxonomy definitions (Category folder name -> Display Title & Description)
TAXONOMY_MAP: dict[str, dict[str, str]] = {
    "01-classical-cv": {
        "title": "Classical CV",
        "desc": "전통 영상처리 (Filtering, Edge, SIFT, Calibration, Epipolar 등)"
    },
    "02-backbones": {
        "title": "Deep Learning Backbones",
        "desc": "딥러닝 백본 아키텍처 (CNN 계열, ViT, Swin, DINOv2, Mamba 등)"
    },
    "03-core-tasks": {
        "title": "Core Vision Tasks",
        "desc": "핵심 비전 태스크 (Detection, Segmentation, Pose, Depth, Tracking)"
    },
    "04-3d-rendering": {
        "title": "3D Vision & Neural Rendering",
        "desc": "3D 비전 및 신경 렌더링 (NeRF, 3DGS, SLAM, Point Cloud)"
    },
    "05-modern-trends": {
        "title": "Modern Vision Trends",
        "desc": "최신 트렌드 (VLM/Multimodal, Diffusion/Flow Matching, VLA/Robotics)"
    }
}

def get_gemini_api_key() -> str:
    """Retrieve GEMINI_API_KEY from environment or .env file."""
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    return api_key

def get_quarto_env() -> dict[str, str]:
    """Provide a safe subprocess environment for Quarto on Windows."""
    env = os.environ.copy()
    env["TEMP"] = "C:\\Temp"
    env["TMP"] = "C:\\Temp"
    quarto_bin = "C:\\Quarto\\bin"
    if quarto_bin not in env.get("PATH", ""):
        env["PATH"] = f"{quarto_bin};{env.get('PATH', '')}"
    return env

