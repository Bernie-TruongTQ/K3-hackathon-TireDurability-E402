"""
Application configuration settings.
Centralized configuration following Single Responsibility Principle.
"""

from pathlib import Path
from typing import Literal

import torch
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    # Application Settings
    APP_NAME: str = "Document Understanding API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    OUTPUT_DIR: Path = BASE_DIR / "ocr_output"
    DB_PATH: Path = BASE_DIR / "db_ds"
    TEMP_DIR: Path = BASE_DIR / "temp"

    # OCR Settings
    OCR_MODEL_NAME: str = "deepseek-ai/DeepSeek-OCR"
    OCR_DPI: int = 200
    OCR_BASE_SIZE: int = 1024
    OCR_IMAGE_SIZE: int = 1024
    SKIP_FIRST_N_PAGES: int = 3  # Skip first 3 pages

    # Embedding Settings
    EMBEDDING_MODEL: str = "Qwen/Qwen3-Embedding-0.6B"
    COLLECTION_NAME: str = "slide_ds"

    # Chunking Settings
    CHUNK_BATCH_SIZE: int = 5

    # Retrieval Settings
    RETRIEVAL_TOP_K: int = 50
    RERANK_TOP_K: int = 5
    RERANKER_MODEL: str = "BAAI/bge-reranker-v2-m3"

    # LLM Settings
    LLM_PROVIDER: Literal["qwen", "gemini"] = "qwen"

    # Local LLM (Qwen) Settings
    LOCAL_LLM_MODEL: str = "Qwen/Qwen3-0.6B"
    LOCAL_LLM_MAX_TOKENS: int = 1024
    LOCAL_LLM_TEMPERATURE: float = 0.3

    # Gemini Settings
    GOOGLE_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.5-pro"
    GEMINI_MAX_TOKENS: int = 1024
    GEMINI_TEMPERATURE: float = 0.3

    # Device Settings
    DEVICE: str = "cuda" if torch.cuda.is_available() else "cpu"
    USE_BFLOAT16: bool = torch.cuda.is_bf16_supported() if torch.cuda.is_available() else False

    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()


# Create necessary directories
def setup_directories():
    """Create necessary directories if they don't exist."""
    settings.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    settings.DB_PATH.mkdir(parents=True, exist_ok=True)
    settings.TEMP_DIR.mkdir(parents=True, exist_ok=True)
