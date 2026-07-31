"""Fail-fast audit of artifacts required by the hackathon rubric."""

from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLACEHOLDER_RE = re.compile(r"\[CẦN|REPLACE_|NOT_RUN", re.I)


def check(condition: bool, label: str, failures: list[str]) -> None:
    print(("PASS" if condition else "FAIL"), "-", label)
    if not condition:
        failures.append(label)


def main() -> int:
    failures: list[str] = []
    required = [
        "README.md",
        "spec.md",
        "eval/golden_set.jsonl",
        "validation/feedback-log.csv",
        "demo/demo-script.md",
    ]
    for relative in required:
        check((ROOT / relative).exists(), f"required file: {relative}", failures)

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    spec = (ROOT / "spec.md").read_text(encoding="utf-8")
    check(not PLACEHOLDER_RE.search(readme), "README has no unresolved people placeholders", failures)
    check("[CẦN TÊN]" not in spec and "[CẦN 3 TÊN THẬT]" not in spec, "spec has team and willing-user names", failures)

    rows = [
        json.loads(line)
        for line in (ROOT / "eval/golden_set.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    check(len(rows) >= 20, "golden set has at least 20 cases", failures)
    check(
        sum(item["source_type"] in {"chatlog", "chatlog-derived"} for item in rows) >= 10,
        "golden set has at least 10 chatlog-derived cases",
        failures,
    )
    for error_class in ("source_truth", "ambiguity", "out_of_scope", "domain"):
        check(
            sum(item["difficulty_class"] == error_class for item in rows) >= 2,
            f"golden set covers {error_class} with >=2 cases",
            failures,
        )

    feedback_path = ROOT / "validation/feedback-log.csv"
    with feedback_path.open(encoding="utf-8-sig", newline="") as handle:
        feedback = [
            row
            for row in csv.DictReader(handle)
            if row.get("tester_name") and "[CẦN" not in row["tester_name"]
        ]
    check(len(feedback) >= 5, "validation has >=5 real feedback rows", failures)
    check(len({row["tester_name"] for row in feedback}) >= 5, "validation has >=5 distinct testers", failures)

    reflections = [
        path
        for path in (ROOT / "reflection").glob("*.md")
        if path.name.upper() != "TEMPLATE.MD"
    ]
    check(bool(reflections), "at least one completed reflection exists", failures)

    result_files = [path for path in (ROOT / "eval/results").glob("*.csv")]
    reviewed_rows = []
    real_ai_rows = []
    for path in result_files:
        with path.open(encoding="utf-8-sig", newline="") as handle:
            for row in csv.DictReader(handle):
                if row.get("overall_pass", "").lower() in {"true", "false"}:
                    reviewed_rows.append(row)
                if row.get("provider") in {"openai", "gemini", "qwen"} and row.get("trace_id"):
                    real_ai_rows.append(row)
    check(len(reviewed_rows) >= len(rows), "full golden set has reviewed results", failures)
    check(bool(real_ai_rows), "at least one real-AI trace is recorded in eval results", failures)

    deck_pdf = ROOT / "demo-slides.pdf"
    check(deck_pdf.exists(), "demo-slides.pdf exists", failures)
    if deck_pdf.exists():
        try:
            from pypdf import PdfReader

            check(len(PdfReader(str(deck_pdf)).pages) == 6, "demo-slides.pdf has exactly 6 pages", failures)
        except ImportError:
            check(False, "pypdf installed to verify slide page count", failures)

    if failures:
        print(f"\nSubmission audit: {len(failures)} blocker(s).")
        return 1
    print("\nSubmission audit: all automated gates pass.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
