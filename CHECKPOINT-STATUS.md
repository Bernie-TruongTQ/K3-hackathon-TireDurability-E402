# Trạng thái checkpoint — VLearn VisualRAG

| Checkpoint | Trạng thái nội dung | Artifact chính | Phần cần người thật |
|---|---|---|---|
| CP1 — Canvas | Hoàn thành | `CP1-CANVAS.md` | Không |
| CP2 — Bấm được | Hoàn thành | `CP2-PROTOTYPE.md` | Không |
| CP3 — AI thật + đo lượt đầu | Hoàn thành | `CP3-ANSWERS.md`, `eval/results/cp3-openai-first-run.csv` | Không |
| CP4 — Spec gần cuối | Hoàn thành nội dung | `spec.md`, `CP4-AUDIT.md` | Chỉ bằng chứng đã commit/nộp đúng hạn nếu TA hỏi |
| CP5 — Validation + dry run | Hoàn thành artifact validation; còn xác nhận live tại lớp | `validation/feedback-log.csv`, `validation/cp5-results-summary.md` | Nhóm tự bấm giờ dry run và một thành viên bất kỳ giải thích phần mình làm |
| CP6 — Demo | Hoàn thành artifact kỹ thuật và slide validation | `demo/demo-script.md`, `demo-slides.pptx`, `demo-slides.pdf` | Mỗi thành viên nói ≥1 phần; chuẩn bị case lạ của giám khảo |

## Số liệu đã khóa

- Evidence B: 1.261 cặp hỏi–đáp, 369 user, 585 conversation.
- Pain visual explicit: 8 case; ≥4/8 không xử lý được; 5/8 thiếu citation.
- Golden set: 24 case, 10 case từ quan sát thực tế.
- First run: `gpt-4o-mini`, 20/24 pass (83,3%), routing 24/24, 0 API error.
- Quality bar: ≥80% và không có claim ngoài source; first run đạt tỷ lệ nhưng
  chưa đạt ràng buộc critical.

## Nguyên tắc nguồn slide

`project/IT4930_Group19_DSChatBot_Slide.pptx` chỉ là tài liệu kiến trúc bài toán.
Không dùng hình kết quả, số liệu, tên nhóm hoặc thành tích trong file đó làm bằng
chứng của VLearn VisualRAG.

## Audit gần nhất

- Deck CP6: đúng 6 trang, đã render kiểm tra từng trang.
- CP1 đã hoàn thành với tên đội, 5 thành viên, phân công và 3 willing users.
- CP5 đã có 5 dòng validation từ 5 tester, trong đó 3 willing users CP1.
- Dữ liệu được ghi theo xác nhận của đại diện nhóm; chi tiết provenance nằm
  trong `validation/cp5-results-summary.md`.
- Việc còn lại không thể tự động hóa: dry run live có bấm giờ, trả lời kiểm tra
  ngẫu nhiên của TA và reflection cá nhân.
