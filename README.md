# Multi-Project Agent Hub (`.agents`)

Trung tâm quản lý và điều phối các nhóm **AI Agent chuyên biệt theo từng dự án**, tích hợp trực tiếp với Google Antigravity.

---

## 🏗️ Cấu trúc Hệ thống

```text
.agents/
├── common/                          # Giao thức, MCP, Scripts & Kỹ năng dùng chung toàn hệ thống
│   ├── rules/
│   │   └── m2m-protocol.md          # Giao thức M2M tiết kiệm token cực hạn, Checkpoint Protocol (Rule 1-10)
│   ├── docs/
│   │   ├── project-onboarding.md    # Hướng dẫn tạo nhóm agent cho dự án mới (1-Click & Manual)
│   │   └── architecture-blueprints.md # Kho lưu trữ thiết kế kiến trúc (Multi-agent to Excel, ...)
│   ├── scripts/                     # ♻️ Thư viện Script dùng chung toàn hệ thống
│   │   ├── hub_status.py            # Bảng điều khiển tiến độ, branch Git và checkpoint mọi dự án
│   │   ├── hub_doctor.py            # Bác sĩ toàn diện kiểm toán Docker, Git, Ports, Token budget
│   │   ├── hub_cleaner.py           # Dọn dẹp tự động scratch scripts & ảnh chụp màn hình Playwright
│   │   ├── linter_guard.py          # Chốt chặn kiểm tra cú pháp, ruff/eslint & secret leak trước khi commit/test
│   │   ├── mock_server_launcher.py  # Khởi chạy Instant API Mock Server từ OpenAPI spec (hỗ trợ CORS & CRUD)
│   │   ├── qa_report_builder.py     # Xuất báo cáo nghiệm thu Markdown kèm bằng chứng hình ảnh 1-click
│   │   ├── dependency_patcher.py    # Quét & tự động nâng cấp phiên bản an toàn cho requirements/npm
│   │   ├── env_guardian.py          # Kiểm toán .env vs .env.example & quét phát hiện rò rỉ secret
│   │   ├── mock_data_generator.py   # Máy sinh dữ liệu mồi đa nghiệp vụ (Dental, Airflow, Ecommerce)
│   │   ├── git_safe_snapshot.py     # Tạo snapshot & tự động hoàn nguyên (rollback) an toàn mã nguồn
│   │   ├── create_project.py        # Khởi tạo dự án mới 1-click (Auto-scan, Setup PM, Test scaffold)
│   │   ├── scan_repo_techstack.py   # Khảo sát codebase, Docker, dependencies & sinh tech-stack.md
│   │   ├── docker_doctor.py         # Kiểm toán Docker, phát hiện & giải phóng cổng 80/8000/3000...
│   │   ├── peek_data.py             # Peek 3 dòng mẫu dữ liệu lớn, tiết kiệm 99% token
│   │   └── validate_system.py       # Kiểm tra tính toàn vẹn 100% của toàn bộ hệ thống Agent
│   ├── mcp/
│   │   └── web-search-interactive/  # MCP Server Dual-Engine (Fast HTTP + Playwright Browser)
│   └── skills/
│       ├── master-secretary/        # Thư ký Toàn quyền điều phối tự động sang các dự án
│       ├── lead-ba/                 # Universal: Chuyên gia Phân tích Nghiệp vụ, Tech Stack & Living Doc
│       ├── web-search-interactive/  # Kỹ năng tìm kiếm và tự động hóa trình duyệt toàn cục
│       ├── lead-architect/          # Universal: Kiến trúc sư trưởng thiết kế hệ thống & OpenAPI Spec
│       ├── lead-frontend/           # Universal: Trưởng nhóm Frontend UI/UX Mobile-First
│       ├── lead-backend/            # Universal: Trưởng nhóm Backend API, DB & Migration trong Docker
│       ├── lead-qa/                 # Universal: Trưởng nhóm QA kiểm thử Shift-Left trong Docker
│       ├── lead-cyber-security/     # Universal: Trưởng nhóm An toàn thông tin, SAST & Secret Audit
│       └── gitops-gatekeeper/       # Universal: Gác cổng Git & Review bảo mật trước khi commit
├── rules/                           # Rules toàn cục tự động nhận diện
│   └── m2m-protocol.md
├── projects/                        # Các nhóm Agent & Context chuyên biệt theo từng dự án
│   ├── dental-project/              # Dự án Phòng Khám Nha Khoa Minh Sinh
│   │   ├── README.md
│   │   ├── knowledge/
│   │   │   ├── tech-stack.md        # Cấu hình Tech Stack, quy chuẩn Docker, UI/UX
│   │   │   └── checkpoint.md        # Ghi nhớ ngữ cảnh xuyên phiên, tiến độ kiểm thử
│   │   ├── rules/
│   │   │   └── dental-rules.md
│   │   └── skills/                  # PM điều phối (kết nối Universal Dev & Security Squad)
│   │       └── pm-orchestrator/     # dental-pm-orchestrator
│   ├── pc-builder/                  # Dự án Chuyên gia Tư vấn & Build PC
│   │   ├── README.md
│   │   ├── knowledge/
│   │   │   ├── tech-stack.md        # Workload sizing (Data Science, Docker, AI, Gaming)
│   │   │   ├── hardware-compatibility.md # Ma trận tương thích CPU/Mainboard/PSU
│   │   │   ├── vietnam-retailers.md # Danh bạ web & link build PC Việt Nam
│   │   │   └── checkpoint.md        # Ghi nhớ cấu hình chốt & ngân sách
│   │   ├── rules/
│   │   │   └── pc-rules.md          # Quy chuẩn phần cứng không nghẽn cổ chai
│   │   └── skills/
│   │       └── pc-builder/          # pc-builder skill (kèm script tính PSU & link build)
│   ├── vietjet-airflow/             # Dự án Hạ Tầng Dữ Liệu & Airflow Pipelines Vietjet
│   │   ├── README.md
│   │   ├── knowledge/
│   │   │   ├── tech-stack.md        # Chuẩn Airflow 2.10, TaskFlow API, Timezone Asia/Ho_Chi_Minh
│   │   │   └── checkpoint.md        # Ghi nhớ trạng thái DAGs & Docker DagBag
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
│   │   ├── knowledge/               # Thuật ngữ PSS, Taxonomy phụ thu, Tech Stack Databricks, checkpoint.md
│   │   ├── rules/                   # Quy định không hardcode, bảo toàn tài chính
│   │   └── skills/                  # Bộ 5 Lead Agents cho Ancillary & Databricks
│   ├── vietjet-brd/                 # Dự án Tự Động Hóa Soạn Thảo BRD Vietjet
│   │   ├── README.md
│   │   ├── knowledge/               # Chuẩn BRD, Từ điển domain Vietjet, checkpoint.md
│   │   ├── rules/                   # Quy chuẩn soạn thảo Word chuẩn nhận diện
│   │   ├── scripts/                 # Engine sinh file docx tự động
│   │   ├── templates/               # Master docx template chuẩn
│   │   └── skills/                  # vietjet-brd-architect skill
│   ├── agent-supervisor/            # Nhóm Giám Sát, Đo Đạc Token & Tối Ưu Hóa Kỹ Năng
│   │   ├── README.md
│   │   ├── knowledge/               # evaluation-metrics.md
│   │   ├── rules/                   # supervisor-rules.md
│   │   ├── scripts/                 # audit_performance.py
│   │   ├── reports/                 # Lịch sử các báo cáo kiểm toán audit_report_*.md
│   │   └── skills/                  # 4 Lead Agents kiểm toán & tối ưu
│   └── _template/                   # Template mẫu chuẩn sẵn sàng nhân bản cho dự án mới
│       ├── README.md
│       ├── knowledge/
│       │   ├── tech-stack.md        # Khai báo tech stack riêng của dự án mới
│       │   └── checkpoint.md        # Tệp ghi nhớ ngữ cảnh ban đầu
│       ├── rules/
│       └── skills/
│           └── pm-orchestrator/     # PM chuyên biệt kế thừa Universal Dev Squad
├── skills.json                      # Đăng ký các nhóm skill active cho Antigravity
└── README.md                        # Tài liệu tổng quan
```

