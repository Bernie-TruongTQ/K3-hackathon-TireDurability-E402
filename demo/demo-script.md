# Demo script CP6 — 5 phút

## Chuẩn bị

- Tài liệu demo chỉ dùng data pack hoặc PDF giả tự sinh.
- Precompute OCR để tránh chờ GPU; lời gọi ở quyết định trung tâm vẫn phải là AI thật.
- Mở sẵn app, log trace và bản backup video/screenshot.

## 0:00–0:45 — User & Job

- Một học viên đang ôn slide có hình/bảng/công thức.
- Nêu evidence: 8 lượt explicit theo mining bảo thủ; case `T0135` bị downvote.

## 0:45–1:30 — Vì sao chọn

- So sánh ba ứng viên: visual understanding, citation gap, latency.
- Chọn visual understanding vì cost-of-error cao và có nền kỹ thuật sẵn.

## 1:30–3:30 — Demo live

### Case chuẩn

1. Chọn tài liệu demo đã index.
2. Hỏi một câu text.
3. Chỉ ra câu trả lời, page citation và mode `text`.

### Case khó

1. Hỏi về một biểu đồ/bảng/công thức.
2. Chỉ ra visual routing và crop ảnh được gửi cho VLM.
3. Chỉ ra citation filename/page/region.
4. Hỏi một câu không có căn cứ để demo graceful failure.

## 3:30–4:15 — Kết quả đo

- Nêu quality bar cố định: ≥80%, citation correctness 100%, source-truth safety 100%.
- Nêu kết quả lượt cuối và failure đáng kể nhất từ `eval/results/`.

## 4:15–5:00 — User thật & tuần tiếp theo

- Đọc hai quote có tên/vai từ validation.
- Nêu thay đổi đã làm từ feedback.
- Hai ưu tiên tiếp theo phải trỏ về failure/feedback.

## Q&A

- Chuẩn bị một tài liệu/case lạ theo thẻ giám khảo.
- Mỗi thành viên nói ít nhất một phần.

