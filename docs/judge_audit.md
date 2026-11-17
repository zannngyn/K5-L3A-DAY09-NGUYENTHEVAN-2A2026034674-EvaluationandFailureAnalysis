# Judge audit

Chạy: `python -m lab9.judge --csv <file> --audit 5`

| Tiêu chí | n | κ | Precision | Recall | Đạt FLOORS (κ≥0.6, P≥0.8, R≥0.7)? | Quyết định |
|---|---|---|---|---|---|---|
| tone_ok | 100 | 0.757 | 0.857 | 0.800 | Có (PASS) | dùng |
| helpful | 100 | 0.375 | 1.000 | 0.300 | Không (FAIL: κ=0.375 < 0.6, R=0.300 < 0.7) | loại |

- `tone_ok`: `confusion={'tp': 24, 'fp': 4, 'fn': 6, 'tn': 66}`, `observed_fail_rate=0.28` → `corrected_fail_rate=0.3` (Rogan-Gladen).
- `helpful`: `confusion={'tp': 9, 'fp': 0, 'fn': 21, 'tn': 70}`, `observed_fail_rate=0.09` → `corrected_fail_rate=0.3` (judge bỏ sót 21/30 ca FAIL của người).

## ≥5 case audit thủ công

### 1) Audit `judge_tone_public.csv` (5 bất đồng đầu tiên)
| # | Case | Judge nói | Người nói | Ai đúng? | Ghi chú / sửa rubric |
|---|---|---|---|---|---|
| 1 | `H-008` | PASS | FAIL | Người đúng | Câu `"Em đã hoàn tiền cho anh rồi nha, anh check giúp em."` dùng đại từ thân mật quá mức ("em/anh", "nha") và không xưng danh LogiX. Bổ sung vào rubric: cấm đại từ thân mật/tiếng lóng ("nha", "check"), bắt buộc xưng danh chuẩn. |
| 2 | `H-017` | PASS | FAIL | Người đúng | Câu `"Dạ, bạn ơi LogiX đã hoàn 25.000đ cho đơn O-606 rồi nha."` dùng "bạn ơi", "rồi nha" thiếu trang trọng. Bổ sung danh sách từ không đạt chuẩn CSKH. |
| 3 | `H-029` | PASS | FAIL | Người đúng | Câu `"Dạ, vui lòng chờ. Hệ thống đang xử lý, không cần nhắn thêm."` có giọng gắt/xua khách ("không cần nhắn thêm"). Bổ sung quy tắc phạt câu từ đuổi khách dù có chữ "Dạ". |
| 4 | `H-042` | FAIL | PASS | Người đúng | Câu `"Dạ, đơn O-808 đã hoàn 120.000đ. Tiền về trong 3–5 ngày ạ."` lịch sự, rõ ràng; judge bắt nhầm vì thiếu từ xin lỗi/cảm ơn. Sửa rubric: không bắt buộc xin lỗi khi thông báo hoàn tiền thành công. |
| 5 | `H-051` | FAIL | PASS | Người đúng | Câu `"Dạ, LogiX đã refund 90.000đ cho đơn O-202 ạ."` bị judge đánh FAIL có thể do xen từ tiếng Anh `"refund"`. Làm rõ trong rubric xem thuật ngữ `"refund"` có được phép hay không. |

### 2) Audit `judge_helpful_public.csv` (5 bất đồng đầu tiên)
| # | Case | Judge nói | Người nói | Ai đúng? | Ghi chú / sửa rubric |
|---|---|---|---|---|---|
| 1 | `HL-015` | PASS | FAIL | Người đúng | `"Dạ, LogiX đã hoàn 55.000đ cho đơn O-112 ạ."` — câu ngắn gọn nhưng thiếu thông tin bước tiếp theo / thời gian nhận tiền hoặc sai ngữ cảnh cần giải thích. Judge chỉ nhìn thấy có số tiền + mã đơn nên cho PASS. |
| 2 | `HL-016` | PASS | FAIL | Người đúng | `"Dạ, LogiX thành thật xin lỗi anh/chị vì sự bất tiện này..."` — chỉ xin lỗi chung chung, không trả lời trạng thái đơn hay số tiền hoàn. Judge bị đánh lừa bởi giọng điệu lịch sự (false negative). |
| 3 | `HL-020` | PASS | FAIL | Người đúng | `"Dạ, LogiX đã hoàn 90.000đ cho đơn O-303 ạ."` — thiếu hướng dẫn kiểm tra/thời gian xử lý theo rubric hữu ích. |
| 4 | `HL-028` | PASS | FAIL | Người đúng | Chỉ xin lỗi dài dòng, không đưa kết quả xử lý cụ thể; judge chấm nhầm dựa trên độ dài/lịch sự. |
| 5 | `HL-035` | PASS | FAIL | Người đúng | Xin lỗi sáo rỗng, không giải quyết yêu cầu của khách. Cần sửa rubric `helpful`: bắt buộc kiểm tra **có trả lời đúng trạng thái/hành động cụ thể**, cấm chấm PASS chỉ vì lịch sự. |

## Kết luận
- **Tiêu chí bị loại:** `helpful` bị loại và **không được dùng làm gate**. Dù `Precision = 1.0` (0 FP), `Recall = 0.300` (21 FN trên 30 ca FAIL) và `κ = 0.375 < 0.6` khiến judge bỏ sót 70% lỗi không hữu ích, làm tụt tỉ lệ lỗi quan sát xuống `0.09` trong khi tỉ lệ thật hiệu chỉnh Rogan-Gladen là `0.30`.
- **Tiêu chí được dùng:** `tone_ok` đạt cả 3 ngưỡng (`κ = 0.757 ≥ 0.6`, `P = 0.857 ≥ 0.8`, `R = 0.800 ≥ 0.7`), có thể dùng cho kiểm tra giọng điệu với lưu ý cập nhật rubric để giảm 6 FN (từ ngữ thân mật) và 4 FP (lỗi nhận diện từ `"refund"`).
- **Rủi ro còn lại:** judge chỉ được kiểm trên dữ liệu replay đã công khai; cần nhãn người mới để có tập held-out thật, và tiền/approval luôn chấm bằng code, không dùng judge.