---

## ⚡ 12 Nguyên Tắc Cốt Lõi (Core Principles)

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
9. **Giám Sát Hạn Mức Token & Chế Độ Siêu Tinh Gọn (Token Budget Watchdog & Hyper-Zero-Fat):**
   - Giám sát tổng dung lượng token trong phiên làm việc. Khi phiên vượt ngưỡng cảnh báo (120,000 tokens), hệ thống tự động kích hoạt chế độ **Hyper-Zero-Fat**:
     - Cắt bỏ hoàn toàn các câu giải thích phụ trợ;
     - Tất cả các agent chỉ trả về duy nhất payload JSON code tối giản (`status`, `result`, `error`);
     - Tối đa hóa việc đẩy dữ liệu trung gian vào file scratch/log trên đĩa thay vì in ra ngữ cảnh.
10. **Bàn Giao Ngữ Cảnh Xuyên Phiên (Cross-Session Checkpoint Protocol):**
    - Mỗi dự án bắt buộc duy trì `knowledge/checkpoint.md`.
    - Khi kết thúc phiên: PM / BA cập nhật trạng thái, tính năng vừa xong và 2-3 bước ưu tiên kế tiếp.
    - Khi mở phiên mới: Master Secretary hoặc PM đọc ngay `knowledge/checkpoint.md` để khôi phục tiến độ 100% mà không cần User giải thích lại.
