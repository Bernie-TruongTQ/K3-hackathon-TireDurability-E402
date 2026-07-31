"""Upload and OCR/preprocess documents."""

from __future__ import annotations

import json
import logging
import shutil
import uuid
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile

from app.core.config import settings
from app.core.dependencies import get_ocr_service
from app.models import ExtractResponse


router = APIRouter(prefix="/extract", tags=["Extract"])
ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".webp", ".md", ".json"}
logger = logging.getLogger(__name__)


def _safe_name(filename: str | None) -> str:
    name = Path(filename or "document").name
    return re_safe.sub("_", name)


import re

re_safe = re.compile(r"[^A-Za-z0-9._-]+")


async def save_upload(file: UploadFile) -> Path:
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Định dạng chưa hỗ trợ: {suffix}")

    settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    destination = settings.UPLOAD_DIR / f"{uuid.uuid4().hex}_{_safe_name(file.filename)}"
    size = 0
    with destination.open("wb") as handle:
        while chunk := await file.read(1024 * 1024):
            size += len(chunk)
            if size > settings.MAX_UPLOAD_MB * 1024 * 1024:
                destination.unlink(missing_ok=True)
                raise HTTPException(status_code=413, detail="Tệp vượt quá giới hạn upload")
            handle.write(chunk)
    await file.close()
    return destination


def preprocess_markdown(path: Path, output_dir: Path) -> dict:
    document_id = uuid.uuid4().hex
    content = path.read_text(encoding="utf-8")
    payload = {
        "document_id": document_id,
        "elements": [
            {
                "file_name": document_id,
                "page": 1,
                "region_order": 1,
                "region_type": "text",
                "content": content,
                "original_filename": path.name,
                "metadata": {"page": 1, "region_type": "text", "coordinates": []},
                "saved_link": None,
            }
        ],
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / f"{path.stem}.json"
    markdown_path = output_dir / f"{path.stem}.md"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    markdown_path.write_text(content, encoding="utf-8")
    return {
        "json_path": str(json_path),
        "markdown_path": str(markdown_path),
        "total_pages": 1,
        "elements_count": 1,
        "output_dir": str(output_dir),
    }


def preprocess_native_pdf(path: Path, output_dir: Path) -> dict:
    """Extract a born-digital PDF without loading the GPU OCR model.

    Each page contributes one text element plus one full-page visual element.
    The visual element keeps an image path so GPT-4o mini can inspect diagrams,
    tables and formulas when the query is routed to the VLM.
    """
    import fitz

    document_id = uuid.uuid4().hex
    output_dir.mkdir(parents=True, exist_ok=True)
    image_dir = output_dir / "images"
    image_dir.mkdir(parents=True, exist_ok=True)

    elements: list[dict] = []
    markdown_pages: list[str] = []
    total_text_chars = 0

    with fitz.open(path) as document:
        if document.page_count == 0:
            raise ValueError("PDF không có trang")

        for page_index, page in enumerate(document):
            page_number = page_index + 1
            page_text = page.get_text("text").strip()
            total_text_chars += len(page_text)
            if page_text:
                markdown_pages.append(f"## Trang {page_number}\n\n{page_text}")
                elements.append(
                    {
                        "file_name": document_id,
                        "page": page_number,
                        "region_order": 1,
                        "region_type": "text",
                        "content": page_text,
                        "original_filename": path.name,
                        "metadata": {
                            "page": page_number,
                            "region_type": "text",
                            "coordinates": [],
                            "extraction_method": "native_pdf_text",
                        },
                        "saved_link": None,
                    }
                )

            image_path = image_dir / f"page_{page_number:04d}.png"
            pixmap = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5), alpha=False)
            pixmap.save(image_path)
            elements.append(
                {
                    "file_name": document_id,
                    "page": page_number,
                    "region_order": 2,
                    "region_type": "image",
                    "content": (
                        f"Ảnh toàn trang {page_number}. Dùng ảnh này khi câu hỏi "
                        "yêu cầu đọc hình, bảng, biểu đồ hoặc công thức."
                    ),
                    "original_filename": path.name,
                    "metadata": {
                        "page": page_number,
                        "region_type": "image",
                        "coordinates": [0, 0, 1000, 1000],
                        "extraction_method": "native_pdf_render",
                    },
                    "saved_link": str(image_path),
                }
            )

        # A digitally generated slide deck normally exposes substantial text.
        # If it does not, defer to DeepSeek-OCR instead of indexing empty pages.
        minimum_text = max(20, document.page_count * 10)
        if total_text_chars < minimum_text:
            raise ValueError(
                "PDF không có đủ text gốc; cần DeepSeek-OCR trên máy GPU"
            )
        page_count = document.page_count

    json_path = output_dir / f"{path.stem}.json"
    markdown_path = output_dir / f"{path.stem}.md"
    json_path.write_text(
        json.dumps({"document_id": document_id, "elements": elements}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    markdown_path.write_text("\n\n---\n\n".join(markdown_pages), encoding="utf-8")
    return {
        "json_path": str(json_path),
        "markdown_path": str(markdown_path),
        "total_pages": page_count,
        "elements_count": len(elements),
        "output_dir": str(output_dir),
    }


def extract_saved_file(path: Path) -> dict:
    output_dir = settings.OUTPUT_DIR / f"{path.stem}_{uuid.uuid4().hex[:8]}"
    suffix = path.suffix.lower()
    if suffix == ".md":
        return preprocess_markdown(path, output_dir)
    if suffix == ".json":
        output_dir.mkdir(parents=True, exist_ok=True)
        destination = output_dir / path.name
        shutil.copy2(path, destination)
        payload = json.loads(destination.read_text(encoding="utf-8"))
        return {
            "json_path": str(destination),
            "markdown_path": None,
            "total_pages": len({item.get("page") for item in payload.get("elements", [])}),
            "elements_count": len(payload.get("elements", [])),
            "output_dir": str(output_dir),
        }
    if suffix == ".pdf":
        try:
            return preprocess_native_pdf(path, output_dir)
        except (ImportError, ValueError) as exc:
            logger.info("Native PDF extraction unavailable, falling back to DeepSeek-OCR: %s", exc)
    return get_ocr_service().process_document(str(path), str(output_dir))


@router.post("", response_model=ExtractResponse)
async def extract_document(file: UploadFile) -> ExtractResponse:
    try:
        saved = await save_upload(file)
        result = extract_saved_file(saved)
        return ExtractResponse(
            status="success",
            message="Đã trích xuất tài liệu",
            output_path=result["output_dir"],
            total_pages=result["total_pages"],
            elements_count=result["elements_count"],
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Trích xuất thất bại: {exc}") from exc
