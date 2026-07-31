"""Grounded VisualRAG chat endpoints."""

from __future__ import annotations

import json
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.core.config import settings
from app.core.dependencies import get_rag_service
from app.models import ChatRequest, ChatResponse, SourceDocument


router = APIRouter(prefix="/chat", tags=["Chat"])
VALID_PROVIDERS = {"demo", "qwen", "gemini", "openai"}


def _artifact_url(image_path: str | None) -> str | None:
    if not image_path:
        return None
    try:
        relative = Path(image_path).resolve().relative_to(settings.OUTPUT_DIR.resolve())
        return "/artifacts/" + relative.as_posix()
    except ValueError:
        return None


def _source(document) -> SourceDocument:
    metadata = document.metadata
    return SourceDocument(
        page=int(metadata.get("page", 0)),
        filename=str(metadata.get("filename", "unknown")),
        content_preview=document.page_content[:240],
        source_id=metadata.get("source_id"),
        region_type=metadata.get("region_type"),
        image_path=_artifact_url(metadata.get("image_path")),
        score=document.score,
    )


def _service(request: ChatRequest):
    provider = request.llm_provider or settings.LLM_PROVIDER
    if provider not in VALID_PROVIDERS:
        raise HTTPException(status_code=400, detail=f"Provider không hợp lệ: {provider}")
    try:
        return get_rag_service(provider)
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Không khởi tạo được provider {provider}: {exc}") from exc


@router.post("", response_model=ChatResponse)
async def chat_query(request: ChatRequest) -> ChatResponse:
    service = _service(request)
    result = service.query(
        request.query,
        document_id=request.document_id,
        selected_page=request.selected_page,
        selected_image_id=request.selected_image_id,
    )
    return ChatResponse(
        status="success",
        query=request.query,
        answer=result.answer,
        sources=[_source(document) for document in result.sources],
        llm_provider=result.provider,
        model=result.model,
        route=result.route,
        grounded=result.grounded,
        trace_id=result.trace_id,
        is_mock=result.is_mock,
    )


@router.post("/stream")
async def chat_query_stream(request: ChatRequest):
    service = _service(request)

    async def events():
        try:
            async for chunk in service.query_stream(
                request.query,
                document_id=request.document_id,
                selected_page=request.selected_page,
                selected_image_id=request.selected_image_id,
            ):
                yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"
        except Exception as exc:
            error = {"type": "error", "data": str(exc)}
            yield f"data: {json.dumps(error, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        events(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
