# Hướng Dẫn Thêm Dự Án Mới (Project Onboarding Guide)

Repository này được thiết kế theo cấu trúc **Multi-Project Agent Hub**, cho phép bạn quản lý nhiều nhóm Agent chuyên biệt cho từng dự án khác nhau.

## Các bước thiết lập dự án mới

1. **Nhân bản Template:**
   ```powershell
   Copy-Item -Path "projects\_template" -Destination "projects\<ten-du-an>" -Recurse
   ```

2. **Cập nhật Thông tin Dự án:**
   - Sửa file `projects/<ten-du-an>/knowledge/tech-stack.md`:
     - Điền đường dẫn thư mục code thực tế của dự án.
     - Điền các công nghệ sử dụng (Framework, Database, Styling, State Management).
   - Đổi tiền tố `[PROJECT_NAME]` trong các file `SKILL.md` thành tên viết tắt của dự án (ví dụ: `shop-pm-orchestrator`, `shop-lead-frontend`...).

3. **Khai báo trong `skills.json`:**
   Mở file `.agents/skills.json` và thêm đường dẫn:
   ```json
   {
     "entries": [
       { "path": "projects/dental-project/skills" },
       { "path": "projects/<ten-du-an>/skills" }
     ]
   }
   ```

4. **Kích hoạt:**
   Khi chat trong Antigravity, bạn có thể gọi trực tiếp tên agent (ví dụ: `/shop-pm-orchestrator`) hoặc mô tả công việc liên quan đến dự án để Antigravity tự động định tuyến.
