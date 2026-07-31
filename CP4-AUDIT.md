# CP4 — Audit spec gần cuối

## Checklist chính thức

| Yêu cầu | Trạng thái | Bằng chứng |
|---|---|---|
| Evidence chuẩn A và/hoặc B có log | Đạt B | `evidence/mining-results.md`, `evidence/visual-query-quotes.md`, script và manual review |
| Bảng impact ≥3 ứng viên, giữ ứng viên loại | Đạt | `spec.md` §2 |
| 4 lớp chỗ khó cụ thể | Đạt | `spec.md` §5 |
| ≥8 kịch bản, ≥2/lớp | Đạt | `spec.md` §5 có S1–S2, A1–A2, O1–O2, D1–D2 |
| ≥4 HAX/PAIR có vị trí áp dụng | Đạt | `spec.md` §4b: G1, G2, G10, G11, G9 |
| 4 đường đi trải nghiệm | Đạt | `spec.md` §6 |
| Quality bar bằng số | Đạt | ≥80%, citation 100%, lớp nguồn sự thật không claim ngoài source |
| Kết quả đo đầu tiên và phân tích fail | Đạt | 20/24; `eval/results/cp3-openai-first-run-review.md` |
| Prototype khai báo khớp thực tế | Đạt | Working; OpenAI trace thật, 6/6 test, frontend build pass |
| Commit `spec.md` trước hạn cứng | Chưa thể chứng minh | `spec.md` hiện là file chưa commit trong worktree; thời hạn quá khứ không thể tái tạo |

## Kết luận CP4

**Nội dung CP4 đã hoàn chỉnh.** Điều duy nhất không thể tự tạo lại là bằng chứng
timestamp/commit đúng hạn; nhóm cần dùng lịch sử nộp thực tế nếu TA yêu cầu.
