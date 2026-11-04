# Tech Stack Knowledge Base - [PROJECT_NAME]

Mọi Agent làm việc trên dự án [PROJECT_NAME] BẮT BUỘC tuân thủ:
- **Đường dẫn dự án:** [ĐIỀN ĐƯỜNG DẪN SOURCE CODE TẠI ĐÂY]
- **Nguyên tắc cốt lõi:** Code ngắn gọn, DRY, Component-Driven.
- **Docker-First:** Chạy mọi lệnh kiểm thử, linter, test và install trong Docker.
- **Quản trị Dependency & .env:** Tự động ghi lại thư viện mới và `.env.example`.
- **Cách ly Không gian:** Phân chia rõ ràng thư mục Frontend / Backend, cấm sửa chéo.
- **Tiêu chuẩn Giao tiếp:** Tuân thủ `m2m-protocol.md`.

---

## 📋 Danh Mục Lệnh CLI Tái Sử Dụng (Reusable CLI Registry)

| Nhóm Tác Vụ | Lệnh Mẫu Chuẩn (Thực thi trong Docker / CLI) | Ghi Chú |
| :--- | :--- | :--- |
| **Kiểm tra Dữ liệu (Peek)** | `uv run python D:\Thành\Agent\common\scripts\peek_data.py <path_file> --rows 3` | Soi nhanh CSV/Excel/JSON không tốn token |
| **Kiểm thử Toàn diện** | `python scripts/test_suite.py --all` | Chạy bộ kiểm thử tự động của dự án |
| **Kiểm tra Docker** | `docker-compose ps` / `docker-compose logs --tail=50 <service>` | Xem trạng thái và logs container |
| **Linter Nội bộ (Shift-Left)** | `docker-compose exec <service> <linter_command>` | Tự fix lỗi trước khi bàn giao QA |
