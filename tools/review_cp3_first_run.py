"""Apply the documented manual review to the frozen CP3 first-run CSV."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "eval" / "results" / "cp3-openai-first-run.csv"
SUMMARY = RESULT.with_suffix(".summary.json")
REVIEW_MD = ROOT / "eval" / "results" / "cp3-openai-first-run-review.md"

FAILURES = {
    "GS002": {
        "grounded_pass": "false",
        "usefulness_pass": "true",
        "notes": (
            "FAIL: trả đúng 4 giai đoạn nhưng thêm nhận định ngoài source "
            "('thường được sử dụng...'), vi phạm no_external_claim."
        ),
    },
    "GS006": {
        "grounded_pass": "false",
        "usefulness_pass": "true",
        "notes": (
            "FAIL: đọc đúng bảng nhưng suy đoán các giá trị có thể là chỉ số hiệu "
            "suất; claim này không có trong source."
        ),
    },
    "GS007": {
        "grounded_pass": "false",
        "usefulness_pass": "true",
        "notes": (
            "FAIL: đúng tên 4 bước nhưng tự bổ sung mô tả cho từng bước, vi phạm "
            "source_labels_only."
        ),
    },
    "GS022": {
        "grounded_pass": "true",
        "usefulness_pass": "false",
        "notes": (
            "FAIL: không đoán số nhưng chỉ báo thiếu căn cứ; chưa hiển thị crop và "
            "chưa nói rõ ảnh quá mờ theo expected behavior."
        ),
    },
}


def main() -> None:
    if not RESULT.exists():
        raise SystemExit(f"Missing frozen first-run file: {RESULT}")
    with RESULT.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
        fields = list(rows[0].keys())

    for row in rows:
        failure = FAILURES.get(row["case_id"])
        if failure:
            row.update(failure)
            row["overall_pass"] = "false"
        else:
            row["grounded_pass"] = "true"
            row["usefulness_pass"] = "true"
            row["overall_pass"] = str(
                row["routing_pass"] == "true" and row["citation_pass"] == "true"
            ).lower()
            row["notes"] = "PASS: đáp ứng expected behavior và hard constraints."
        row["reviewer"] = "Codex-assisted strict review"

    with RESULT.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    passed = sum(row["overall_pass"] == "true" for row in rows)
    total = len(rows)
    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
    summary.update(
        {
            "semantic_score": passed,
            "overall_pass": passed,
            "overall_total": total,
            "overall_rate": round(passed / total, 4),
            "quality_bar_percentage_met": passed / total >= 0.8,
            "zero_external_claim_failures_met": False,
            "failed_cases": list(FAILURES),
            "reviewer": "Codex-assisted strict review",
            "note": (
                "Strict review completed against expected_behavior and "
                "hard_constraints; first-run answers remain unchanged."
            ),
        }
    )
    SUMMARY.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    lines = [
        "# CP3 first-run review",
        "",
        f"- Provider/model: OpenAI / `gpt-4o-mini`",
        f"- Kết quả: **{passed}/{total} ({passed / total:.1%})**",
        "- Routing: **24/24**",
        "- API errors: **0**",
        "- Ngưỡng ≥80%: **đạt**",
        "- Điều kiện 0 claim ngoài source: **chưa đạt**",
        "",
        "| Case | Kết quả | Ghi chú |",
        "|---|---|---|",
    ]
    for row in rows:
        result = "PASS" if row["overall_pass"] == "true" else "FAIL"
        note = row["notes"].replace("|", "\\|")
        lines.append(f"| {row['case_id']} | {result} | {note} |")
    REVIEW_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Reviewed {total} cases: {passed}/{total} pass")
    print(f"Wrote {REVIEW_MD}")


if __name__ == "__main__":
    main()
