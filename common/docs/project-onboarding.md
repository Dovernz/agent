# Hướng Dẫn Thêm Dự Án Mới (Project Onboarding Guide)

Repository này được thiết kế theo cấu trúc **Multi-Project Agent Hub**, cho phép bạn quản lý nhiều nhóm Agent chuyên biệt cho từng dự án khác nhau và tự động hóa 100% quy trình khởi tạo.

---

## ⚡ Cách 1: Khởi Tạo Tự Động 1-Click (Khuyên Dùng)

Chạy công cụ `create_project.py` trong thư mục `common/scripts/`:

```powershell
uv run python "D:\Thành\Agent\common\scripts\create_project.py" --name "<ten-du-an>" --repo "<duong-dan-code>" --desc "<mo-ta-nghiep-vu>"
```

### Công cụ sẽ tự động thực hiện:
1. Nhân bản cấu trúc chuẩn từ `projects/_template` sang `projects/<ten-du-an>`.
2. Tự động quét mã nguồn thực tế (`docker-compose.yml`, backend/frontend framework, DB, active ports) và xuất ngay ra `knowledge/tech-stack.md`.
3. Tự động đổi tên và cấu hình `<ten-du-an>-pm-orchestrator`.
4. Tạo tệp ghi nhớ ngữ cảnh xuyên phiên `knowledge/checkpoint.md`.
5. Tự động đăng ký đường dẫn kỹ năng vào cả `skills.json` của Agent Hub và cấu hình toàn cục `~/.gemini/config/skills.json`.

---

## 🛠️ Cách 2: Thiết Lập Thủ Công (Khi Cần Tuỳ Biến Sâu)

1. **Nhân bản Template:**
   ```powershell
   Copy-Item -Path "projects\_template" -Destination "projects\<ten-du-an>" -Recurse
   ```

2. **Cập nhật Thông tin Dự án:**
   - Sửa file `projects/<ten-du-an>/knowledge/tech-stack.md`:
     - Điền đường dẫn thư mục code thực tế của dự án.
     - Điền các công nghệ sử dụng (Framework, Database, Styling, State Management).
   - Đổi tiền tố `[PROJECT_NAME]` trong file `skills/pm-orchestrator/SKILL.md` thành tên viết tắt của dự án (ví dụ: `shop-pm-orchestrator`).

3. **Khai báo trong `skills.json`:**
   Mở file `.agents/skills.json` và thêm đường dẫn:
   ```json
   {
     "entries": [
       { "path": "projects/<ten-du-an>/skills" }
     ]
   }
   ```

4. **Kích hoạt:**
   Khi chat trong Antigravity, bạn có thể gọi trực tiếp tên agent (ví dụ: `shop-pm-orchestrator`) hoặc mô tả công việc liên quan đến dự án để `master-secretary` tự động định tuyến.
