# Bộ Tiêu Chuẩn Kiểm Toán Hiệu Năng & Đo Đạc Token (Evaluation Metrics)

Tài liệu này định nghĩa hệ quy chiếu tiêu chuẩn để nhóm Agent Giám Sát đánh giá chất lượng phiên làm việc:

## 1. Khung Tiêu Chí Đo Lường (Metrics Framework)

| Tiêu Chí | Đơn Vị Đo | Ngưỡng Tối Ưu (Green) | Ngưỡng Cảnh Báo (Yellow) | Ngưỡng Báo Động (Red) |
| :--- | :--- | :--- | :--- | :--- |
| **Token Tiêu Thụ / Tác vụ** | Tokens | `< 50,000` | `50,000 - 150,000` | `> 150,000` |
| **Tỷ lệ Lỗi Tool (Error Rate)** | % | `< 5%` | `5% - 15%` | `> 15%` |
| **Vòng Lặp QA (Loop Factor)** | Số lần | `0 - 1 lần` | `2 lần` | `≥ 3 lần` (Bắt buộc Escalate) |
| **Thời gian Thực thi (Latency)** | Phút | `< 5 phút` | `5 - 10 phút` | `> 10 phút` (Cần kill) |
| **Tuân thủ M2M Protocol** | % | `100%` | `80% - 99%` | `< 80%` (Chat thừa thãi) |

---

## 2. Công Thức Ước Tính Token
- Văn bản tiếng Việt có dấu: `1 token ≈ 1.8 ký tự`
- Code Python / TypeScript / JSON / SQL: `1 token ≈ 3.8 - 4.0 ký tự`
- Tỷ lệ hỗn hợp trung bình toàn hệ thống: `1 token ≈ 3.5 - 3.8 ký tự`
- Chi phí ước lượng: Phân tách theo bảng giá Model gốc đang kế thừa (`inherit`).
