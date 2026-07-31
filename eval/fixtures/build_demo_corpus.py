"""Build a reproducible CP3 fixture corpus for the 24-case golden set.

The corpus is intentionally synthetic. Chatlog-derived cases keep their original
query/source reference in golden_set.jsonl, while these small documents provide
stable evidence that can be indexed and rerun without redistributing course
material.
"""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "eval" / "fixtures" / "generated"
IMAGE_DIR = ROOT / "project" / "ocr_output" / "cp3-fixtures"


def font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        Path("C:/Windows/Fonts/arial.ttf"),
        Path("C:/Windows/Fonts/calibri.ttf"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size=size)
    return ImageFont.load_default()


def visual(name: str, title: str, lines: list[str]) -> Path:
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    path = IMAGE_DIR / f"{name}.png"
    image = Image.new("RGB", (900, 520), "#F7FAFC")
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((28, 28, 872, 492), radius=22, fill="white", outline="#CBD5E1", width=3)
    draw.rectangle((28, 28, 872, 94), fill="#102A43")
    draw.text((54, 47), title, fill="white", font=font(27))
    y = 132
    colors = ["#2563EB", "#0F766E", "#D62839", "#F59E0B"]
    for index, line in enumerate(lines):
        color = colors[index % len(colors)]
        draw.rounded_rectangle((66, y, 834, y + 60), radius=12, fill="#F4F7FB", outline=color, width=3)
        draw.text((88, y + 15), line, fill="#172B4D", font=font(22))
        y += 78
    image.save(path)
    return path.resolve()


FIXTURES: dict[str, dict] = {
    "visual_identity": {
        "page": 2,
        "type": "image",
        "title": "Lecture photo",
        "lines": ["A presenter explains the course diagram"],
        "content": "Ảnh một người đang trình bày; tài liệu không ghi danh tính.",
    },
    "double_diamond": {
        "page": 16,
        "type": "diagram",
        "title": "Double Diamond",
        "lines": ["Discover", "Define", "Develop", "Deliver"],
        "content": "Double Diamond gồm bốn giai đoạn: Discover, Define, Develop, Deliver.",
    },
    "process_chart": {
        "page": 16,
        "type": "diagram",
        "title": "Process stages",
        "lines": ["Discover -> Define", "Develop -> Deliver"],
        "content": "Biểu đồ mô tả thứ tự Discover → Define → Develop → Deliver.",
    },
    "circled_table": {
        "page": 9,
        "type": "table",
        "title": "Selected table",
        "lines": ["Model A | 0.72", "Model B | 0.81", "Model C | 0.76"],
        "content": "Bảng được chọn: Model A 0.72; Model B 0.81; Model C 0.76.",
    },
    "ai_product_flow": {
        "page": 6,
        "type": "diagram",
        "title": "AI product flow",
        "lines": ["Observe", "Prototype", "Evaluate", "Iterate"],
        "content": "Quy trình phát triển sản phẩm AI: Observe → Prototype → Evaluate → Iterate.",
    },
    "attention_formula_present": {
        "page": 27,
        "type": "formula",
        "title": "Scaled dot-product attention",
        "lines": ["Attention(Q,K,V)", "= softmax(QK^T / sqrt(d_k)) V"],
        "content": "Công thức: Attention(Q,K,V) = softmax(QK^T / sqrt(d_k))V.",
    },
    "numeric_table": {
        "page": 9,
        "type": "table",
        "title": "Scores",
        "lines": ["Row A | 12", "Row B | 19", "Row C | 15"],
        "content": "Bảng số liệu: hàng A là 12, hàng B là 19, hàng C là 15; cao nhất là hàng B.",
    },
    "legend_chart": {
        "page": 5,
        "type": "chart",
        "title": "Model comparison",
        "lines": ["Orange = VisualRAG", "Blue = Text-only RAG"],
        "content": "Chú giải biểu đồ: màu cam là VisualRAG; màu xanh là Text-only RAG.",
    },
    "pass_rate_table": {
        "page": 6,
        "type": "table",
        "title": "Evaluation result",
        "lines": ["Common | 7/8", "Hard | 9/14", "Total | 17/24 = 70.8%"],
        "content": "Bảng kết quả minh họa: hàng Tổng là 17/24, tương đương 70.8%.",
    },
    "formula_with_caption": {
        "page": 7,
        "type": "formula",
        "title": "Attention notation",
        "lines": ["d_k = dimension of key vectors", "Scale factor = sqrt(d_k)"],
        "content": "Caption ghi d_k là số chiều của vector key và sqrt(d_k) là hệ số chuẩn hóa.",
    },
    "architecture_diagram": {
        "page": 2,
        "type": "diagram",
        "title": "VisualRAG pipeline",
        "lines": ["OCR", "Chunk & Index", "Retrieve & Rerank", "Generate"],
        "content": "Sau OCR là bước Chunk & Index, rồi Retrieve & Rerank, cuối cùng Generate.",
    },
    "ocr_visual_conflict": {
        "page": 11,
        "type": "table",
        "title": "Original table",
        "lines": ["OCR text: 75%", "Original image: 73%"],
        "content": "OCR ghi 75%, nhưng bảng trong ảnh gốc ghi 73%. Phải nêu rõ mâu thuẫn và ưu tiên ảnh gốc.",
    },
}


