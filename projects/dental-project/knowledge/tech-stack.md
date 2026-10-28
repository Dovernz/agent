# Tech Stack Knowledge Base - Minh Sinh Dental (`dental_project`)

Mọi Agent làm việc trên dự án Minh Sinh Dental BẮT BUỘC tuân thủ:
- **Đường dẫn dự án:** `d:\Thành\WEB\Code\dental_project`
- **Nguyên tắc cốt lõi:** Code siêu ngắn, DRY, Component-Driven (chia nhỏ UI).
- **Docker-First (BẢO VỆ MÁY GỐC):** Mọi lệnh cài đặt (npm, pip) hoặc chạy script (linter, test, db check) BẮT BUỘC phải chạy BÊN TRONG container Docker (vd: `docker-compose exec` hoặc `docker run`). Tuyệt đối KHÔNG chạy lệnh trực tiếp làm rác môi trường máy tính gốc của User.
- **Quản trị Dependency & .env:** Cài thêm thư viện BẮT BUỘC tự động cập nhật `package.json`/`requirements.txt` và ghi chú biến vào `.env.example`.
- **Cách ly Không gian (Workspace Isolation):** Khi chạy song song, Frontend CHỈ sửa file trong folder `/frontend`, Backend CHỈ sửa trong folder `/backend`. CẤM sửa chéo để tránh Git Conflict.
- **Tốc độ:** Lazy Load, UI Mobile-First. Auto-Cleanup file rác sau test.
- **State:** Cache API = React Query/SWR. State UI = Zustand. Redux bị cấm.
- **Tiêu chuẩn:** Tuân thủ `m2m-protocol.md`.
