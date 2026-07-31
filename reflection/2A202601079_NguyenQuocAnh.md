# Reflection — Nguyễn Quốc Anh

- **Mã học viên:** 2A202601079
- **Vai trò:** Backend OCR & Indexing
- **Phần tôi trực tiếp làm:**
  - Xây dựng pipeline OCR sử dụng DeepSeek-OCR để trích xuất cấu trúc tài liệu và vùng ảnh.
  - Phát triển pipeline Indexing với hierarchical chunking, lưu metadata (page, heading, coordinates, image path) và tích hợp Local Store/Chroma phục vụ hệ thống RAG.

- **AI đã hỗ trợ tôi ở đâu:**
  - Hỗ trợ viết và hoàn thiện code cho hierarchical chunking, chunking và indexing với vector database (Chroma).
  - Chuẩn hóa đầu vào/đầu ra giữa các API và tích hợp DeepSeek-OCR.
  - Gợi ý tổ chức lại mã nguồn để dễ debug và kết nối các thành phần trong pipeline OCR → Indexing → Retrieval.

- **Phần nào tôi đã tự kiểm tra/giải thích được:**
  - Thiết kế và kiểm tra pipeline OCR.
  - Chiến lược hierarchical chunking.

- **Một case fail của nhóm:**
  - Ban đầu hệ thống chia tài liệu theo kích thước văn bản nên nhiều chunk mất ngữ cảnh, làm giảm chất lượng truy xuất.

- **Nguyên nhân:**
  - Chưa bảo toàn cấu trúc tài liệu và thiếu metadata (heading, page, coordinates) trong quá trình indexing.

- **Tôi đã học được gì từ case fail đó:**
  - Chất lượng Retrieval phụ thuộc rất lớn vào bước Indexing; việc bảo toàn ngữ cảnh và metadata quan trọng hơn chỉ chia nhỏ văn bản.

- **Nếu làm lại, tôi sẽ đổi gì:**
  - Tích hợp thêm mô hình VLM để mô tả các vùng ảnh đã crop và chèn mô tả vào phần tham chiếu hình ảnh.
  - Thử nghiệm các mô hình OCR nhẹ hơn DeepSeek-OCR để giảm chi phí tính toán và tăng tốc độ xử lý.