TEXT_FIXTURES: dict[str, tuple[int, str]] = {
    "text_overview": (1, "# Mục tiêu\nTài liệu trình bày pipeline VisualRAG cho PDF có cả văn bản và hình ảnh."),
    "text_pipeline": (3, "# Pipeline\nBa bước chính: OCR; Chunking & Indexing; Retrieval & Generation."),
    "text_chunk_limit": (4, "# Chunking\nMỗi chunk có tối đa 1024 token."),
    "embedding_model": (8, "# Embedding\nHệ thống dùng Qwen/Qwen3-Embedding-0.6B."),
}


MULTI_VISUALS = {
    "multiple_visuals_page59": [
        ("chart", "Chart A", ["Revenue | Q1", "Revenue | Q2"]),
        ("table", "Table B", ["Metric | 12", "Metric | 18"]),
        ("diagram", "Diagram C", ["Input", "Output"]),
    ],
    "two_charts": [
        ("chart", "Chart A", ["Series A | 12", "Series B | 15"]),
        ("chart", "Chart B", ["Series A | 20", "Series B | 18"]),
        ("chart", "Chart C", ["Series A | 9", "Series B | 11"]),
    ],
}


def write_fixture(fixture_id: str, elements: list[dict]) -> str:
    document_id = f"cp3-{fixture_id}"
    payload = {"document_id": document_id, "elements": elements}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{fixture_id}.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return document_id


def main() -> None:
    document_map: dict[str, str] = {}

    for fixture_id, item in FIXTURES.items():
        image_path = visual(fixture_id, item["title"], item["lines"])
        document_map[fixture_id] = write_fixture(
            fixture_id,
            [
                {
                    "page": item["page"],
                    "region_order": 1,
                    "region_type": item["type"],
                    "content": item["content"],
                    "saved_link": str(image_path),
                    "original_filename": f"{fixture_id}.pdf",
                    "metadata": {"coordinates": [40, 100, 860, 490]},
                }
            ],
        )

    for fixture_id, (page, content) in TEXT_FIXTURES.items():
        document_map[fixture_id] = write_fixture(
            fixture_id,
            [
                {
                    "page": page,
                    "region_order": 1,
                    "region_type": "text",
                    "content": content,
                    "original_filename": f"{fixture_id}.pdf",
                    "metadata": {"coordinates": [40, 80, 860, 460]},
                }
            ],
        )

    for fixture_id, visuals in MULTI_VISUALS.items():
        elements = []
        for index, (region_type, title, lines) in enumerate(visuals, start=1):
            image_path = visual(f"{fixture_id}-{index}", title, lines)
            elements.append(
                {
                    "page": 59,
                    "region_order": index,
                    "region_type": region_type,
                    "content": f"{title}: " + "; ".join(lines),
                    "saved_link": str(image_path),
                    "original_filename": f"{fixture_id}.pdf",
                    "metadata": {"coordinates": [40, 80 + index * 40, 860, 420]},
                }
            )
        document_map[fixture_id] = write_fixture(fixture_id, elements)

    # These cases intentionally retrieve no evidence.
    document_map["attention_no_formula"] = "cp3-empty-attention"
    document_map["no_deadline"] = "cp3-empty-deadline"
    document_map["blurred_numeric_cell"] = "cp3-empty-blurred-cell"

    (OUT / "document-map.json").write_text(
        json.dumps(document_map, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"Wrote {len(document_map)} fixture mappings to {OUT / 'document-map.json'}")


if __name__ == "__main__":
    main()
