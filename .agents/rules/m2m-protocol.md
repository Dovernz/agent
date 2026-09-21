---
name: m2m-protocol
description: Quy định giao tiếp Machine-to-Machine nội bộ giữa các Agent. Tự động kích hoạt (always_on) để tối ưu Token và tốc độ.
trigger: always_on
---

# M2M Communication Protocol (Rules)

Để tiết kiệm Token tối đa và tối ưu hóa giao tiếp nội bộ, TẤT CẢ các Agents (PM, Architect, Leads, Sub-agents) BẮT BUỘC tuân thủ các quy tắc Machine-to-Machine (M2M) sau khi chat với nhau:

1. **Tuyệt đối không dùng ngôn ngữ tự nhiên** dài dòng (chào hỏi, giải thích) khi làm việc nội bộ. CHỈ dùng JSON, Bash Log hoặc các Cờ tín hiệu (Tags).
2. **Chỉ PM** mới được dùng ngôn ngữ tự nhiên khi báo cáo kết quả cuối cùng hoặc cần hỏi ý kiến **User (Người dùng thật)**.
3. **Các cờ tín hiệu chuẩn hóa:**
   - `[ACK]`: Đã nhận lệnh, bắt đầu làm ngay.
   - `[STATUS: DONE]`: Đã hoàn thành nhiệm vụ thành công.
   - `[STATUS: FAIL] {"log_file": "..."}`: Thất bại. Tuyệt đối không ném log trực tiếp vào chat, phải ghi log ra file văn bản và chỉ truyền đường dẫn.
   - `[STATUS: ESCALATE]`: Yêu cầu con người can thiệp khẩn cấp (thường do lặp QA quá 3 lần).
   - `[SPEC_CHANGED]`: Cảnh báo hệ thống có sự thay đổi về file đặc tả API (API Spec).
