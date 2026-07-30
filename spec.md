# AI SPEC — VLearn VisualRAG · Đội TireDurability · Zone B

Hướng: [x] A — VLearn  [ ] B — Trợ lý Học viên  [ ] C — Làn mở  
Loại: [ ] Tối ưu tính năng có sẵn  [x] Tính năng mới

## §1. User & Job

- **Job executor:** học viên VLearn đang ôn một bài học từ slide PDF có hình, bảng, sơ đồ hoặc công thức.
- **Workflow hiện tại:** chọn đoạn/trang → hỏi tutor → nếu tutor không nhìn được hình thì tự mô tả lại, chuyển sang công cụ khác hoặc bỏ qua.
- **Core JTBD:** Khi ôn bài từ slide PDF, tôi muốn hiểu cả nội dung chữ và hình trong đúng ngữ cảnh để không phải chuyển qua nhiều công cụ và tránh học sai.
- **Problem statement:** Học viên VLearn không nhận được lời giải thích có căn cứ cho nội dung trực quan trong slide, nên phải mô tả lại hình/bảng bằng tay, dùng công cụ khác hoặc bỏ qua phần kiến thức đó.

### Evidence B — mining data pack

Nguồn: `data/vlearn-pack/chatlog/chat_history_anonymized_for_hackathon.csv`, gồm 1.261 cặp hỏi–đáp, 369 user và 585 hội thoại.

Phương pháp đếm bảo thủ:

1. Chỉ đọc message có `role=student`.
2. Lọc câu có yêu cầu trực tiếp về ảnh/hình biểu diễn/biểu đồ/bảng/công thức.
3. Kiểm tra tay từng lượt, loại các câu chỉ nhắc đến từ “mô hình”, “hình dung”, “hình thức”.
4. Đối chiếu câu trả lời tutor cùng `turn_id`, ghi nhận citation, rating và hành vi khi không thấy hình.
5. Script tái lập: `evidence/mine_visual_queries.py`.

Kết quả ban đầu:

- 8 lượt hỏi phụ thuộc trực tiếp vào nội dung trực quan theo quy tắc bảo thủ.
- Ít nhất 4/8 lượt không thể xử lý nội dung hình hoặc yêu cầu học viên tự nhập lại thông tin.
- `T0135` bị đánh giá `down`.
- Toàn bộ data pack có 582/1.261 câu trả lời tutor không có citation (46,2%).

Ví dụ có thể kiểm tra lại:

Nguyên văn đầy đủ của cả 8 truy vấn: `evidence/visual-query-quotes.md`.

| Turn  | Pain quan sát được                       | Kết quả hiện tại                                          |
| ----- | ---------------------------------------- | --------------------------------------------------------- |
| T0135 | Muốn tóm tắt các giai đoạn trong biểu đồ | Tutor không tìm thấy; rating `down`                       |
| T0393 | Muốn giải thích phần bảng được khoanh    | Tutor yêu cầu nhập lại nội dung bảng                      |
| T0611 | Muốn giải thích hình Double Diamond      | Trả lời được từ text/citation, chưa chứng minh đã đọc ảnh |
| T0840 | Muốn phân tích ảnh khoanh đỏ ở slide 59  | Tutor thừa nhận không thấy ảnh                            |
| T0471 | Muốn giải thích hình biểu diễn           | Trả lời theo kiến thức suy đoán, không citation           |
| T0816 | Hỏi người trong ảnh                      | Không xác định được ảnh đang nói tới                      |
| T1043 | Hỏi công thức Attention                  | Dùng kiến thức ngoài tài liệu dù không tìm thấy căn cứ    |
| T1226 | Hỏi công thức Attention trong slide      | Từ chối vì không tìm thấy công thức trong text            |

### Evidence A — khảo sát

Nhóm chọn **Evidence B** làm đường bằng chứng chính nên khảo sát ≥20 người không
phải điều kiện bắt buộc. `validation/survey-template.md` được giữ làm công cụ
khảo sát bổ sung; không ghi số liệu khi chưa khảo sát thật.

## §2. Impact & quyết định chọn

