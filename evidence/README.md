# Evidence

## Cách tái lập

```powershell
python evidence/mine_visual_queries.py `
  --input data/vlearn-pack/chatlog/chat_history_anonymized_for_hackathon.csv `
  --output evidence/mining-summary.local.json
```

`mining-summary.local.json` chứa preview từ data pack và chỉ dùng nội bộ trong
hackathon. Không commit file này khi repo được chia sẻ ra ngoài khoá.

Quy tắc `explicit_visual_patterns_v1` cố ý bảo thủ: chỉ nhận các yêu cầu trực
tiếp như giải thích/phân tích hình, biểu đồ, bảng được khoanh hoặc công thức
Attention. Sau khi chạy script, nhóm phải kiểm tra tay từng hit và ghi quyết
định include/exclude.

## Evidence cần có trước CP6

- [x] Phương pháp đếm tái lập được.
- [x] ≥5 turn ID minh hoạ đã ẩn danh.
- [ ] File log kiểm tra tay từng hit.
- [ ] Khảo sát ≥20 người ngoài nhóm, log đủ từng câu trả lời.

