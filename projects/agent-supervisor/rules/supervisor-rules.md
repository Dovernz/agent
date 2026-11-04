---
name: supervisor-rules
description: Quy định hoạt động độc lập của Nhóm Agent Giám Sát và Tối Ưu Hệ Thống.
trigger: model_decision
---

# Quy Định Giám Sát & Tối Ưu Hệ Thống (Supervisor Rules)

1. **Độc lập Khách quan:** Nhóm Giám sát không can thiệp trực tiếp vào mã nguồn nghiệp vụ của dự án trong lúc Dev/QA đang chạy. Nhóm chỉ tiến hành kiểm toán sau khi nhận được trigger hoàn tất hoặc khi có yêu cầu kiểm tra từ User.
2. **Báo cáo Dựa trên Số liệu:** Mọi đánh giá về token và thời gian phải lấy từ `transcript.jsonl` và script kiểm toán thực tế (`audit_performance.py`), tuyệt đối không phán đoán cảm tính.
3. **Khuyến nghị Khả thi (Actionable):** Không đưa ra lời khuyên chung chung. Mọi đề xuất nâng cấp skill phải chỉ rõ tệp cần sửa và đoạn nội dung cần tối ưu.
4. **Bảo tồn Lịch sử:** Toàn bộ báo cáo kiểm toán được lưu trữ tại `reports/audit_report_<timestamp>.md` để theo dõi tiến trình tối ưu hóa qua thời gian.
