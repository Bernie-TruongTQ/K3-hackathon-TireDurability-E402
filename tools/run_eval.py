"""Run the golden set against a live VisualRAG API.

This script never invents a semantic score. It fills mechanical route/citation
checks and leaves grounded/usefulness review for named human reviewers.
"""

from __future__ import annotations

import argparse
import csv
import json
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


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


def post_json(url: str, payload: dict) -> dict:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=180) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code}: {detail}") from exc


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--golden-set", type=Path, default=Path("eval/golden_set.jsonl"))
    parser.add_argument("--document-map", type=Path, required=True)
    parser.add_argument("--api-base", default="http://localhost:1201")
    parser.add_argument(
        "--provider",
        choices=["demo", "qwen", "gemini", "openai"],
        required=True,
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    cases = [
        json.loads(line)
        for line in args.golden_set.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    document_map = json.loads(args.document_map.read_text(encoding="utf-8"))
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    rows = []

    for case in cases:
        document_id = document_map.get(case["fixture_id"])
        if not document_id and case["expected_route"] not in {"refuse", "clarify"}:
            rows.append(
                {
                    "run_id": run_id,
                    "case_id": case["id"],
                    "provider": args.provider,
                    "model": "",
                    "route": "NOT_RUN",
                    "expected_route": case["expected_route"],
                    "notes": f"Missing document_id for fixture {case['fixture_id']}",
                }
            )
            continue

        payload = {
            "query": case["query"],
            "llm_provider": args.provider,
            "document_id": document_id,
            "selected_page": case.get("selected_page"),
        }
        try:
            result = post_json(f"{args.api_base.rstrip('/')}/api/v1/chat", payload)
            route = result["route"]
            sources = result.get("sources", [])
            citation_required = case["expected_route"] in {"text", "visual"}
            rows.append(
                {
                    "run_id": run_id,
                    "case_id": case["id"],
                    "provider": args.provider,
                    "model": result.get("model", ""),
                    "route": route,
                    "expected_route": case["expected_route"],
                    "answer": result.get("answer", ""),
                    "sources": json.dumps(sources, ensure_ascii=False),
                    "routing_pass": str(route == case["expected_route"]).lower(),
                    "citation_pass": str(bool(sources) if citation_required else True).lower(),
                    "grounded_pass": "",
                    "usefulness_pass": "",
                    "overall_pass": "",
                    "reviewer": "",
                    "trace_id": result.get("trace_id", ""),
                    "notes": "MOCK_PROVIDER" if result.get("is_mock") else "",
                }
            )
        except Exception as exc:
            rows.append(
                {
                    "run_id": run_id,
                    "case_id": case["id"],
                    "provider": args.provider,
                    "model": "",
                    "route": "ERROR",
                    "expected_route": case["expected_route"],
                    "notes": str(exc),
                }
            )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} cases to {args.output}")


if __name__ == "__main__":
    main()
