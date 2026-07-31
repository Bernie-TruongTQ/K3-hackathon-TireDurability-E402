# Evidence B — 8 truy vấn visual nguyên văn

Nguồn: `data/vlearn-pack/chatlog/chat_history_anonymized_for_hackathon.csv`.

Phương pháp đếm và quy tắc lọc được mô tả trong
`evidence/mine_visual_queries.py` và `evidence/mining-results.md`. Bảng dưới giữ
nguyên văn message của học viên, chỉ dùng mã `turn_id` đã ẩn danh.

| Turn | Nội dung nguyên văn |
|---|---|
| `T0135` | “(Trang 16, đoạn được chọn: "tóm tắt nội dung các giai đoạn được mô tả trên slide các biểu đồ") tóm tắt nội dung các giai đoạn được mô tả trên slide các biểu đồ” |
| `T0393` | “(Trang 9, đoạn được chọn: "giải thích phần bảng được khoanh") giải thích phần bảng được khoanh” |
| `T0471` | “(Trang 6, đoạn được chọn: "Phát triển Sản phẩm AI (AI Product)") Giải thích đoạn bôi đen ở Trang 6: "Phát triển Sản phẩm AI (AI Product)" giải thích hình biểu diễn” |
| `T0611` | “(Trang 16, đoạn được chọn: "Mô hình Double Diamond — Don Norman / British Design Council (2005)") giải thích hình ảnh này” |
| `T0816` | “(Trang 2, đoạn được chọn: "người trong ảnh là ai") người trong ảnh là ai” |
| `T0840` | “(Trang 59, đoạn được chọn: "phân tích hình ảnh được khoanh đỏ ở slide 59") phân tích hình ảnh được khoanh đỏ ở slide 59” |
| `T1043` | “(Trang 61, đoạn được chọn: "công thức attention là gì") công thức attention là gì” |
| `T1226` | “(Trang 27, đoạn được chọn: "Công thức toán học của attention mechanism?") Công thức toán học của attention mechanism?” |

## Kết luận có thể kiểm tra lại

- Có 8 truy vấn visual explicit từ 8 user và 8 conversation khác nhau.
- Có ít nhất 5 ví dụ nguyên văn theo chuẩn Evidence B; file này giữ đủ cả 8.
- `evidence/manual-review.csv` ghi hành vi tutor tương ứng và quyết định include.
