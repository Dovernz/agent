---
name: m2m-protocol
description: Quy định giao tiếp Machine-to-Machine nội bộ. Tự động kích hoạt (always_on) để ÉP XUNG tối đa hiệu năng và siêu tiết kiệm Token.
trigger: always_on
---

# M2M Communication Protocol (Rules)

Mọi Agent BẮT BUỘC tuân thủ luật tiết kiệm Token cực hạn (Extreme Token Saving) sau:

1. **Giao tiếp Zero-Fat:** Tuyệt đối không chào hỏi, giải thích dài dòng, hay lặp lại câu hỏi. CHỈ dùng Cờ tín hiệu.
2. **Cờ tín hiệu chuẩn hóa:**
   - `[ACK]`: Đã nhận lệnh.
   - `[STATUS: DONE]`: Hoàn thành.
   - `[STATUS: FAIL] {"log_file": "..."}`: Thất bại. (Chỉ gửi đường dẫn, cấm in log ra chat).
   - `[STATUS: ESCALATE]`: Lặp quá 3 lần, dừng lại tránh đốt Token.
   - `[SPEC_CHANGED]`: Báo thay đổi Spec.
3. **Tiết kiệm Context Code:** Khi fix bug, KHÔNG in lại file code ra chat. Tự dùng tool ghi thẳng vào file ổ cứng.
4. **Đồng bộ Model (Inherit):** Mọi Sub-agent được gọi lên BẮT BUỘC dùng chế độ cấu hình `Model: inherit` để kế thừa chính xác Model gốc (Gemini 3.1 Pro Low) mà User đang dùng. Tuyệt đối không tự ý đổi sang model khác.
