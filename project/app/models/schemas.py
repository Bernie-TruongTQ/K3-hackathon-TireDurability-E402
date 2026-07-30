"""
Pydantic models for API request/response schemas.
"""

from typing import List, Optional

from pydantic import BaseModel, Field


# ==================== Extract Endpoint Schemas ====================
class ExtractRequest(BaseModel):
    """Request schema for document extraction."""

    file_path: str = Field(..., description="Path to PDF file or image to extract")

    class Config:
        json_schema_extra = {"example": {"file_path": "documents/sample.pdf"}}


class ExtractResponse(BaseModel):
    """Response schema for document extraction."""

    status: str = Field(..., description="Status of extraction: success or failed")
    message: str = Field(..., description="Status message")
    output_path: Optional[str] = Field(None, description="Path to output directory with JSON and Markdown files")
    total_pages: Optional[int] = Field(None, description="Total number of pages processed")
    elements_count: Optional[int] = Field(None, description="Total number of elements extracted")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": "Document extracted successfully",
                "output_path": "ocr_output/sample",
                "total_pages": 10,
                "elements_count": 245,
            }
        }


# ==================== Index Endpoint Schemas ====================
class IndexRequest(BaseModel):
    """Request schema for document indexing."""

    file_path: str = Field(..., description="Path to PDF file or image to extract and index")
    extract_only: bool = Field(False, description="If True, only extract without indexing")

    class Config:
        json_schema_extra = {"example": {"file_path": "documents/sample.pdf", "extract_only": False}}


class IndexResponse(BaseModel):
    """Response schema for document indexing."""

    status: str = Field(..., description="Status of indexing: success or failed")
    message: str = Field(..., description="Status message")
    extract_output_path: Optional[str] = Field(None, description="Path to extraction output")
    total_pages_processed: Optional[int] = Field(None, description="Total pages processed")
    chunks_indexed: Optional[int] = Field(None, description="Number of chunks indexed to database")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": "Document indexed successfully",
                "extract_output_path": "ocr_output/sample",
                "total_pages_processed": 10,
                "chunks_indexed": 10,
            }
        }


# ==================== Chat Endpoint Schemas ====================
class ChatRequest(BaseModel):
    """Request schema for chat/query."""

    query: str = Field(..., description="User's question or query", min_length=1)
    llm_provider: Optional[str] = Field(None, description="Override default LLM provider: 'qwen' or 'gemini'")

    class Config:
        json_schema_extra = {"example": {"query": "Nội dung chính của tài liệu là gì?", "llm_provider": "qwen"}}


class SourceDocument(BaseModel):
    """Schema for source document in chat response."""

    page: int = Field(..., description="Page number")
    filename: str = Field(..., description="Original filename")
    content_preview: str = Field(..., description="Preview of the content (first 200 chars)")


class ChatResponse(BaseModel):
    """Response schema for chat/query."""

    status: str = Field(..., description="Status of query: success or failed")
    query: str = Field(..., description="Original query")
    answer: str = Field(..., description="Generated answer")
    sources: List[SourceDocument] = Field(default_factory=list, description="Source documents used")
    llm_provider: str = Field(..., description="LLM provider used for generation")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "query": "Nội dung chính của tài liệu là gì?",
                "answer": "Tài liệu trình bày về...",
                "sources": [{"page": 5, "filename": "sample.pdf", "content_preview": "Nội dung chính bao gồm..."}],
                "llm_provider": "qwen",
            }
        }


# ==================== Common Schemas ====================
class HealthResponse(BaseModel):
    """Response schema for health check endpoint."""

    status: str = Field(..., description="Health status")
    version: str = Field(..., description="API version")
    message: str = Field(..., description="Health message")

    class Config:
        json_schema_extra = {
            "example": {"status": "healthy", "version": "1.0.0", "message": "Document Understanding API is running"}
        }


class ErrorResponse(BaseModel):
    """Response schema for errors."""

    status: str = Field(default="error", description="Error status")
    message: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "error",
                "message": "Failed to process document",
                "detail": "File not found: documents/sample.pdf",
            }
        }
