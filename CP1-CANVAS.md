# CP1 — Canvas 7 dòng · VLearn VisualRAG

> Artifact này chỉ sử dụng evidence của nhóm. File slide HUST trong `project/`
> là tài liệu kiến trúc tham khảo, không phải bằng chứng hay kết quả của nhóm.

1. **Hướng:** A — VLearn; tính năng mới hỗ trợ hỏi đáp tài liệu PDF có nội dung
   trực quan.
2. **Job executor:** học viên VLearn đang ôn một bài học từ slide PDF có hình,
   bảng, sơ đồ hoặc công thức.
3. **Pain một câu:** khi cần hiểu nội dung trực quan trong slide, học viên không
   nhận được lời giải thích có căn cứ nên phải tự mô tả lại, chuyển công cụ hoặc
   bỏ qua, làm tăng nguy cơ học sai.
4. **Evidence ban đầu:** mining 1.261 cặp hỏi–đáp của 369 user/585 conversation
   tìm được 8 truy vấn visual explicit; ít nhất 4/8 không được xử lý nội dung
   visual, 5/8 thiếu citation và `T0135` có rating `down`. Có 8 quote nguyên văn
   tại `evidence/visual-query-quotes.md`.
5. **Lát cắt một câu:** với học viên VLearn đang ôn slide PDF, khi họ hỏi về một
   hình, bảng hoặc công thức, hệ thống quyết định evidence text + crop hình có đủ
   để trả lời hay phải hỏi lại/từ chối, nhằm trả lời có căn cứ kèm trang và hình
   nguồn.
6. **Automation:** conditional — hệ thống tự trả lời khi có evidence; thiếu
   trang/vùng hình thì hỏi lại, thiếu căn cứ thì abstain, vì giải thích sai có
   thể khiến học viên học sai mà khó tự phát hiện.
7. **Willing users và phân công:** Vũ Đức Duy (`2A202601023`), Nguyễn Đình
   Bình (`2A202601091`) và Nguyễn Mạnh Cường (`2A202601061`) đồng ý thử.
   Đội **TireDurability** gồm Đào Văn Đà — hợp nhất code/báo cáo; Nguyễn Quốc
   Anh — System Prompt/báo cáo; Nguyễn Hoàng Vĩnh Phong — UI; Trương Quốc
   Trường — eval/viết bảng; Nguyễn Ngọc Ánh — báo cáo.

## Kiểm tra CP1

- [x] Hướng, job executor và pain cụ thể.
- [x] Evidence ban đầu có số đếm, phương pháp và ≥5 quote nguyên văn.
- [x] Lát cắt đúng format: 1 user · 1 việc · 1 quyết định AI · 1 kết quả.
- [x] Automation có lý do theo cost-of-error.
- [x] Có 3 willing users kèm mã sinh viên.
- [x] Có đầy đủ tên, mã sinh viên và phân công của 5 thành viên.
