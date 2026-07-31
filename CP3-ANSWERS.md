# Câu trả lời CP3 — VLearn VisualRAG

## 1. AI quyết định điều gì và dùng model nào?

**AI quyết định các đoạn văn và crop hình được truy xuất có đủ bằng chứng để trả
lời câu hỏi hay phải nói không tìm thấy/không chắc chắn — dùng
`gpt-4o-mini`.**

Ghi chú kỹ thuật: DeepSeek-OCR dùng để chuyển PDF thành Markdown và tách vùng
hình; quyết định nêu trên thuộc bước trả lời đa phương thức qua OpenAI Responses
API. Chế độ `demo` trong repo chỉ phục vụ phát triển giao diện, không được tính
là lượt chạy AI thật.

## 2. Tổng số câu trong bộ thử nghiệm

**24 câu.**

File kiểm chứng: `eval/golden_set.jsonl`.

## 3. Bộ câu thử có bao nhiêu kiểu tình huống?

**Đủ 4/4 kiểu**, mỗi kiểu có ít nhất hai câu:

- [x] Không có thông tin trong tài liệu: `GS003`, `GS019`.
- [x] Câu mơ hồ hoặc thiếu ngữ cảnh: `GS004`, `GS006`, `GS010`, `GS020`.
- [x] Yêu cầu sản phẩm không được phép làm: `GS001`, `GS021`, `GS024`.
- [x] Trả lời sai có thể gây hậu quả thật: `GS008`, `GS009`, `GS019`, `GS023`.

## 4. Số câu bắt nguồn từ quan sát thực tế

**10 câu.**

- 8 câu lấy trực tiếp từ chatlog: `GS001`–`GS008`.
- 2 câu phát triển từ tình huống đã xuất hiện trong chatlog: `GS009`–`GS010`.

Nguồn được ghi tại trường `source_ref` và `source_type` của từng dòng trong
`eval/golden_set.jsonl`.

## 5. Kết quả chạy thử lần đầu

**20/24 câu đạt (83,3%).**

Lượt chạy dùng OpenAI `gpt-4o-mini`: routing đúng 24/24, không có lỗi API. Bốn
case fail nội dung là `GS002`, `GS006`, `GS007`, `GS022`. Bảng có đủ cả pass và
fail được giữ tại `eval/results/cp3-openai-first-run.csv`.

## 6. Chuẩn đạt của nhóm

**≥80% câu thử đạt, và AI không được bịa thông tin ngoài tài liệu dù chỉ một
lần.**

Tiêu chí kiểm tra bổ sung đã chốt: citation phải đúng 100%. Không hạ chuẩn sau
khi có kết quả lần chạy đầu.

Kết quả đầu tiên đạt ngưỡng phần trăm 83,3%, nhưng **chưa đạt** điều kiện
không-sai-lần-nào vì `GS002`, `GS006`, `GS007` có diễn giải ngoài source.
