# CP5 — Tổng hợp kết quả validation

> Nguồn dữ liệu: kết quả do 5 tester báo cáo và được đại diện đội
> TireDurability xác nhận là chính xác ngày 2026-07-30. Các trace ID và mô tả
> source được giữ theo nội dung tester cung cấp; nhóm không tuyên bố đã xác minh
> độc lập chúng từ log máy chủ.

## Phạm vi

- 5 tester khác nhau, trong đó có 3 willing users đã khai tại CP1.
- Mỗi tester thực hiện 3 câu hỏi và trả lời 3 câu phản hồi sau phiên.
- Tổng cộng 15 lượt hỏi được ghi nhận.
- Tài liệu dùng theo kịch bản: `demo-slides.pdf`.

## Kết quả theo tester

| Tester | Willing user | Kết quả chính | Severity |
|---|---|---|---|
| Vũ Đức Duy | Có | Truy xuất đúng 20/24 và các case fail; thiếu bbox highlight | Medium |
| Nguyễn Đình Bình | Có | Hiểu đúng pipeline; visual crop chưa tự xuất hiện ở câu hỏi sơ đồ | Medium |
| Nguyễn Mạnh Cường | Có | Truy xuất được các phương án/số liệu; trình bày text khó đối chiếu | Medium |
| Hoàng Thị Trà My | Không | Không bịa deadline; abstain UX còn cứng và thiếu next-step | Low |
| Cao Hữu Phúc | Không | Có một lỗi suy diễn ngoài nguồn và một lỗi UX khi crop mờ | High |

## Mẫu phản hồi lặp lại

1. Người dùng đánh giá cao khả năng quay lại trang/crop nguồn để kiểm chứng.
2. Câu hỏi về sơ đồ vẫn thường trả route text; người dùng muốn crop xuất hiện
   tự động.
3. Source card và vùng liên quan chưa đủ nổi bật.
4. Khi từ chối hoặc ảnh mờ, hệ thống cần nói rõ lý do và gợi ý hành động tiếp.
5. Hallucination ngoài nguồn là lỗi critical làm giảm niềm tin.

## Quyết định sau validation

- **Sửa ngay:** siết source-only generation và thêm post-check citation.
- **Sửa trước demo:** tăng nhận diện visual intent cho `pipeline`, `sơ đồ`,
  `quy trình`; cải thiện abstain/refuse UX.
- **Sửa trước demo:** làm source card dễ nhận biết và thêm hướng dẫn chọn lại
  vùng khi crop mờ.
- **Backlog:** bbox highlight chính xác và định dạng bảng cho nội dung so sánh.

## Trạng thái CP5

- [x] Có ít nhất 5 feedback có tên.
- [x] Có ít nhất 5 tester khác nhau.
- [x] Có ít nhất 2 willing users CP1.
- [x] Có quan sát, quote, severity và quyết định thay đổi.
- [x] Changelog trong `spec.md` đã được cập nhật.
- [x] Slide validation đã được chuyển khỏi trạng thái DRAFT.
- [ ] Một thành viên bất kỳ tự giải thích phần mình làm khi TA hỏi.
- [ ] Nhóm tự bấm giờ và xác nhận dry run live không vượt quá 5 phút.
