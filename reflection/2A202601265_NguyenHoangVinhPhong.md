# Reflection — Nguyễn Hoàng Vĩnh Phong

- **Mã học viên:** 2A202601265
- **Vai trò:** UI Retrieval, VLM và Evaluation
- **Phần tôi trực tiếp làm:**
  - Hoàn thiện luồng retrieval và reranking để chọn ngữ cảnh liên quan trước khi sinh câu trả lời.
  - Thiết kế logic phân tuyến giữa câu hỏi dựa trên văn bản và câu hỏi cần phân tích vùng ảnh bằng VLM.
  - Xây dựng và chạy golden set cho các nhóm tình huống: happy path, thiếu nguồn, mơ hồ, ngoài phạm vi và correction; đối chiếu routing, citation và usefulness.
  - Phối hợp đưa source card, trang và vùng ảnh vào giao diện để người dùng kiểm chứng câu trả lời.

- **AI đã hỗ trợ tôi ở đâu:**
  - Hỗ trợ viết prompt cho retrieval/reranking, visual routing và câu trả lời chỉ dựa trên nguồn.
  - Gợi ý cấu trúc golden set, tiêu chí chấm và cách phân tích các case fail.
  - Hỗ trợ refactor code tích hợp model và chuẩn hóa dữ liệu trả về cho UI.

- **Phần nào tôi đã tự kiểm tra/giải thích được:**
  - Luồng retrieve → rerank → route → generate và lý do không gọi VLM cho mọi câu hỏi.
  - Cách metadata trang, heading, tọa độ và image ID giúp truy đúng vùng nguồn.
  - Cách đọc kết quả eval 20/24, xác định case fail và phân biệt routing đúng với câu trả lời thực sự grounded.

- **Một case fail của nhóm:**
  - Trong lần chạy đầu, các case `GS002`, `GS006` và `GS007` vẫn sinh chi tiết không có trong nguồn dù hệ thống đã retrieve được tài liệu liên quan.

- **Nguyên nhân:**
  - Prompt cho phép mô hình tổng hợp quá rộng và chưa có bước hậu kiểm claim theo source; retrieval đúng không tự động bảo đảm generation không suy diễn.

- **Tôi đã học được gì từ case fail đó:**
  - Chất lượng RAG phải được kiểm tra ở từng tầng. Retrieval score tốt chỉ chứng minh đã lấy được ngữ cảnh; groundedness và citation correctness vẫn cần constraint và phép đo riêng.

- **Nếu làm lại, tôi sẽ đổi gì:**
  - Thêm source-only post-check, ngưỡng confidence và cơ chế abstain trước khi trả câu trả lời.
  - Lưu trace của retrieved chunks, routing decision và VLM input cho từng test case để việc debug có thể tái lập.
