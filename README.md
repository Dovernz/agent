# Multi-Project Agent Hub (`.agents`)

Trung tâm quản lý và điều phối các nhóm **AI Agent chuyên biệt theo từng dự án**, tích hợp trực tiếp với Google Antigravity.

---

## 🏗️ Cấu trúc Hệ thống

```text
.agents/
├── common/                          # Giao thức, MCP & tài liệu dùng chung toàn hệ thống
│   ├── rules/
│   │   └── m2m-protocol.md          # Giao thức M2M tiết kiệm token cực hạn, Inherit Model
│   ├── docs/
│   │   └── project-onboarding.md    # Hướng dẫn tạo nhóm agent cho dự án mới
│   ├── mcp/
│   │   └── web-search-interactive/  # MCP Server Dual-Engine (Fast HTTP + Playwright Browser)
│   └── skills/
│       └── web-search-interactive/  # Kỹ năng tìm kiếm và tự động hóa trình duyệt toàn cục
├── rules/                           # Rules toàn cục tự động nhận diện
│   └── m2m-protocol.md
├── projects/                        # Các nhóm Agent chuyên biệt theo từng dự án
│   ├── dental-project/              # Dự án Phòng Khám Nha Khoa Minh Sinh
│   │   ├── README.md
│   │   ├── knowledge/
│   │   │   └── tech-stack.md        # Cấu hình Tech Stack, quy chuẩn Docker, UI/UX
│   │   ├── rules/
│   │   │   └── dental-rules.md
│   │   └── skills/                  # Bộ 5 Lead Agents cho Nha Khoa
│   │       ├── pm-orchestrator/     # dental-pm-orchestrator
│   │       ├── lead-architect/      # dental-lead-architect
│   │       ├── lead-frontend/       # dental-lead-frontend
│   │       ├── lead-backend/        # dental-lead-backend
│   │       └── lead-qa/             # dental-lead-qa
│   ├── pc-builder/                  # Dự án Chuyên gia Tư vấn & Build PC
│   │   ├── README.md
│   │   ├── knowledge/
│   │   │   ├── tech-stack.md        # Workload sizing (Data Science, Docker, AI, Gaming)
│   │   │   ├── hardware-compatibility.md # Ma trận tương thích CPU/Mainboard/PSU
│   │   │   └── vietnam-retailers.md # Danh bạ web & link build PC Việt Nam
│   │   ├── rules/
│   │   │   └── pc-rules.md          # Quy chuẩn phần cứng không nghẽn cổ chai
│   │   └── skills/
│   │       └── pc-builder/          # pc-builder skill (kèm script tính PSU & link build)
│   └── _template/                   # Template mẫu chuẩn sẵn sàng nhân bản
│       ├── README.md
│       ├── knowledge/
│       ├── rules/
│       └── skills/
├── skills.json                      # Đăng ký các nhóm skill active cho Antigravity
└── README.md                        # Tài liệu tổng quan
```

---

## ⚡ 5 Nguyên Tắc Cốt Lõi (Core Principles)

1. **Docker-First (Bảo vệ Máy Host):**
   - Mọi thao tác kiểm tra DB, chạy linter, chạy test, build hoặc install package **BẮT BUỘC** chạy bên trong Docker container. Tuyệt đối không làm ô nhiễm môi trường máy gốc.
2. **Giao tiếp M2M Zero-Fat (Siêu tiết kiệm Token):**
   - Các Agent giao tiếp nội bộ chỉ bằng Cờ Tín Hiệu (`[ACK]`, `[STATUS: DONE]`, `[SPEC_CHANGED]`, `[STATUS: ESCALATE]`). Không chào hỏi dài dòng.
   - Khi có lỗi, QA chỉ ghi traceback ra file log và gửi đường dẫn, cấm dán log dài vào context chat.
3. **Đồng bộ Model (Model Inherit):**
   - Mọi Sub-agent được spawn đều kế thừa chính xác Model gốc của User (ví dụ: Gemini 3.1 Pro Low / Gemini 3.8 Flash), tối ưu chi phí và tính nhất quán.
4. **Shift-Left Testing & Escape Hatch:**
   - Frontend & Backend bắt buộc tự chạy linter và fix lỗi nội bộ trước khi bàn giao cho QA.
   - Nếu tự fix quá 3 lần không xong, kích hoạt nút thoát hiểm `[STATUS: ESCALATE]` để xin ý kiến con người, chống lặp vô tận đốt token.
5. **Auto-Cleanup:**
   - Mọi file script dùng 1 lần (one-off scratch scripts) sinh ra trong quá trình dev/test phải được tự động dọn sạch.

---

## 🚀 Danh Sách Dự Án Đang Hoạt Động

### 1. Dự án Minh Sinh Dental (`dental_project`)
- **Đường dẫn code:** `d:\Thành\WEB\Code\dental_project`
- **Bộ Skills:**
  - `dental-pm-orchestrator`: Nhận yêu cầu, điều phối luồng, kiểm soát QA Loop, KHÔNG tự commit code.
  - `dental-lead-architect`: Thiết kế schema DB trong Docker, sinh OpenAPI spec, Security Gate.
  - `dental-lead-frontend`: Dàn trang Mobile-First, tự sinh API client từ OpenAPI, linter trong Docker.
  - `dental-lead-backend`: Xây dựng API, cấu hình CORS/Security, DB Seeding dữ liệu giả, linter trong Docker.
  - `dental-lead-qa`: Chạy E2E test trong Docker, code review, tear-down dữ liệu rác, dọn script tạm.

### 2. Dự án Tư Vấn & Build Cấu Hình PC (`pc-builder`)
- **Đường dẫn dự án:** `projects/pc-builder`
- **Bộ Skills & Công cụ:**
  - `pc-builder`: Phân bổ ngân sách, kiểm tra tương thích phần cứng, tính công suất nguồn chuẩn và kết hợp tầng web realtime để so sánh giá linh kiện ở các shop lớn.
  - `common/skills/web-search-interactive`: Kỹ năng toàn cục tìm kiếm web & duyệt trình duyệt tương tác.
  - `common/mcp/web-search-interactive`: MCP Server Dual-Engine (Fast HTTP + Playwright/Chrome).

---

## ➕ Cách Tạo Nhóm Agent Cho Dự Án Mới

1. **Nhân bản thư mục `projects/_template`:**
   ```powershell
   Copy-Item -Path "projects\_template" -Destination "projects\<ten-du-an-moi>" -Recurse
   ```
2. **Điền thông tin công nghệ:**
   - Cập nhật đường dẫn code và framework trong `projects/<ten-du-an-moi>/knowledge/tech-stack.md`.
   - Đổi tiền tố `[PROJECT_NAME]` trong các file `SKILL.md` (ví dụ: `shop-pm-orchestrator`, `shop-lead-frontend`...).
3. **Đăng ký vào `skills.json`:**
   Thêm đường dẫn `projects/<ten-du-an-moi>/skills` vào file `.agents/skills.json`.