11. **Tự Động Dọn Dẹp Tập Tin Rác & Ảnh Chụp Màn Hình (Workspace Hygiene & Auto-Cleanup):**
    - Cấm lưu các script tạm chạy 1 lần (`tmp_*.py`, `debug_*.py`, `qa_inspect*.py`) và ảnh chụp màn hình Playwright (`.png`, `.jpg`) trong mã nguồn dự án.
    - Ảnh chụp màn hình dùng làm bằng chứng nghiệm thu bắt buộc lưu vào thư mục Artifacts của Antigravity (`brain/<conversation-id>/`).
    - Trước khi bàn giao và commit, `lead-qa` và `gitops-gatekeeper` tự động kích hoạt `hub_cleaner.py --clean` để quét sạch toàn bộ rác mã nguồn.
12. **Git Là Nguồn Chân Lý Duy Nhất (Git-As-Single-Source-Of-Truth - SSoT):**
    - Toàn bộ tiến độ dự án, commit hash và checkpoint lịch sử được đọc trực tiếp 100% từ thư mục Git (`projects/<project>/knowledge/checkpoint.md`, `git log -1`).
    - Không lưu dữ liệu trùng lặp hay cache trạng thái tạm ngoài luồng trên ổ cứng máy tính. Sau khi commit và push lên remote Git, máy tính chỉ lưu giữ bản sao làm việc sạch sẽ của Git.

---

## 🌐 Đội Ngũ Dev, Nghiệp Vụ & Bảo Mật Toàn Cục (Universal Squad in `common/skills/`)

Được thiết kế theo kiến trúc tái sử dụng triệt để, không còn phụ thuộc cứng vào bất kỳ dự án đơn lẻ nào:
- **`lead-ba`**: Chuyên gia Phân tích Nghiệp vụ & Quản trị Ngữ cảnh Toàn cục (Universal BA & Living Doc). Tự động quét repo sinh `tech-stack.md`, bóc tách User Stories & Acceptance Criteria, đồng bộ tài liệu sống sau mỗi chu kỳ chạy.
- **`lead-architect`**: Đọc `tech-stack.md` của bất kỳ dự án nào để thiết kế DB Schema, API Specification (OpenAPI 3.0), System Architecture.
- **`lead-frontend`**: Thiết kế giao diện Mobile-First, tạo API Client từ OpenAPI spec, linter & format trong Docker.
- **`lead-backend`**: Thiết kế REST/GraphQL APIs, xử lý DB Migrations & Seeding an toàn, thiết lập CORS & Auth trong Docker.
- **`lead-qa`**: Chạy E2E / Unit testing tự động đa luồng trong Docker, code review, tear-down DB rác và dọn dẹp scratch script.
- **`lead-cyber-security`**: Chuyên gia An toàn thông tin phòng thủ (Defensive Cyber Security), rà soát lỗ hổng OWASP Top 10, quét lọt lộ Secret/API key, audit phụ thuộc (`npm audit`, `pip check`), kiểm tra CORS/CSP và đề xuất bản vá bảo mật.
- **`gitops-gatekeeper`**: Chuyên gia kiểm soát chất lượng Git, quét lọt lộ secret trước khi commit, đối chiếu status/diff và soạn thảo conventional commit message chuẩn xác.

---

## 🚀 Danh Sách Dự Án Đang Hoạt Động

