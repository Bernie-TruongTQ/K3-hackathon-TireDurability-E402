# Reflection — Nguyễn Ngọc Ánh

- **Mã học viên:** 2A202601643
- **Vai trò:** Validation và slide
- **Phần tôi trực tiếp làm:**
  - Chuẩn bị kế hoạch validation, task cho người thử và bộ câu hỏi phỏng vấn sau khi quan sát.
  - Tổng hợp phản hồi của 5 tester, phân loại mức độ nghiêm trọng và chuyển insight thành các mục trong changelog.
  - Xây dựng slide thuyết trình, trực quan hóa problem, luồng sản phẩm, kết quả eval và bài học từ case fail.
  - Phối hợp dry run, bấm giờ và điều chỉnh nội dung để mỗi thành viên có phần trình bày rõ ràng.

- **AI đã hỗ trợ tôi ở đâu:**
  - Hỗ trợ nhóm các quan sát và trích dẫn của tester thành theme mà không làm mất dữ liệu gốc.
  - Gợi ý cấu trúc slide 6 trang, cách rút gọn câu chữ và cách thể hiện tỷ lệ pass 20/24.
  - Hỗ trợ soạn kịch bản demo, câu chuyển ý và danh sách câu hỏi Q&A có thể gặp.

- **Phần nào tôi đã tự kiểm tra/giải thích được:**
  - Sự khác nhau giữa quan sát hành vi, lời người dùng nói và suy luận của nhóm.
  - Cách ưu tiên thay đổi theo severity và mức ảnh hưởng tới trust, thay vì chỉ đếm số lần phản hồi xuất hiện.
  - Ý nghĩa của kết quả 20/24: đạt ngưỡng tổng thể nhưng chưa đạt đầy đủ ràng buộc không sinh claim ngoài nguồn.

- **Một case fail của nhóm:**
  - Trong validation, một câu trả lời suy diễn ngoài nguồn vẫn được trình bày khá tự tin; ngoài ra thông báo từ chối ở case thiếu căn cứ chưa chỉ cho người dùng bước tiếp theo.

- **Nguyên nhân:**
  - Nhóm tập trung nhiều vào tỷ lệ pass tổng và happy path, chưa kiểm tra đủ cảm giác tin cậy cũng như khả năng phục hồi của người dùng khi AI không chắc chắn.

- **Tôi đã học được gì từ case fail đó:**
  - Validation không chỉ xác nhận sản phẩm “chạy được”. Nó phải tìm ra nơi người dùng có thể hiểu sai mức độ chắc chắn của AI và xem họ có tự phục hồi được sau lỗi hay không.

- **Nếu làm lại, tôi sẽ đổi gì:**
  - Bổ sung task riêng cho hallucination, abstain và correction path ngay từ vòng test đầu.
  - Chuẩn hóa feedback log trước khi test, ghi rõ evidence, severity, quyết định thay đổi và người phụ trách để việc tổng hợp slide nhanh và có thể kiểm chứng hơn.