| Ứng viên                                 | Quy mô quan sát được                                        | Tần suất / tổn thất mỗi lần                                                                             | Khả thi trong hackathon                 | Quyết định                 |
| ---------------------------------------- | -----------------------------------------------------------:| ------------------------------------------------------------------------------------------------------- | --------------------------------------- | -------------------------- |
| Giải thích hình/bảng/công thức có căn cứ | 8/369 user có query explicit trong mẫu; 8/1.261 lượt        | ≥4/8 lượt không xử lý được; mỗi lần phải mô tả lại/chuyển công cụ/bỏ qua, 1 rating `down`               | Có — tái dùng OCR/RAG hiện có           | **Chọn**                   |
| Bắt buộc citation cho mọi câu trả lời    | 582/1.261 câu tutor, tương đương 46,15%                     | Mỗi answer thiếu citation làm user không kiểm chứng được nguồn; ảnh hưởng rộng nhưng không riêng visual | Có, nhưng phạm vi rộng hơn một lát cắt  | Loại khỏi CP6, đưa backlog |
| Giảm latency outlier                     | 2.522 message của 369 user; p90 3.686 giây, max 23.848 giây | 10% message chậm ít nhất 3,686 giây; mất thời gian chờ nhưng ít ảnh hưởng độ đúng                       | Có, nhưng không tận dụng thế mạnh dự án | Loại                       |

Lý do chọn: tần suất explicit thấp hơn citation gap nhưng cost-of-error cao hơn; nhóm đã có nền DeepSeek-OCR, crop ảnh, Chroma và reranker nên có thể tạo một lát cắt Working trong thời gian sự kiện.

## §3. Giải pháp tương tự đã nghiên cứu

| Sản phẩm              | Flow                                   | Đáng học                      | Đáng né                                                    | VLearn VisualRAG khác gì                                 |
| --------------------- | -------------------------------------- | ----------------------------- | ---------------------------------------------------------- | -------------------------------------------------------- |
| NotebookLM            | Nạp nguồn → hỏi → trả lời kèm citation | Citation nằm cạnh câu trả lời | Workspace rộng, không tối ưu chọn vùng hình trong slide    | Tập trung một câu hỏi học tập và hiển thị đúng crop hình |
| ChatGPT upload PDF    | Upload → chat đa phương thức           | UX đơn giản, xử lý linh hoạt  | Có thể dùng kiến thức ngoài nguồn và khó tái lập retrieval | Conditional routing và từ chối khi không có căn cứ       |
| VLearn tutor hiện tại | Chọn đoạn/trang → hỏi tutor            | Có ngữ cảnh trang             | Không thấy nội dung trực quan trong nhiều case             | Kết hợp text chunk + visual chunk + page/bbox            |

## §4. Thiết kế

### Lát cắt MỘT CÂU

> Với học viên VLearn đang ôn một bài có slide PDF, khi họ hỏi về một hình, bảng hoặc công thức, hệ thống quyết định chỉ dùng nội dung chữ hay cần phân tích đúng vùng ảnh bằng VLM, để trả lời có căn cứ kèm trang và hình nguồn.

### Non-goals

1. Không xây workspace/folder/template kiểu NotebookLM hoặc ChatGPT.
2. Không tìm kiếm web hoặc trả lời kiến thức ngoài tài liệu đã nạp.
3. Không hỗ trợ tài liệu thật ngoài data pack hoặc dữ liệu giả tự sinh trong hackathon.
4. Không xây auth, multi-user, phân quyền hay deployment production.
5. Không xử lý mọi định dạng; CP6 chỉ cam kết PDF/Markdown và ảnh.

### Mức prototype

- [ ] Sketch  [ ] Mock  [x] Working

- OpenAI `gpt-4o-mini` đã chạy thật trên đủ 24 case; trace xác nhận
  `provider=openai`, `model=gpt-4o-mini`, `is_mock=false`.
- Thật: ingest, lưu page/bbox/image, retrieval, routing, citation, UI flow.
- Có thể precompute: DeepSeek-OCR cho tài liệu demo để tránh phụ thuộc GPU khi trình bày.
- Mock được phép: danh sách tài liệu mẫu và tiến trình OCR dài; phải gắn nhãn rõ trong UI.

### Automation

- [ ] augment  [x] conditional  [ ] automate

