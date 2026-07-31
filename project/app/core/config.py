"""
Application configuration settings.
Centralized configuration following Single Responsibility Principle.
"""

from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


def _detect_device() -> tuple[str, bool]:
    try:
        import torch

        if torch.cuda.is_available():
            return "cuda", bool(torch.cuda.is_bf16_supported())
    except ImportError:
        pass
    return "cpu", False


DEFAULT_DEVICE, DEFAULT_BFLOAT16 = _detect_device()


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="VISUALRAG_",
        case_sensitive=True,
        extra="ignore",
    )

    # Application Settings
    APP_NAME: str = "Document Understanding API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    API_PREFIX: str = "/api/v1"

    # Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    OUTPUT_DIR: Path = BASE_DIR / "ocr_output"
    DB_PATH: Path = BASE_DIR / "db_ds"
    TEMP_DIR: Path = BASE_DIR / "temp"
    UPLOAD_DIR: Path = BASE_DIR / "uploads"

    # OCR Settings
    OCR_MODEL_NAME: str = "deepseek-ai/DeepSeek-OCR"
    OCR_DPI: int = 200
    OCR_BASE_SIZE: int = 1024
    OCR_IMAGE_SIZE: int = 1024
    SKIP_FIRST_N_PAGES: int = 0

    # Embedding Settings
    EMBEDDING_MODEL: str = "Qwen/Qwen3-Embedding-0.6B"
    COLLECTION_NAME: str = "slide_ds"
    VECTOR_STORE_PROVIDER: Literal["local", "chroma"] = "local"

    # Chunking Settings
    CHUNK_BATCH_SIZE: int = 5
    MAX_CHUNK_TOKENS: int = 1024

    # Retrieval Settings
    RETRIEVAL_TOP_K: int = 50
    RERANK_TOP_K: int = 5
    RERANKER_MODEL: str = "BAAI/bge-reranker-v2-m3"

    # LLM Settings
    LLM_PROVIDER: Literal["demo", "qwen", "gemini", "openai"] = "demo"

    # Local LLM (Qwen) Settings
    LOCAL_LLM_MODEL: str = "Qwen/Qwen3-0.6B"
    LOCAL_LLM_MAX_TOKENS: int = 1024
    LOCAL_LLM_TEMPERATURE: float = 0.3

    # Gemini Settings
    GOOGLE_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.5-pro"
    GEMINI_MAX_TOKENS: int = 1024
    GEMINI_TEMPERATURE: float = 0.3

    # OpenAI Responses API Settings
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_MAX_OUTPUT_TOKENS: int = 1024
    OPENAI_TEMPERATURE: float = 0.2

    # Device Settings
    DEVICE: str = DEFAULT_DEVICE
    USE_BFLOAT16: bool = DEFAULT_BFLOAT16
    RERANKER_PROVIDER: Literal["lexical", "cross_encoder"] = "lexical"
    MAX_UPLOAD_MB: int = 50

# Global settings instance
settings = Settings()


# Create necessary directories
def setup_directories():
    """Create necessary directories if they don't exist."""
    settings.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    settings.DB_PATH.mkdir(parents=True, exist_ok=True)
    settings.TEMP_DIR.mkdir(parents=True, exist_ok=True)
    settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
