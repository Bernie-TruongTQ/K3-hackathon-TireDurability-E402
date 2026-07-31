# Cấu hình OpenAI cho lượt chạy CP3

Model đã chốt: `gpt-4o-mini`.

## 1. Tạo API key

Tạo key trong OpenAI Platform. Không gửi key qua chat, không chụp màn hình key
và không commit key vào Git.

## 2. Tạo file cấu hình local

Tại thư mục gốc repo:

```powershell
Copy-Item project\.env.example project\.env
notepad project\.env
```

Trong `project/.env`, giữ các dòng:

```dotenv
VISUALRAG_LLM_PROVIDER="openai"
VISUALRAG_OPENAI_API_KEY="sk-...key-thật-của-bạn..."
VISUALRAG_OPENAI_MODEL="gpt-4o-mini"
VISUALRAG_OPENAI_MAX_OUTPUT_TOKENS=1024
VISUALRAG_OPENAI_TEMPERATURE=0.2
VISUALRAG_VECTOR_STORE_PROVIDER="local"
VISUALRAG_RERANKER_PROVIDER="lexical"
```

`project/.env` đã bị loại khỏi Git bởi `.gitignore`.

## 3. Chạy và đóng băng first run

```powershell
python tools\run_cp3_openai.py
```

Kết quả được lưu tại:

- `eval/results/cp3-openai-first-run.csv`
- `eval/results/cp3-openai-first-run.summary.json`

Script không ghi đè first run. Mọi case lỗi hoặc fail vẫn được lưu.

## 4. Chấm semantic

Đối chiếu từng `answer` với `expected_behavior` và `hard_constraints` trong
`eval/golden_set.jsonl`, sau đó điền:

- `grounded_pass`
- `usefulness_pass`
- `overall_pass`
- `reviewer`
- `notes`

Chỉ sau bước này mới được báo kết quả dạng `x/24`.
