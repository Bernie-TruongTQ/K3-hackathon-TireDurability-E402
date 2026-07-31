# Eval

## Cơ cấu golden set

- 24 case.
- 10 case lấy hoặc phát triển từ chatlog thật (`GS001`–`GS010`).
- 8 case thường (`GS011`–`GS018`).
- 4 case khó bổ sung (`GS019`–`GS022`).
- 2 case hiếm (`GS023`–`GS024`).
- Mỗi lớp nguồn sự thật, mơ hồ, ngoài phạm vi và domain có ít nhất hai case.

## Quality bar đã ghi trong spec

- ≥80% pass tổng thể.
- Citation correctness = 100%.
- 100% case lớp nguồn sự thật không sinh claim ngoài source.

Không đổi bar sau khi có kết quả. Mọi lượt chạy phải lưu đủ cả case pass và fail.

## First run — OpenAI gpt-4o-mini

- Kết quả strict review: **20/24 (83,3%)**.
- Routing: **24/24**.
- API errors: **0**.
- Đạt ngưỡng tổng ≥80%, nhưng chưa đạt điều kiện 0 claim ngoài source.
- Kết quả đầy đủ: `results/cp3-openai-first-run.csv`.
- Giải thích từng case: `results/cp3-openai-first-run-review.md`.

## Định dạng kết quả

Mỗi file trong `results/` phải có:

```csv
run_id,case_id,provider,route,answer,sources,grounded_pass,citation_pass,routing_pass,failure_pass,overall_pass,reviewer,notes
```

Hai người chấm độc lập ít nhất năm case khó trước khi chốt định nghĩa.