- Sai giải thích hình/công thức có thể khiến học viên học sai. Hệ thống chỉ tự trả lời khi có nguồn truy xuất; thiếu trang/hình thì hỏi lại, thiếu căn cứ thì từ chối.

### §4b. Nguyên tắc HAX/PAIR

| Nguyên tắc                         | Áp cụ thể vào đâu trong prototype                                                                      |
| ---------------------------------- | ------------------------------------------------------------------------------------------------------ |
| G1 — Làm rõ hệ thống làm được gì   | Empty state nói rõ chỉ trả lời từ tài liệu đã nạp và có thể đọc hình/bảng                              |
| G2 — Làm rõ nó làm tốt đến đâu     | Mỗi câu trả lời hiển thị mode `text`/`visual`, nguồn và mức căn cứ                                     |
| G10 — Thu hẹp phạm vi khi nghi ngờ | Không xác định được trang/hình → hỏi user chọn nguồn thay vì đoán                                      |
| G11 — Giải thích vì sao            | Citation gồm filename, page, region và thumbnail                                                       |
| G9 — Sửa dễ dàng                   | Mỗi source card là nút chọn; lần hỏi tiếp gửi `selected_page` và `selected_image_id` để khóa đúng vùng |

## §5. Kiểu lỗi — 4 lớp chỗ khó

| ID  | Tình huống                                       | Lớp              | Hành vi mong muốn                                              | Nguyên tắc |
| --- | ------------------------------------------------ | ---------------- | -------------------------------------------------------------- | ---------- |
| S1  | Query không có chunk đủ liên quan                | ① Nguồn sự thật  | Nói không tìm thấy căn cứ; không dùng kiến thức ngoài          | G2, G10    |
| S2  | Text và hình cho thông tin mâu thuẫn             | ① Nguồn sự thật  | Hiển thị cả hai nguồn, nêu mâu thuẫn, không kết luận chắc      | G11        |
| A1  | “Giải thích hình này” nhưng chưa chọn trang/hình | ② Mơ hồ          | Hỏi user chọn trang hoặc nguồn cụ thể                          | G10        |
| A2  | Một trang có nhiều biểu đồ                       | ② Mơ hồ          | Hiển thị thumbnail để user chọn                                | G9, G10    |
| O1  | Hỏi kiến thức web/ngoài tài liệu                 | ③ Ngoài phạm vi  | Từ chối ngắn và nhắc phạm vi                                   | G1         |
| O2  | Hỏi nhận dạng người trong ảnh                    | ③ Ngoài phạm vi  | Không suy đoán danh tính; mô tả nội dung học thuật nếu hữu ích | G1, G10    |
| D1  | OCR đọc sai ký hiệu trong công thức              | ④ Đặc thù domain | Gọi VLM trên crop gốc, hiển thị ảnh và cảnh báo nếu chưa chắc  | G2, G11    |
| D2  | Bảng bị tách hàng/cột sai                        | ④ Đặc thù domain | Dùng ảnh gốc làm nguồn chính; không dựng số liệu thiếu         | G10, G11   |

## §6. Bốn đường đi của trải nghiệm

- **Happy path:** upload tài liệu → hỏi nội dung chữ/hình → retrieve → nếu cần gọi VLM → trả lời + citation.
- **Low-confidence:** retrieval có điểm thấp hoặc nhiều hình đồng hạng → hỏi user chọn trang/hình.
- **Failure/không căn cứ:** không có nguồn → trả lời “không tìm thấy trong tài liệu đã nạp”.
- **Correction:** user chọn nguồn khác hoặc báo sai nguồn → chạy lại với source đã khóa và lưu feedback.
- **Ngoài phạm vi:** không web search, không nhận dạng người, không trả lời bằng kiến thức ngoài.
- **Đặc thù domain:** công thức/bảng luôn kèm crop gốc để user kiểm tra.

## §7. Kiểm thử

### Chiều chất lượng

| Chiều                | Pass khi                                                                       |
| -------------------- | ------------------------------------------------------------------------------ |
| Grounded correctness | Mọi claim kiểm chứng được từ source được trả về; không thêm fact ngoài source  |
| Citation correctness | Filename/page/region trỏ đúng nội dung dùng để trả lời                         |
| Visual routing       | Câu hỏi phụ thuộc hình gọi visual path; câu text không gọi VLM không cần thiết |
| Graceful failure     | Case thiếu nguồn/mơ hồ/ngoài phạm vi hỏi lại hoặc từ chối đúng                 |
| Usefulness           | Trả lời trực tiếp câu hỏi, tiếng Việt rõ, không dài quá mức cần thiết          |

