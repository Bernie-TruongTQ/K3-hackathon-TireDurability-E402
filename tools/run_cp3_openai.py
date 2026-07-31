"""Run and freeze the CP3 24-case first run with OpenAI gpt-4o-mini.

This runner uses the same chunker, store, routing, reranker and generator as the
API. It writes every case, including errors and failures. Semantic review fields
remain blank until answers are reviewed against expected_behavior.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import runpy
import sys
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv


ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "project"
DEFAULT_OUTPUT = ROOT / "eval" / "results" / "cp3-openai-first-run.csv"
FIELDS = [
    "run_id",
    "case_id",
    "provider",
    "model",
    "route",
    "expected_route",
    "answer",
    "sources",
    "routing_pass",
    "citation_pass",
    "grounded_pass",
    "usefulness_pass",
    "overall_pass",
    "reviewer",
    "trace_id",
    "notes",
]


def ensure_configuration() -> None:
    env_path = PROJECT / ".env"
    if not env_path.exists():
        raise SystemExit(
            "Thiếu project/.env. Sao chép project/.env.example thành project/.env "
            "và điền VISUALRAG_OPENAI_API_KEY."
        )
    load_dotenv(env_path, override=False)
    key = os.getenv("VISUALRAG_OPENAI_API_KEY", "")
    if not key or "YOUR_OPENAI" in key:
        raise SystemExit(
            "VISUALRAG_OPENAI_API_KEY chưa được điền trong project/.env. "
            "Không dán key vào chat hoặc commit vào git."
        )
    os.environ.setdefault("VISUALRAG_LLM_PROVIDER", "openai")
    os.environ.setdefault("VISUALRAG_OPENAI_MODEL", "gpt-4o-mini")


def build_fixtures_if_needed() -> Path:
    document_map = ROOT / "eval" / "fixtures" / "generated" / "document-map.json"
    if not document_map.exists():
        runpy.run_path(
            str(ROOT / "eval" / "fixtures" / "build_demo_corpus.py"),
            run_name="__main__",
        )
    return document_map


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--allow-overwrite",
        action="store_true",
        help="Only use for a deliberately separate rerun, never to rewrite first-run evidence.",
    )
    args = parser.parse_args()

    output = args.output.resolve()
    if output.exists() and not args.allow_overwrite:
        raise SystemExit(
            f"{output} đã tồn tại. First run phải được giữ nguyên; "
            "hãy chọn --output khác cho lần chạy sau."
        )

    ensure_configuration()
    document_map_path = build_fixtures_if_needed()
    sys.path.insert(0, str(PROJECT))

    from app.core.config import settings
    from app.services.indexing_service import (
        HierarchicalMarkdownChunker,
        IndexingService,
        LocalDocumentStore,
    )
    from app.services.rag_service import (
        LexicalReranker,
        RAGService,
        create_generator,
    )

    cases = [
        json.loads(line)
        for line in (ROOT / "eval" / "golden_set.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
        if line.strip()
    ]
    document_map = json.loads(document_map_path.read_text(encoding="utf-8"))

    output.parent.mkdir(parents=True, exist_ok=True)
    store_path = output.with_suffix(".store.json")
    store = LocalDocumentStore(store_path)
    indexer = IndexingService(HierarchicalMarkdownChunker(), store)
    for fixture_path in sorted(document_map_path.parent.glob("*.json")):
        if fixture_path.name != "document-map.json":
            indexer.index_from_json(str(fixture_path))

    generator = create_generator("openai")
    service = RAGService(store, LexicalReranker(), generator)
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    rows = []

    for case in cases:
        document_id = document_map.get(case["fixture_id"])
        try:
            result = service.query(
                case["query"],
                document_id=document_id,
                selected_page=case.get("selected_page"),
            )
            sources = [
                {
                    "source_id": item.metadata.get("source_id"),
                    "filename": item.metadata.get("filename"),
                    "page": item.metadata.get("page"),
                    "region_type": item.metadata.get("region_type"),
                    "score": item.score,
                }
                for item in result.sources
            ]
            citation_required = case["expected_route"] in {"text", "visual"}
            rows.append(
                {
                    "run_id": run_id,
                    "case_id": case["id"],
                    "provider": "openai",
                    "model": settings.OPENAI_MODEL,
                    "route": result.route,
                    "expected_route": case["expected_route"],
                    "answer": result.answer,
                    "sources": json.dumps(sources, ensure_ascii=False),
                    "routing_pass": str(result.route == case["expected_route"]).lower(),
                    "citation_pass": str(bool(sources) if citation_required else True).lower(),
                    "grounded_pass": "",
                    "usefulness_pass": "",
                    "overall_pass": "",
                    "reviewer": "",
                    "trace_id": result.trace_id,
                    "notes": "",
                }
            )
            print(f"{case['id']}: {result.route} (expected {case['expected_route']})")
        except Exception as exc:
            rows.append(
                {
                    "run_id": run_id,
                    "case_id": case["id"],
                    "provider": "openai",
                    "model": settings.OPENAI_MODEL,
                    "route": "ERROR",
                    "expected_route": case["expected_route"],
                    "answer": "",
                    "sources": "[]",
                    "routing_pass": "false",
                    "citation_pass": "false",
                    "grounded_pass": "",
                    "usefulness_pass": "",
                    "overall_pass": "",
                    "reviewer": "",
                    "trace_id": "",
                    "notes": f"{type(exc).__name__}: {exc}",
                }
            )
            print(f"{case['id']}: ERROR {type(exc).__name__}")

    with output.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    route_pass = sum(row["routing_pass"] == "true" for row in rows)
    errors = sum(row["route"] == "ERROR" for row in rows)
    summary = {
        "run_id": run_id,
        "provider": "openai",
        "model": settings.OPENAI_MODEL,
        "total": len(rows),
        "route_pass": route_pass,
        "errors": errors,
        "semantic_score": None,
        "note": "Review grounded/usefulness/overall fields before reporting x/24.",
    }
    output.with_suffix(".summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"Wrote {len(rows)} cases to {output}")
    print(f"Mechanical route pass: {route_pass}/{len(rows)}; errors: {errors}")


if __name__ == "__main__":
    main()
