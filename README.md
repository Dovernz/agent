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
│       ├── master-secretary/        # Thư ký Toàn quyền điều phối tự động sang các dự án
│       ├── multiagent-requirement-to-excel/ # Phân tích yêu cầu nghiệp vụ phức tạp & tạo Excel
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
│   ├── vietjet-airflow/             # Dự án Hạ Tầng Dữ Liệu & Airflow Pipelines Vietjet
│   │   ├── README.md
│   │   ├── knowledge/
│   │   │   └── tech-stack.md        # Chuẩn Airflow 2.10, TaskFlow API, Timezone Asia/Ho_Chi_Minh
│   │   ├── rules/
│   │   │   └── airflow-rules.md     # Quy định Docker test & Zero-Fat M2M
│   │   ├── schemas/                 # JSON Schemas cho Spec & Test Report
│   │   ├── scripts/                 # Bộ kiểm thử siêu tốc (AST + Docker DagBag)
│   │   ├── templates/               # Template DAG TaskFlow chuẩn Vietjet
│   │   └── skills/                  # Bộ 4 Lead Agents cho Vietjet Airflow
│   │       ├── vj-pm-orchestrator/  # vj-pm-orchestrator
│   │       ├── vj-lead-architect/   # vj-lead-architect
│   │       ├── vj-lead-coder/       # vj-lead-coder
│   │       └── vj-lead-qa/          # vj-lead-qa
│   ├── vietjet-ancillary/           # Dự án Vietjet PSS Ancillary & Databricks Migration
│   │   ├── README.md
│   │   ├── knowledge/               # Thuật ngữ PSS, Taxonomy phụ thu, Tech Stack Databricks
│   │   ├── rules/                   # Quy định không hardcode, bảo toàn tài chính
│   │   └── skills/                  # Bộ 5 Lead Agents cho Ancillary & Databricks
│   └── _template/                   # Template mẫu chuẩn sẵn sàng nhân bản
│       ├── README.md
│       ├── knowledge/
│       ├── rules/
│       └── skills/
├── skills.json                      # Đăng ký các nhóm skill active cho Antigravity
└── README.md                        # Tài liệu tổng quan
```

---

## ⚡ 8 Nguyên Tắc Cốt Lõi (Core Principles)

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
5. **Auto-Cleanup & Peek-and-Script:**
   - Mọi file script dùng 1 lần (one-off scratch scripts) sinh ra trong quá trình dev/test phải được tự động dọn sạch.
   - Với file Excel/CSV, tuyệt đối cấm dump toàn bộ vào context chat, chỉ Peek 3 dòng mẫu và xử lý tổng hợp bằng script.
6. **Diệt Agent Treo & Chạy Quá Giờ (Timeout & Kill Zombie Sub-Agents):**
   - Mọi sub-agent và tác vụ nền đều có giới hạn thời gian chạy (ngưỡng 5-10 phút). Nếu sub-agent bị treo, hold quá lâu hoặc không phản hồi, PM BẮT BUỘC dùng ngay `manage_subagents` (`Action: "kill"`) hoặc `manage_task` (`Action: "kill"`) để diệt tiến trình, giải phóng tài nguyên và báo `[STATUS: ESCALATE]`.
7. **Cấm Đệ Quy Sub-Agent (No-Recursion Policy):**
   - Các sub-agent cấp con (Lead, Worker) được tạo ra mặc định **BỊ KHÓA** quyền tạo sub-agent (`EnableSubagentTools: false`). Tuyệt đối không tự ý phân nhánh đệ quy trừ khi có quy định đặc thù tại SKILL của Manager dự án.
8. **Chuẩn Hóa Giao Tiếp Nội Bộ Bằng Code & JSON:**
   - Thư ký (Master Secretary) và Project PMs giao tiếp 100% bằng JSON Code Payload (`EXECUTE_TASK`, `STATUS: DONE`), không trò chuyện văn bản qua lại để tiết kiệm token tối đa.

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

### 3. Dự án Hạ Tầng Dữ Liệu & Airflow Vietjet (`vietjet-airflow`)
- **Đường dẫn code:** `D:\Vietjet\Gitlab\vj-prod-airflow-cc`
- **Môi trường Test:** `D:\Vietjet\Gitlab\test`
- **Bộ Skills & Công cụ:**
  - `vj-pm-orchestrator`: Nhận yêu cầu, điều phối Spec -> Coder -> QA, kiểm soát QA Loop, đồng bộ Model inherit, KHÔNG tự commit code.
  - `vj-lead-architect`: Phân tích yêu cầu, sinh JSON AST Spec tối giản theo chuẩn M2M, xác định connection/hook/params.
  - `vj-lead-coder`: Sinh mã DAG Python Airflow TaskFlow API (`@dag`, `@task`) chuẩn Vietjet (múi giờ `Asia/Ho_Chi_Minh`, batch dates `Param`).
  - `vj-lead-qa`: Chạy kiểm thử đa tầng (AST, cycle detection và nạp DagBag trong container Docker `test-airflow-webserver-1`), Auto-Cleanup file tạm, xuất JSON log lỗi.

### 4. Dự án Vietjet PSS Ancillary & Databricks Migration (`vietjet-ancillary`)
- **Đường dẫn code:** `d:\Vietjet\2026\Tờ trình`
- **Tài liệu PSS & Stored Procedure:** `d:\Vietjet\Docs\PSS`
- **Bộ Skills & Công cụ:**
  - `vietjet-pm-orchestrator`: Nhận yêu cầu, điều phối 4 subagents, kiểm soát luồng tổng hợp.
  - `vietjet-code-analyzer`: Phân tích SP cũ, DDL views, bóc tách CTEs, thiết kế Databricks Medallion.
  - `vietjet-policy-reader`: Đọc hiểu tài liệu chính sách, trích xuất ma trận đơn giá hoa hồng.
  - `vietjet-catalog-inspector`: Thẩm định danh mục Master Data, thực hiện Gap Analysis.
  - `vietjet-excel-builder`: Tự động hóa xây dựng bảng tính Excel tổng hợp báo cáo.

### 5. Dự án Tự Động Hóa Soạn Thảo BRD Vietjet (`vietjet-brd`)
- **Đường dẫn BRD:** `D:\Vietjet\2026\COM - Sale Reports\BRD`
- **Tài liệu nguồn:** `D:\Vietjet\2026\COM - Sale Reports\20260108_REPORT REQUEST TO IT.xlsx`
- **Bộ Skills & Công cụ:**
  - `vietjet-brd-architect`: Agent chuyên trách phân tích và tự động soạn thảo tài liệu BRD chuẩn Vietjet.
  - `scripts/brd_builder.py`: Engine sinh file docx tự động từ JSON / Excel, bảo toàn 100% trang bìa, thủ tục A-F, font Times New Roman, màu đỏ `#EE0000`, xám `#D7D7D7`.
  - `scripts/excel_reader.py`: Script trích xuất spec yêu cầu trực tiếp từ file Excel sang BRD.
  - `templates/template_vietjet_brd.docx`: Master template chuẩn trích xuất từ tài liệu chính thức Vietjet.

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
