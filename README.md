# VLearn VisualRAG — Đội TireDurability

Trợ lý học tập truy vấn tài liệu PDF có khả năng giải thích cả văn bản, bảng,
công thức và hình ảnh, đồng thời trả về đúng trang và vùng nguồn đã sử dụng.

## Lát cắt CP6

> Với học viên VLearn đang ôn một bài có slide PDF, khi họ hỏi về một hình,
> bảng hoặc công thức, hệ thống quyết định chỉ dùng nội dung chữ hay cần phân
> tích đúng vùng ảnh bằng VLM, để trả lời có căn cứ kèm trang và hình nguồn.

## Trạng thái prototype

- Mức hiện tại: **Working prototype**.
- DeepSeek-OCR → Markdown/JSON có page, region type và bbox.
- Crop hình được lưu cùng metadata.
- Chroma retrieval + cross-encoder reranking.
- Generation đa phương thức mặc định cho CP3/CP6: OpenAI `gpt-4o-mini`;
  vẫn giữ local Qwen và Gemini làm provider tùy chọn.
- Frontend đã kết nối API VisualRAG và hỗ trợ upload, index, chat, source card,
  route và trace.

DeepSeek-OCR có thể được tiền xử lý cho tài liệu demo để tránh phụ thuộc GPU;
mọi phần tiền xử lý được mô tả rõ trong `spec.md`.

## Thành viên và phân công

| Thành viên | Mã sinh viên | Phần phụ trách |
|---|---|---|
| Đào Văn Đà | 2A202601089 | Hợp nhất code, báo cáo |
| Nguyễn Quốc Anh | 2A202601079 | Viết System Prompt, báo cáo |
| Nguyễn Hoàng Vĩnh Phong | 2A202601265 | UI |
| Trương Quốc Trường | 2A202601195 | Eval, viết bảng |
| Nguyễn Ngọc Ánh | 2A202601643 | Báo cáo |

### Willing users CP1

| Người dùng đồng ý thử | Mã sinh viên |
|---|---|
| Vũ Đức Duy | 2A202601023 |
| Nguyễn Đình Bình | 2A202601091 |
| Nguyễn Mạnh Cường | 2A202601061 |

## Cấu trúc bài nộp

```text
.
├── README.md
├── spec.md
├── demo-slides.pdf
├── project/                   # codebase prototype
├── evidence/                  # mining method và log
├── eval/
│   ├── golden_set.jsonl
│   └── results/
├── validation/
├── reflection/
├── demo/
└── data/                      # data pack BTC cung cấp; không đưa vào repo công khai
```

## Chạy backend

Yêu cầu Python 3.10+.

```powershell
cd project
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python run.py
```

API docs: `http://localhost:1201/docs`.

Lưu ý:

- DeepSeek-OCR và các model local cần tài nguyên lớn; có thể precompute OCR cho
  tài liệu demo.
- Để chứng minh lời gọi AI thật ở quyết định trung tâm, cấu hình provider thật
  và giữ trace trong `eval/results/`.
- Không commit API key.
- Không gửi nguyên data pack lên dịch vụ bên ngoài. Nếu dùng cloud provider,
  chỉ dùng PDF giả tự sinh hoặc phần tối thiểu đã được phép.

## Chạy frontend

```powershell
cd project\frontend
pnpm install
pnpm dev
```

Mặc định frontend gọi API tại `http://localhost:1201`. Có thể đặt
`NEXT_PUBLIC_API_BASE_URL`.

## Tái lập evidence

```powershell
python evidence\mine_visual_queries.py `
  --input data\vlearn-pack\chatlog\chat_history_anonymized_for_hackathon.csv `
  --output evidence\mining-summary.local.json
```

File `.local.json` chỉ dùng nội bộ và không được commit.

## Quality bar

- ≥80% pass trên 24 case.
- Citation correctness = 100%.
- 100% case nguồn sự thật không sinh claim ngoài nguồn.

Chi tiết định nghĩa và bốn lớp chỗ khó: `spec.md`.

## Checklist trước CP6

- [x] Điền tên/mã và phân công của mọi thành viên.
- [x] Có ≥3 willing users có tên.
- [x] Có mining log đạt chuẩn Evidence B.
- [x] Có lời gọi AI thật và trace với OpenAI `gpt-4o-mini`.
- [x] Chạy đủ 24 case, lưu cả pass và fail.
- [x] Có ≥5 feedback từ ≥5 tester ngoài nhóm.
- [x] Có changelog từ feedback.
- [x] `demo-slides.pdf` đúng 6 trang.
- [ ] Dry run 5 phút và backup demo.
- [ ] Mỗi thành viên có một reflection và nói ít nhất một phần.
