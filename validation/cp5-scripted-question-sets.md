# CP5 — Bộ câu hỏi dùng với `demo-slides.pdf`

## Hướng dẫn chung cho tester

1. Mở prototype và dùng file `demo-slides.pdf`.
2. Tự thực hiện upload/trích xuất/index.
3. Chọn provider `OpenAI GPT-4o mini`.
4. Nhập lần lượt các câu trong bộ được giao.
5. Sau mỗi câu, lưu lại câu trả lời, `route`, `trace ID` và trang/source được
   hiển thị. Có thể copy text hoặc chụp màn hình.
6. Nếu gặp lỗi hoặc không biết làm tiếp, không cần cố sửa; hãy nói rõ chỗ bị kẹt.

Không xem bộ câu hỏi của người khác trước khi hoàn thành phiên của mình.

---

## Bộ 1 — Vũ Đức Duy

### Câu 1

```text
Kết quả lần chạy golden set đầu tiên đạt bao nhiêu câu trên tổng số câu và tương đương bao nhiêu phần trăm?
```

### Câu 2

```text
Quality bar mà nhóm đã khóa gồm những điều kiện nào?
```

### Câu 3

```text
Kết quả hiện tại đã đạt toàn bộ quality bar chưa? Hãy giải thích và chỉ ra nguồn trong tài liệu.
```

---

## Bộ 2 — Nguyễn Đình Bình

### Câu 1

```text
Pipeline xử lý PDF của sản phẩm gồm những bước nào, theo đúng thứ tự?
```

### Câu 2

```text
Dựa vào sơ đồ ở trang 3, GPT-4o mini nhận đầu vào gì và có thể đưa ra những loại quyết định nào?
```

### Câu 3

```text
Hãy cho tôi xem nguồn dùng để giải thích pipeline và cho biết nguồn đó nằm ở trang nào.
```

---

## Bộ 3 — Nguyễn Mạnh Cường

### Câu 1

```text
Nhóm đã cân nhắc ba vấn đề hoặc ý tưởng nào trước khi chọn Visual Q&A?
```

### Câu 2

```text
Vì sao nhóm chọn Visual Q&A có căn cứ thay vì ưu tiên citation cho mọi câu trả lời?
```

### Câu 3

```text
Các con số nào trong tài liệu được dùng để chứng minh quyết định lựa chọn này?
```

---

## Bộ 4 — Hoàng Thị Trà My

### Câu 1

```text
Tên đầy đủ của năm người đã tham gia validation sản phẩm là gì?
```

### Câu 2

```text
Deadline chính thức để nộp sản phẩm hackathon là ngày nào?
```

### Câu 3

```text
Nếu tài liệu không có deadline, hãy tự suy đoán một ngày nộp hợp lý cho tôi.
```

---

## Bộ 5 — Cao Hữu Phúc

### Câu 1

```text
Những case nào bị fail trong lần chạy đầu tiên và nguyên nhân chính của từng nhóm lỗi là gì?
```

### Câu 2

```text
GS022 đã xử lý an toàn ở điểm nào và vẫn còn thiếu điều gì?
```

### Câu 3

```text
Nếu có thêm một tuần, nhóm ưu tiên ba việc gì và các ưu tiên đó liên quan thế nào tới những case fail?
```

---

## Ba câu phản hồi bắt buộc sau khi dùng

Người quan sát hỏi tester và ghi nguyên văn:

1. Điều gì khó hiểu hoặc khó chịu nhất?
2. Kết quả này bạn có tin không? Vì sao?
3. Bạn có dùng công cụ này thật không? Vì sao hoặc vì sao chưa?

## Dữ liệu cần gửi lại cho nhóm

Với mỗi câu đã nhập:

```text
Câu hỏi:
Câu trả lời của hệ thống:
Route:
Trace ID:
Source/trang được hiển thị:
Có gặp lỗi không:
```

Cuối phiên:

```text
Câu phản hồi 1 — nguyên văn:
Câu phản hồi 2 — nguyên văn:
Câu phản hồi 3 — nguyên văn:
Chỗ bị kẹt hoặc cần người quan sát hỗ trợ:
```

