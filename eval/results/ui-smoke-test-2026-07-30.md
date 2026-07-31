# UI smoke test — 2026-07-30

Nguồn: nhóm tự dùng thử giao diện với `CP1-CANVAS.md`, provider OpenAI
`gpt-4o-mini`. Đây là evidence kỹ thuật/self-test, không được tính là external
validation CP5.

| # | Tình huống | Trace ID | Route thực tế | Kết quả hành vi | Chấm nghiêm ngặt |
|---|---|---|---|---|---|
| 1 | Hỏi đối tượng người dùng và công việc | `3b25e25c8ca047c8b0ffbe41d4ec7006` | `text` | Trả lời đúng, có `[S1]` | PASS |
| 2 | Hỏi số liệu evidence | `407e1bdb94b2497ab424dc939dbd3bbe` | `text` | Đúng 369 user, 585 conversation, 8 visual queries | PASS |
| 3 | Hỏi quyết định AI | `b1cb4db8d4aa4149b0ee16ba8916941a` | `text` | Đúng logic answer / clarify / abstain, có `[S1]` | PASS |
| 4 | Hỏi deadline không có trong nguồn | `ed55702675114a5694fb3a674dddc8b9` | `text` | Không bịa; nói rõ tài liệu không đề cập | FAIL route |
| 5 | Hỏi hình khoanh đỏ khi không có crop | `e6131786c88848cfa68eff85921b3829` | `clarify` | Yêu cầu chọn trang/thumbnail, không đoán | PASS |

## Tổng kết

- Đúng hành vi: **5/5**.
- Chấm nghiêm ngặt cả route: **4/5 = 80%**.
- Critical “không bịa ngoài source”: **0 lỗi**.
- Lỗi cần sửa: câu trả lời đã abstain đúng về nội dung nhưng metadata vẫn là
  `route=text`. Nguyên nhân là route hiện được gán trước khi model sinh câu trả
  lời; chưa có bước hậu kiểm chuyển sang `abstain`.
- Lưu ý thao tác: source trang 1 đang được khóa trong cả năm lượt thử.
