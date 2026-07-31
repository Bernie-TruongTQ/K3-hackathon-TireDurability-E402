# Reflection — Trương Quốc Trường

- **Mã học viên:** 2A202601195
- **Vai trò:** Frontend và demo
- **Phần tôi trực tiếp làm:**
  - Xây dựng giao diện web cho luồng hội thoại, sidebar, composer, trạng thái chờ và lịch sử trao đổi.
  - Thiết kế trải nghiệm hiển thị câu trả lời cùng source card để người dùng thấy trang và nguồn liên quan.
  - Chuẩn bị luồng demo 5 phút, gồm happy path, case lỗi live và correction path khi người dùng chọn lại nguồn.
  - Phối hợp kết nối dữ liệu từ backend với các trạng thái loading, success, empty và error trên frontend.

- **AI đã hỗ trợ tôi ở đâu:**
  - Hỗ trợ tạo khung component React/Next.js và gợi ý cách tách các thành phần giao diện.
  - Gợi ý nội dung microcopy cho trạng thái loading, từ chối và hướng dẫn người dùng sửa nguồn.
  - Hỗ trợ rà soát responsive layout, accessibility cơ bản và kịch bản trình diễn theo thời lượng.

- **Phần nào tôi đã tự kiểm tra/giải thích được:**
  - Luồng state từ lúc người dùng gửi câu hỏi đến khi nhận answer, citation và source image.
  - Cách source card trở thành correction control: người dùng chọn nguồn rồi gửi lại `selected_page`/`selected_image_id`.
  - Cách xử lý các trạng thái lỗi để demo không che giấu giới hạn của AI.

- **Một case fail của nhóm:**
  - Ở một bản demo sớm, câu trả lời có citation nhưng crop hình nguồn chưa tự hiện, nên người dùng vẫn phải thao tác thêm mới kiểm chứng được phần giải thích.

- **Nguyên nhân:**
  - Giao diện ưu tiên phần chat và coi source là nội dung phụ; contract dữ liệu giữa backend và frontend cũng chưa thống nhất đầy đủ cho image ID và vùng crop.

- **Tôi đã học được gì từ case fail đó:**
  - Với sản phẩm VisualRAG, evidence không phải chi tiết trang trí. Hình nguồn phải xuất hiện đúng lúc, cạnh claim mà nó hỗ trợ, nếu không giá trị “có căn cứ” chưa được thể hiện.

- **Nếu làm lại, tôi sẽ đổi gì:**
  - Chốt API contract và các UI state bằng một fixture hoàn chỉnh trước khi phát triển component.
  - Thiết kế source-first từ đầu: tự mở crop quan trọng nhất, làm rõ trạng thái đã chọn và cho phép correction bằng một thao tác.