- Golden set: `eval/golden_set.jsonl`, mục tiêu 24 case; ≥10 phát triển từ chatlog thật.
- **Quality bar chốt:** đạt khi ≥80% case pass tổng thể, citation correctness = 100%, và 100% case lớp ① không sinh claim ngoài nguồn.
- Kết quả các lượt chạy: `eval/results/`.
- Không đổi quality bar sau khi chạy; nếu chưa đạt phải giữ kết quả và phân tích.
- **First run `gpt-4o-mini`: 20/24 (83,3%)**, routing 24/24, 0 API
  errors. Đạt ngưỡng tổng nhưng chưa đạt ràng buộc 0 claim ngoài source do
  `GS002`, `GS006`, `GS007`; `GS022` fail usefulness vì chưa trả crop/giới hạn
  ảnh mờ đúng yêu cầu.

## §8. Phân công & kế hoạch

| Họ và tên               | Mã sinh viên | Vai trò               |
| ----------------------- | ------------ | --------------------- |
| ĐÀO VĂN ĐÀ              | 2A202601089  | Product/spec/evidence |
| NGUYỄN QUỐC ANH         | 2A202601079  | Backend OCR/indexing  |
| NGUYỄN HOÀNG VĨNH PHONG | 2A202601265  | UI Retrieval/VLM/eval |
| TRƯƠNG QUỐC TRƯỜNG      | 2A202601195  | Frontend/demo         |
| NGUYỄN NGỌC ÁNH         | 2A202601643  | Validation/slide      |

- Willing users: **Vũ Đức Duy — 2A202601023; Nguyễn Đình Bình — 2A202601091;
  Nguyễn Mạnh Cường — 2A202601061**.
- Tester bổ sung cho CP5: **Hoàng Thị Trà My — 2A202601290; Cao Hữu Phúc —
  2A202601283**. Nguyễn Quốc Anh phụ trách quan sát và ghi log phiên của Cao
  Hữu Phúc.
- Vòng validation: dùng `validation/feedback-log.csv`; mỗi phiên giao một task, im lặng quan sát, hỏi đúng ba câu theo guide.
- Kế hoạch và phiếu quan sát: `validation/cp5-test-plan.md` và
  `validation/cp5-observer-form.md`.

## §9. Changelog

| Thời điểm  | Đổi gì                                                        | Vì sao                                                                                     |
| ---------- | ------------------------------------------------------------- | ------------------------------------------------------------------------------------------ |
| 2026-07-30 | Đổi định vị từ chatbot PDF chung sang VLearn VisualRAG        | Khớp Hướng A và evidence chatlog                                                           |
| 2026-07-30 | Chọn conditional automation                                   | Cost-of-error cao khi giải thích sai hình/công thức                                        |
| 2026-07-30 | Bỏ workspace/folder/template khỏi scope                       | Giữ demo trong 5 phút và tập trung lát cắt                                                 |
| 2026-07-30 | Tích hợp OpenAI Responses API với `gpt-4o-mini`               | Cần lời gọi AI/VLM thật ở quyết định trung tâm                                             |
| 2026-07-30 | Giữ first run 20/24 và công khai 4 case fail                  | Tuân thủ quality bar đã chốt, không che failure                                            |
| 2026-07-30 | Cho phép bấm source card để khóa `selected_image_id`          | Làm correction path và HAX G9 khớp prototype                                               |
| 2026-07-30 | Ghi nhận validation 5/5 tester, gồm 3 willing users CP1       | Hoàn thành feedback log có tên, quan sát, quote và severity                                |
| 2026-07-30 | Ưu tiên source-only post-check và cải thiện visual/abstain UX | Tester ghi nhận một lỗi suy diễn ngoài nguồn, crop chưa tự hiện và từ chối thiếu next-step |
| 2026-07-30 | Giữ bbox highlight và bảng so sánh trong backlog              | Có ích nhưng thấp hơn lỗi hallucination và khả năng phục hồi khi crop mờ                   |
