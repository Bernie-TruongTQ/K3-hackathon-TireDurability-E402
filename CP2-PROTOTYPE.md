# CP2 — Prototype bấm được

## Flow chính

1. Mở frontend VLearn VisualRAG.
2. Chọn tài liệu Markdown/PDF và bấm upload.
3. Backend trích xuất/index, trả `document_id`.
4. Chọn provider và nhập câu hỏi.
5. Frontend gọi `/api/v1/chat`.
6. Giao diện hiển thị answer, route, source page/thumbnail và `trace_id`.

Flow hiện tại được cài tại:

- `project/frontend/components/VisualRAGApp.tsx`
- `project/app/routes/index.py`
- `project/app/routes/chat.py`

## Bằng chứng chạy

- Test `test_markdown_upload_to_chat_end_to_end` chứng minh upload → index → chat
  không cần can thiệp giữa chừng.
- Toàn bộ backend: **7/7 test pass**, gồm upload PDF số hóa với text + ảnh nguồn.
- Frontend: production build pass, route `/` prerender thành công.
- Provider `demo` có nhãn `is_mock=true`; UI không trình bày mock như AI thật.
- Repo đã có lịch sử commit; commit gần nhất trước đợt hoàn thiện:
  `0f4fdab run-full`.

Chi tiết lệnh và phạm vi test: `evidence/automated-checks.md`.

## Kiểm tra CP2

- [x] Flow chính bấm đi hết được.
- [x] Mock được gắn nhãn rõ.
- [x] Repo có commit.
- [x] Working slice đã vượt yêu cầu Sketch/Mock của CP2.
