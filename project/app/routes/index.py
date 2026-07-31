"""Combined upload, extraction and indexing endpoints."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile

from app.core.dependencies import get_indexing_service
from app.models import IndexResponse
from app.routes.extract import extract_saved_file, save_upload


router = APIRouter(prefix="/index", tags=["Index"])


@router.post("/upload", response_model=IndexResponse)
async def index_upload(file: UploadFile) -> IndexResponse:
    try:
        saved = await save_upload(file)
        extract_result = extract_saved_file(saved)
        index_result = get_indexing_service().index_from_json(extract_result["json_path"])
        return IndexResponse(
            status="success",
            message="Đã trích xuất và index tài liệu",
            extract_output_path=extract_result["output_dir"],
            total_pages_processed=extract_result["total_pages"],
            chunks_indexed=index_result["chunks_indexed"],
            document_id=index_result["document_id"],
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Index thất bại: {exc}") from exc


@router.post("/preprocessed", response_model=IndexResponse)
async def index_preprocessed(json_path: str) -> IndexResponse:
    """Index an OCR JSON already produced locally for a stable CP6 demo."""
    path = Path(json_path).resolve()
    if not path.exists() or path.suffix.lower() != ".json":
        raise HTTPException(status_code=400, detail="JSON path không hợp lệ")
    result = get_indexing_service().index_from_json(str(path))
    return IndexResponse(
        status="success",
        message="Đã index JSON tiền xử lý",
        extract_output_path=str(path.parent),
        chunks_indexed=result["chunks_indexed"],
        document_id=result["document_id"],
    )

