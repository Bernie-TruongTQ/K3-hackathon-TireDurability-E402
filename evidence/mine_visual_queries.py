"""Reproducible mining for VisualRAG evidence.

Only reads the anonymized hackathon data pack. It never writes raw messages to
the public submission. The generated summary uses anonymized turn IDs.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import defaultdict
from pathlib import Path


EXPLICIT_VISUAL_PATTERNS = [
    re.compile(r"\b(giải thích|phân tích|tóm tắt).{0,80}\b(hình ảnh|hình biểu diễn|biểu đồ|bảng được khoanh)\b", re.I),
    re.compile(r"\b(người trong ảnh|ảnh được khoanh|hình được khoanh)\b", re.I),
    re.compile(r"\b(công thức attention|công thức toán học của attention)\b", re.I),
]


def is_explicit_visual_query(text: str) -> bool:
    normalized = " ".join(text.split())
    return any(pattern.search(normalized) for pattern in EXPLICIT_VISUAL_PATTERNS)


def citation_is_empty(value: str | None) -> bool:
    return (value or "").strip() in {"", "[]", "null", "None"}


def mine(csv_path: Path) -> dict:
    with csv_path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))

    by_turn: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        by_turn[row["turn_id"]].append(row)

    students = [row for row in rows if row["role"] == "student"]
    tutors = [row for row in rows if row["role"] == "tutor"]
    hits = [row for row in students if is_explicit_visual_query(row.get("content", ""))]

    cases = []
    for student in hits:
        tutor_rows = [row for row in by_turn[student["turn_id"]] if row["role"] == "tutor"]
        tutor = tutor_rows[0] if tutor_rows else {}
        cases.append(
            {
                "conversation_id": student["conversation_id"],
                "turn_id": student["turn_id"],
                "user_id": student["user_id"],
                "student_query_preview": " ".join(student["content"].split())[:240],
                "tutor_response_preview": " ".join(tutor.get("content", "").split())[:320],
                "citations_empty": citation_is_empty(tutor.get("citations")),
                "rating": tutor.get("rating") or None,
            }
        )

    empty_citations = sum(citation_is_empty(row.get("citations")) for row in tutors)
    return {
        "method": "explicit_visual_patterns_v1_plus_manual_review",
        "total_rows": len(rows),
        "student_turns": len(students),
        "tutor_turns": len(tutors),
        "users": len({row["user_id"] for row in rows}),
        "conversations": len({row["conversation_id"] for row in rows}),
        "explicit_visual_hits": len(hits),
        "explicit_visual_users": len({row["user_id"] for row in hits}),
        "explicit_visual_conversations": len({row["conversation_id"] for row in hits}),
        "tutor_empty_citations": empty_citations,
        "tutor_empty_citations_rate": round(empty_citations / len(tutors), 4),
        "cases": cases,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    summary = mine(args.input)
    rendered = json.dumps(summary, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)


if __name__ == "__main__":
    main()

