# Fixture map

Mỗi `fixture_id` trong golden set phải trỏ đến một tài liệu demo đã index. Sau
khi gọi `/api/v1/index/upload`, lưu `document_id` vào một bản sao local:

```powershell
Copy-Item eval/fixtures/document-map.example.json eval/fixtures/document-map.local.json
```

Không dùng dữ liệu người thật ngoài pack. Với provider cloud, ưu tiên fixture
giả tự sinh; không upload nguyên data pack.

