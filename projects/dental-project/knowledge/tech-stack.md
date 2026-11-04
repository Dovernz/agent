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

---

## 📋 Danh Mục Lệnh CLI Tái Sử Dụng (Reusable CLI Registry)

Bảng tra cứu nhanh các lệnh chuẩn hóa cho việc kiểm thử, vận hành và quản trị dữ liệu dự án Dental:

### 1. Bộ Kiểm Thử Hợp Nhất (Unified Test Suite Runner)
> Sử dụng công cụ `uv` với Playwright để chạy bộ test tích hợp `test_suite.py`:

- **Chạy toàn bộ kiểm thử (All Suites):**
  ```powershell
  & "C:\Users\thanhcaotien\.local\bin\uv.exe" run --with playwright python "D:\Thành\Agent\projects\dental-project\scripts\test_suite.py" --all
  ```
- **Kiểm tra nhanh kết nối Backend, DB Schema & Giao diện Admin/Features:**
  ```powershell
  & "C:\Users\thanhcaotien\.local\bin\uv.exe" run --with playwright python "D:\Thành\Agent\projects\dental-project\scripts\test_suite.py" --verify
  ```
- **Kiểm thử Đặt lịch E2E nhanh:**
  ```powershell
  & "C:\Users\thanhcaotien\.local\bin\uv.exe" run --with playwright python "D:\Thành\Agent\projects\dental-project\scripts\test_suite.py" --e2e
  ```
- **Kiểm thử Toàn diện Luồng Đặt lịch (Full Multi-step Flow):**
  ```powershell
  & "C:\Users\thanhcaotien\.local\bin\uv.exe" run --with playwright python "D:\Thành\Agent\projects\dental-project\scripts\test_suite.py" --flow
  ```
- **Chạy xuất kết quả chuẩn JSON (Machine-to-Machine):**
  ```powershell
  & "C:\Users\thanhcaotien\.local\bin\uv.exe" run --with playwright python "D:\Thành\Agent\projects\dental-project\scripts\test_suite.py" --verify --json
  ```

### 2. Quản Trị Cơ Sở Dữ Liệu & Migrations (Docker-First)
> Chạy trực tiếp trong container `dental_backend` bảo vệ máy host:

- **Kiểm tra danh sách và trạng thái migrations:**
  ```powershell
  docker exec dental_backend python manage.py showmigrations
  ```
- **Kiểm tra tính toàn vẹn migrations (exit code 0 nếu không có migration tồn đọng):**
  ```powershell
  docker exec dental_backend python manage.py migrate --check
  ```
- **Kiểm tra kết nối và cấu hình Database:**
  ```powershell
  docker exec dental_backend python manage.py check --database default
  ```
- **Áp dụng migrations mới:**
  ```powershell
  docker exec dental_backend python manage.py migrate
  ```

### 3. Đóng Gói Bundle Frontend (esbuild)
> Tạo bundle JS độc lập phục vụ nhúng Django templates (`/dist/booking_app.bundle.js` và `/dist/dental_chart_app.bundle.js`):

- **Build bundles:**
  ```powershell
  cd "d:\Thành\WEB\Code\dental_project\frontend"; node build_bundles.js
  ```

### 4. Soi Dữ Liệu Tiết Kiệm Token (Peek Data Utility)
> Soi nhanh cấu trúc file JSON, CSV, Excel, seed fixture mà không tốn token đọc toàn bộ file:

- **Soi file dữ liệu/seed:**
  ```powershell
  & "C:\Users\thanhcaotien\.local\bin\uv.exe" run python "D:\Thành\Agent\common\scripts\peek_data.py" "<đường_dẫn_file>" --rows 3
  ```
