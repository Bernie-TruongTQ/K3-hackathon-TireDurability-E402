# CP5 — Kế hoạch test với 5 người dùng thật

## Nguyên tắc

- Mỗi phiên khoảng 10 phút.
- Tester tự thao tác; người quan sát không hướng dẫn hoặc gợi ý câu lệnh.
- Dùng cùng một bản prototype và cùng file `demo-slides.pdf`.
- Ghi nguyên văn lời tester, không sửa câu chữ và không tự điền thay.
- Mỗi tester chỉ được tính một dòng trong `validation/feedback-log.csv`.

## Chuẩn bị kỹ thuật

1. Chạy backend tại `http://localhost:1201`.
2. Chạy frontend tại `http://localhost:3000`.
3. Mở app và xác nhận provider là `OpenAI GPT-4o mini`.
4. Đặt `demo-slides.pdf` ở vị trí tester có thể chọn.
5. Xóa trạng thái/source đang khóa từ phiên trước hoặc tải lại trang.
6. Không cho tester xem phần “Kết quả mong đợi” khi đang làm task.

## Danh sách và task

| # | Tester | Mã sinh viên | Willing user CP1 | Task giao nguyên văn |
|---|---|---|---|---|
| 1 | Vũ Đức Duy | 2A202601023 | yes | “Hãy dùng công cụ để tìm xem lần chạy thử đạt bao nhiêu câu và kiểm chứng thông tin đó từ tài liệu.” |
| 2 | Nguyễn Đình Bình | 2A202601091 | yes | “Hãy dùng công cụ để hiểu pipeline xử lý PDF từ đầu vào đến câu trả lời.” |
| 3 | Nguyễn Mạnh Cường | 2A202601061 | yes | “Hãy dùng công cụ để tìm hiểu vì sao nhóm chọn Visual Q&A thay vì hai phương án còn lại.” |
| 4 | Hoàng Thị Trà My | 2A202601290 | no | “Hãy hỏi công cụ một thông tin không có trong tài liệu và đánh giá xem nó có tự đoán hay không.” |
| 5 | Cao Hữu Phúc | 2A202601283 | no | “Hãy dùng công cụ để tìm các trường hợp bị fail trong lần chạy đầu và giải thích nguyên nhân.” |

Phiên của Cao Hữu Phúc do **Nguyễn Quốc Anh** phụ trách quan sát và ghi log.

## Ba câu hỏi bắt buộc sau task

Hỏi đúng ba câu sau và ghi nguyên văn:

1. “Điều gì khó hiểu hoặc khó chịu nhất?”
2. “Kết quả này bạn có tin không? Vì sao?”
3. “Bạn có dùng công cụ này thật không? Vì sao hoặc vì sao chưa?”

## Người quan sát cần ghi gì

- Tester bấm gì đầu tiên.
- Có hiểu phải upload/index trước khi chat không.
- Có nhận ra source card có thể bấm và khóa nguồn không.
- Có hiểu số trang, citation, route và trace ID không.
- Tester bị kẹt ở đâu; có cần trợ giúp kỹ thuật không.
- Task hoàn thành, hoàn thành một phần hay thất bại.
- Một hoặc nhiều quote nguyên văn.
- Mức nghiêm trọng: `low`, `medium` hoặc `high`.
- Quyết định: sửa trước demo, giữ nguyên có lý do, hoặc đưa backlog.

## Điều kiện đạt CP5

- Có đủ 5 phiên từ 5 tester khác nhau.
- Có ít nhất 2 willing users CP1; kế hoạch này có 3.
- Mỗi dòng có tên/vai, task, observation, quote và severity.
- Có ít nhất một thay đổi hoặc quyết định giữ nguyên dựa trên feedback thật.
- Cập nhật `spec.md` §9 và slide 5 sau khi tổng hợp.
- Dry run 5 phút sau khi sửa.