### 1. Dự án Minh Sinh Dental (`dental-project`)
- **Đường dẫn code:** `d:\Thành\WEB\Code\dental_project`
- **Bộ Skills & Điều phối:**
  - `dental-pm-orchestrator`: Nhận yêu cầu, đọc `knowledge/tech-stack.md`, điều phối luồng thực thi xuống **Universal Dev & Security Squad**, kiểm soát QA Loop, ghi nhận `checkpoint.md`, KHÔNG tự commit code.

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
  - `vj-pm-orchestrator`: Nhận yêu cầu, điều phối Spec -> Coder -> QA, kiểm soát QA Loop, đồng bộ Model inherit, bàn giao qua `gitops-gatekeeper`, KHÔNG tự commit code.
  - `vj-lead-architect`: Phân tích yêu cầu, sinh JSON AST Spec tối giản theo chuẩn M2M, xác định connection/hook/params.
  - `vj-lead-coder`: Sinh mã DAG Python Airflow TaskFlow API (`@dag`, `@task`) chuẩn Vietjet (múi giờ `Asia/Ho_Chi_Minh`, batch dates `Param`).
  - `vj-lead-qa`: Chạy kiểm thử đa tầng (AST, cycle detection và nạp DagBag trong container Docker `test-airflow-webserver-1`), Auto-Cleanup file tạm, xuất JSON log lỗi.

### 4. Dự án Vietjet PSS Ancillary & Databricks Migration (`vietjet-ancillary`)
- **Đường dẫn code:** `d:\Vietjet\2026\Tờ trình`
- **Tài liệu PSS & Stored Procedure:** `d:\Vietjet\Docs\PSS`
- **Bộ Skills & Công cụ:**
  - `vietjet-pm-orchestrator`: Nhận yêu cầu, điều phối 4 subagents, kiểm soát luồng tổng hợp, bàn giao qua `gitops-gatekeeper`.
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

### 6. Nhóm Agent Giám Sát, Đo Đạc Token & Tối Ưu Kỹ Năng (`agent-supervisor`)
- **Đường dẫn:** `projects/agent-supervisor`
- **Báo cáo kiểm toán:** `projects/agent-supervisor/reports/`
- **Bộ Skills & Công cụ:**
  - `supervisor-orchestrator`: Chánh thanh tra điều phối kiểm toán hiệu năng sau phiên chạy, tính điểm chất lượng.
  - `token-cost-profiler`: Bóc tách và định lượng chính xác Input/Output/Thinking tokens từ transcript JSONL.
  - `performance-evaluator`: Đánh giá độ trễ thực thi, tỷ lệ lỗi công cụ, số chu kỳ lặp QA loop.
  - `skill-meta-optimizer`: Chuyên gia tối ưu hóa kỹ năng (Meta-Learning), đề xuất vá trực tiếp các tệp `SKILL.md`.
  - `scripts/audit_performance.py`: Engine tự động đọc log transcript, tính token và xuất báo cáo Markdown.

---

## ➕ Cách Tạo Nhóm Agent Cho Dự Án Mới

### Cách 1: Tự Động 1-Click (Khuyên Dùng)
Chạy script tự động hóa toàn bộ:
```powershell
uv run python D:\Thành\Agent\common\scripts\create_project.py --name "<ten-du-an>" --repo "<duong-dan-code>" --desc "<mo-ta-du-an>"
```
Script sẽ tự động nhân bản template, quét mã nguồn bằng `scan_repo_techstack.py`, tạo `tech-stack.md`, tạo `checkpoint.md`, và đăng ký vào cả `skills.json` của Agent Hub và `~/.gemini/config/skills.json`.

### Cách 2: Thủ Công
1. **Nhân bản thư mục `projects/_template`:**
   ```powershell
   Copy-Item -Path "projects\_template" -Destination "projects\<ten-du-an-moi>" -Recurse
   ```
2. **Khai báo Tech Stack và PM của dự án:**
   - Cập nhật thông tin đường dẫn code, framework, DB, Docker service trong `projects/<ten-du-an-moi>/knowledge/tech-stack.md`.
   - Cập nhật quy tắc đặc thù trong `projects/<ten-du-an-moi>/rules/`.
   - Cập nhật `pm-orchestrator` để tự động triệu hồi Universal Dev Squad.
3. **Đăng ký vào `skills.json`:**
   Thêm đường dẫn `projects/<ten-du-an-moi>/skills` vào file `.agents/skills.json`.
