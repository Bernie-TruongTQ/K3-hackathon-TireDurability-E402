"""
Dependency injection module for FastAPI.
Provides reusable dependencies for routes.
"""

from functools import lru_cache

from app.core.config import settings
from app.services import (
    IndexingService,
    OCRService,
    RAGService,
    create_vector_store,
    create_indexing_service,
    create_ocr_service,
    create_rag_service,
)
from app.services.indexing_service import IVectorStoreRepository


@lru_cache()
def get_ocr_service() -> OCRService:
    """Get or create OCR service singleton."""
    return create_ocr_service()


@lru_cache()
def get_vector_store() -> IVectorStoreRepository:
    """Get or create vector store singleton."""
    return create_vector_store()


@lru_cache()
def get_indexing_service() -> IndexingService:
    """Get or create indexing service singleton."""
    return create_indexing_service(vector_store=get_vector_store())


@lru_cache()
def get_rag_service(llm_provider: str = None) -> RAGService:
    """
    Get or create RAG service singleton.

    Args:
        llm_provider: Override default LLM provider
    """
    vector_store = get_vector_store()
    return create_rag_service(vector_store, llm_provider or settings.LLM_PROVIDER)
