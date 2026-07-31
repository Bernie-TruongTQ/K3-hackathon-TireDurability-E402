# Automated checks

Ngày chạy: 2026-07-30

## Backend

Lệnh:

```powershell
$env:PYTHONPATH='project'
python -m unittest discover -s project\tests -v
```

Kết quả: **7/7 test pass**.

Test thứ bảy xác nhận PDF số hóa giữ được cả text theo trang và ảnh toàn trang,
sau đó route visual chuyển ảnh nguồn tới generator.

Các hành vi được kiểm tra:

1. Luồng mơ hồ, nhận dạng danh tính và thiếu nguồn.
2. Chunking theo heading giữ cấu trúc Markdown.
3. Upload Markdown → index → chat end-to-end.
4. Visual chunk giữ đường dẫn ảnh và tọa độ.
5. Visual route chuyển đúng crop ảnh tới generator.
6. Ảnh local được mã hóa thành data URL đúng định dạng cho OpenAI Responses API.

## Frontend

Lệnh:

```powershell
corepack pnpm --dir project\frontend build
```

Kết quả: **production build pass**; route `/` được prerender thành công.

## Phạm vi của bằng chứng

Các kiểm tra trên chứng minh luồng phần mềm và ràng buộc dữ liệu hoạt động. Chúng
không thay thế lượt đánh giá 24 case bằng provider AI thật hoặc validation với
người dùng thật.
