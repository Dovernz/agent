---
name: m2m-protocol
description: Quy định giao tiếp Machine-to-Machine nội bộ. Tự động kích hoạt (always_on) để ÉP XUNG tối đa hiệu năng và siêu tiết kiệm Token.
trigger: always_on
---

# M2M Communication Protocol (Rules)

Mọi Agent BẮT BUỘC tuân thủ luật tiết kiệm Token cực hạn (Extreme Token Saving) sau:

1. **Giao tiếp Zero-Fat:** Tuyệt đối không chào hỏi, không giải thích dài dòng, không lặp lại câu hỏi của PM. CHỈ dùng Cờ tín hiệu.
2. **Cờ tín hiệu chuẩn hóa:**
   - `[ACK]`: Đã nhận lệnh.
   - `[STATUS: DONE]`: Hoàn thành.
   - `[STATUS: FAIL] {"log_file": "..."}`: Thất bại. (Chỉ gửi đường dẫn, cấm in log ra chat).
   - `[STATUS: ESCALATE]`: Lặp quá 3 lần, dừng lại để tránh kẹt loop đốt Token.
   - `[SPEC_CHANGED]`: Báo thay đổi Spec.
3. **Tiết kiệm Context Code:** Khi fix bug, KHÔNG in lại toàn bộ file code ra chat. Tự dùng tool ghi thẳng vào file ổ cứng.
4. **Phân bổ Model thông minh:** Khi PM gọi Sub-agent, ưu tiên cấp quyền `Model: flash` hoặc `flash_lite` cho các task đơn giản (Dàn trang UI, Chạy Linter). Chỉ dùng `pro` (hoặc `inherit`) cho các task dính đến logic phức tạp.
