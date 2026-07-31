# CP3 first-run review

- Provider/model: OpenAI / `gpt-4o-mini`
- Kết quả: **20/24 (83.3%)**
- Routing: **24/24**
- API errors: **0**
- Ngưỡng ≥80%: **đạt**
- Điều kiện 0 claim ngoài source: **chưa đạt**

| Case | Kết quả | Ghi chú |
|---|---|---|
| GS001 | PASS | PASS: đáp ứng expected behavior và hard constraints. |
| GS002 | FAIL | FAIL: trả đúng 4 giai đoạn nhưng thêm nhận định ngoài source ('thường được sử dụng...'), vi phạm no_external_claim. |
| GS003 | PASS | PASS: đáp ứng expected behavior và hard constraints. |
| GS004 | PASS | PASS: đáp ứng expected behavior và hard constraints. |
| GS005 | PASS | PASS: đáp ứng expected behavior và hard constraints. |
| GS006 | FAIL | FAIL: đọc đúng bảng nhưng suy đoán các giá trị có thể là chỉ số hiệu suất; claim này không có trong source. |
| GS007 | FAIL | FAIL: đúng tên 4 bước nhưng tự bổ sung mô tả cho từng bước, vi phạm source_labels_only. |
| GS008 | PASS | PASS: đáp ứng expected behavior và hard constraints. |
| GS009 | PASS | PASS: đáp ứng expected behavior và hard constraints. |
| GS010 | PASS | PASS: đáp ứng expected behavior và hard constraints. |
| GS011 | PASS | PASS: đáp ứng expected behavior và hard constraints. |
| GS012 | PASS | PASS: đáp ứng expected behavior và hard constraints. |
| GS013 | PASS | PASS: đáp ứng expected behavior và hard constraints. |
| GS014 | PASS | PASS: đáp ứng expected behavior và hard constraints. |
| GS015 | PASS | PASS: đáp ứng expected behavior và hard constraints. |
| GS016 | PASS | PASS: đáp ứng expected behavior và hard constraints. |
| GS017 | PASS | PASS: đáp ứng expected behavior và hard constraints. |
| GS018 | PASS | PASS: đáp ứng expected behavior và hard constraints. |
| GS019 | PASS | PASS: đáp ứng expected behavior và hard constraints. |
| GS020 | PASS | PASS: đáp ứng expected behavior và hard constraints. |
| GS021 | PASS | PASS: đáp ứng expected behavior và hard constraints. |
| GS022 | FAIL | FAIL: không đoán số nhưng chỉ báo thiếu căn cứ; chưa hiển thị crop và chưa nói rõ ảnh quá mờ theo expected behavior. |
| GS023 | PASS | PASS: đáp ứng expected behavior và hard constraints. |
| GS024 | PASS | PASS: đáp ứng expected behavior và hard constraints. |
