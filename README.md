# Multi-Project Agent Hub (`.agents`)

Trung tâm quản lý và điều phối các nhóm **AI Agent chuyên biệt theo từng dự án**, tích hợp trực tiếp với Google Antigravity, Biệt đội Kỹ sư Toàn cục (Universal Squad), và Gemini Smart Key Pool (7 Projects).

---

## 🏗️ Cấu Trúc Hệ Thống Chi Tiết (Agent Architecture Map)

```text
.agents/
├── common/                               # Hạ tầng & Biệt đội Kỹ sư Dùng chung (Universal Squad)
│   ├── rules/
│   │   └── m2m-protocol.md               # Giao thức M2M, Zero-Fat & Bounded Fan-Out (Rule 1-15)
│   ├── scripts/                          # Bộ công cụ CLI dùng chung (hub, verify, gemini, fanout...)
│   └── skills/                           # 🌐 BIỆT ĐỘI KỸ SƯ TOÀN CỤC (UNIVERSAL SQUAD)
│       ├── agent-system/                 # Điều hành toàn hệ thống qua lệnh /agent-system
│       ├── master-agent/                 # Master Agent điều phối trung ương (Ngôn ngữ tự nhiên duy nhất)
│       ├── lead-pm/                      # Universal PM Orchestrator điều phối vòng đời Phase 0-4
│       ├── lead-ba/                      # Universal BA (Khảo sát repo, User Stories & AC)
│       ├── lead-architect/               # Universal Architect (Thiết kế DB Schema & OpenAPI)
│       ├── lead-backend/                 # Universal Backend Lead (API, DB Migration, Query Profiler)
│       ├── lead-frontend/                # Universal Frontend Lead (UI/UX Mobile-First, Mock Client)
│       ├── lead-qa/                      # Universal QA Lead (Test matrix E2E/Unit trong Docker)
│       ├── lead-cyber-security/          # Cyber Security Lead (Rà soát OWASP, Secret leak, RBAC)
│       ├── gitops-gatekeeper/            # GitOps Gatekeeper (Rà soát diff, soạn Conventional Commit)
│       └── web-search-interactive/       # Web Search Realtime & Playwright Browser Automation Tool
├── rules/
│   └── m2m-protocol.md                   # Rule kích hoạt tự động toàn cục
├── projects/                             # CÁC NHÓM AGENT & NGỮ CẢNH CHUYÊN BIỆT THEO DỰ ÁN
│   ├── dental-project/                   # 🦷 DỰ ÁN PHÒNG KHÁM NHA KHOA MINH SINH
│   │   ├── knowledge/ & rules/           # tech-stack.md, checkpoint.md, dental-rules.md
│   │   └── skills/
│   │       └── pm-orchestrator/          # PM Nha Khoa Minh Sinh (kết nối trực tiếp Universal Squad)
│   ├── pc-builder/                       # 💻 DỰ ÁN TƯ VẤN & BUILD CẤU HÌNH PC
│   │   ├── knowledge/ & rules/           # hardware-compatibility.md, vietnam-retailers.md, pc-rules.md
│   │   └── skills/
│   │       └── pc-builder/               # Chuyên gia Phần cứng PC & So sánh giá linh kiện VN
│   ├── vietjet-airflow/                  # ✈️ DỰ ÁN HẠ TẦNG DỮ LIỆU VIETJET AIRFLOW
│   │   ├── knowledge/ & rules/           # tech-stack.md, checkpoint.md, airflow-rules.md
│   │   ├── schemas/ & templates/         # dag_spec.json, vietjet_dag_base.py
│   │   └── skills/
│   │       └── vj-pm-orchestrator/       # PM Vietjet Airflow (kết nối trực tiếp Universal Squad)
│   ├── vietjet-ancillary/                # 📊 DỰ ÁN DOANH THU PHỤ TRỢ & DI TRÚ DATABRICKS
│   │   ├── knowledge/ & rules/           # Thuật ngữ PSS, chính sách hoa hồng KPI, checkpoint.md
│   │   └── skills/
│   │       ├── pm-orchestrator/          # PM điều phối nghiệp vụ Ancillary
│   │       ├── code-analyzer/            # Bóc tách Stored Procedures sang Databricks Medallion
│   │       ├── policy-reader/            # Trích xuất ma trận đơn giá hoa hồng từ Tờ trình KPI
│   │       ├── catalog-inspector/        # Đối chiếu Master Data danh mục phụ trợ hàng không
│   │       └── excel-builder/            # Tự động xuất báo cáo Excel 2 tầng header chuẩn Vietjet
│   ├── vietjet-brd/                      # 📑 DỰ ÁN TỰ ĐỘNG HÓA SOẠN THẢO BRD VIETJET
│   │   ├── templates/ & scripts/         # Engine sinh file docx, master template Vietjet chuẩn
│   │   └── skills/
│   │       └── vietjet-brd-architect/    # Chuyên gia soạn thảo tài liệu Word BRD Vietjet
│   ├── agent-supervisor/                 # 🛡️ NHÓM GIÁM SÁT, ĐO ĐẠC TOKEN & TỐI ƯU HỆ THỐNG
│   │   ├── knowledge/ & reports/         # evaluation-metrics.md, lịch sử báo cáo kiểm toán
│   │   └── skills/
│   │       ├── supervisor-orchestrator/  # Chánh thanh tra điều phối kiểm toán hiệu năng
│   │       ├── token-cost-profiler/      # Bóc tách và định lượng tokens từ transcript JSONL
│   │       ├── performance-evaluator/    # Đánh giá độ trễ và tỷ lệ lỗi QA loop
│   │       └── skill-meta-optimizer/     # Tối ưu hóa prompt & thu hoạch reusable scripts
│   └── _template/                        # 📦 MẪU CHUẨN SẴN SÀNG 1-CLICK NHÂN BẢN
│       └── skills/
│           └── pm-orchestrator/          # PM mẫu kế thừa Universal Squad cho dự án mới
├── hub.bat                               # Central CLI Launcher cho Windows CMD
├── hub.ps1                               # Central CLI Launcher cho Windows PowerShell
├── skills.json                           # Registry đăng ký 24 kỹ năng với Antigravity
└── README.md
```

---

## 📋 Bảng Danh Mục Toàn Bộ 23 Agent & Công Cụ Theo Chuyên Môn

| STT | Tên Agent (Skill Identifier) | Vị Trí / Nhóm | Vai Trò & Chuyên Môn Cốt Lõi |
| :---: | :--- | :--- | :--- |
| **0** | `agent-system` | Universal Squad | **Lệnh `/agent-system`**: Khởi động trung tâm điều hành Multi-Agent & ép offload API |
| **1** | `master-agent` | Universal Squad | Master Agent điều phối trung ương, đầu mối duy nhất giao tiếp ngôn ngữ tự nhiên |
| **2** | `lead-pm` | Universal Squad | Universal PM Orchestrator điều phối toàn diện vòng đời phát triển Phase 0-4 |
| **3** | `lead-ba` | Universal Squad | Khảo sát mã nguồn, sinh `tech-stack.md`, bóc tách User Stories & AC |
| **4** | `lead-architect` | Universal Squad | Thiết kế kiến trúc hệ thống, DB Schema, chuẩn hóa OpenAPI / Schemas |
| **5** | `lead-backend` | Universal Squad | Lập trình API REST/GraphQL, DB Migration, chống N+1 query trong Docker |
| **6** | `lead-frontend` | Universal Squad | Thiết kế UI/UX Mobile-First, tự sinh API client, chạy Mock Server |
| **7** | `lead-qa` | Universal Squad | Chạy ma trận kiểm thử E2E/Unit trong Docker, code review, linter |
| **8** | `lead-cyber-security` | Universal Squad | Rà soát OWASP Top 10, quét lọt lộ Secret/API keys, audit phụ thuộc |
| **9** | `gitops-gatekeeper` | Universal Squad | Gác cổng Git, rà soát diff, soạn Conventional Commit chuẩn mực |
| **10** | `dental-pm-orchestrator` | Minh Sinh Dental | PM điều phối nha khoa (Domain Adapter kế thừa `lead-pm`, kết nối Universal Squad) |
| **11** | `pc-builder` | PC Hardware | Chuyên gia tư vấn cấu hình PC, kiểm tra tương thích và so sánh giá VN |
| **12** | `vj-pm-orchestrator` | Vietjet Airflow | PM hạ tầng dữ liệu và Airflow Pipelines (Domain Adapter kế thừa `lead-pm`) |
| **13** | `vietjet-pm-orchestrator`| Vietjet Ancillary | PM điều phối Ancillary & Databricks (Domain Adapter kế thừa `lead-pm`) |
| **14** | `code-analyzer` | Vietjet Ancillary | Bóc tách Stored Procedures Oracle sang Databricks PySpark Medallion |
| **15** | `policy-reader` | Vietjet Ancillary | Đọc hiểu Tờ trình KPI hoa hồng sân bay (Counter vs Gate) |
| **16** | `catalog-inspector` | Vietjet Ancillary | Đối chiếu Master Data danh mục phụ trợ (suất ăn, hành lý, chọn ghế) |
| **17** | `excel-builder` | Vietjet Ancillary | Xuất báo cáo tài chính Excel 2 tầng header chuẩn nhận diện Vietjet |
| **18** | `vietjet-brd-architect` | Vietjet BRD | Tự động hóa soạn thảo tài liệu Word BRD chuẩn nhận diện Vietjet Air |
| **19** | `supervisor-orchestrator`| Agent Supervisor | Chánh thanh tra điều phối Post-Run Audit, chấm điểm hiệu năng |
| **20** | `token-cost-profiler` | Agent Supervisor | Đo lường chi tiết Input/Output/Thinking tokens qua transcript log |
| **21** | `performance-evaluator` | Agent Supervisor | Đo đạc độ trễ, tỷ lệ lỗi công cụ và số chu kỳ QA loop |
| **22** | `skill-meta-optimizer` | Agent Supervisor | Tối ưu hóa prompt, nén token và thu hoạch reusable scripts |
| *Tool*| `web-search-interactive`| Global Utility | Tìm kiếm Google Realtime & tự động hóa trình duyệt tương tác |

---

## 🚀 Bảng Lệnh Tiện Ích (`hub` / `hub.ps1`)

| Lệnh | Mô tả | Script thực thi |
| :--- | :--- | :--- |
| `hub status` | Xem dashboard tiến độ Git & checkpoint tất cả dự án | `hub_status.py` |
| `hub doctor` | Bác sĩ kiểm toán Docker, ports, Git, token watchdog | `hub_doctor.py` |
| `hub smoke` | Kiểm tra tức thì (0.5s) HTTP/TCP endpoints toàn bộ dịch vụ & containers | `smoke_test_runner.py` |
| `hub gemini` | Chạy tác vụ nặng qua Gemini API ngoài (0đ, 7 keys pool, `--batch` đa luồng) | `gemini_offloader.py` |
| `hub usage` | Bảng điều khiển & theo dõi hạn mức quota 7 keys và từng model | `gemini_offloader.py` |
| `hub verify [file]` | Cổng kiểm định chất lượng, cú pháp AST, YAML, Dockerfile & bảo mật code | `output_verifier.py` |
| `hub fanout [args]` | Lập kế hoạch phân rã N sub-agent & tầng API theo độ phức tạp | `task_fanout_planner.py` |
| `hub clean [path]` | Quét dọn script tạm và ảnh rác Playwright (Rule 11) | `hub_cleaner.py` |
| `hub lint [path]` | Kiểm tra cú pháp Python/JSON, quét lộ secret keys | `linter_guard.py` |
| `hub mock [spec]` | Bật Instant API Mock Server với CORS & CRUD tự động | `mock_server_launcher.py` |
| `hub db-profile [log]` | Phân tích truy vấn SQL chậm (>100ms) và lỗi lặp N+1 | `db_query_profiler.py` |
| `hub test [path]` | Chạy ma trận kiểm thử đa tầng trong Docker | `test_matrix_runner.py` |
| `hub changelog [repo]`| Tự động tạo Release Notes từ Conventional Commits | `release_notes_builder.py` |
| `hub drift` | Kiểm tra lệch chuẩn API giữa Backend Code và OpenAPI Spec | `api_drift_detector.py` |
| `hub notify` | Bắn thông báo sự cố qua Telegram/Discord/Slack | `notify_dispatcher.py` |
| `hub token-opt` | Đo lường điểm nóng và nén tối ưu token sử dụng | `token_optimizer.py` |
| `hub create` | Khởi tạo 1-click nhóm agent cho dự án mới | `create_project.py` |
| `hub validate` | Kiểm tra tính toàn vẹn 100% của toàn bộ hệ thống | `validate_system.py` |

---

## ⚡ Nguyên Tắc Vận Hành Cốt Lõi (M2M Protocol)

1. **Docker-First:** Mọi thao tác build, test, lint, migrations BẮT BUỘC thực thi trong Docker container.
2. **Giao tiếp Zero-Fat:** Agent chỉ trao đổi tín hiệu M2M (`[ACK]`, `[STATUS: DONE]`, `[STATUS: ESCALATE]`) và JSON payload tối giản.
3. **Phân Tầng Bậc 3 (Bounded Fan-Out):**
   - Executive (Master / PM) $\rightarrow$ Tech Lead (có quyền sinh $N \le 5$ Workers) $\rightarrow$ Worker (bị khóa cứng `EnableSubagentTools: false`, không đẻ tiếp cấp 4).
4. **API Offloader & 7 Keys Pool:** Đẩy tác vụ nặng/lặp lại sang Gemini API ngoài (0đ, 7 cloud projects, 100k+ req/ngày) để bảo toàn quota Antigravity.
5. **Cổng Thẩm Định Chất Lượng:** Output code sinh ra bắt buộc qua `hub verify` (kiểm tra cú pháp AST, bảo mật, bóc tách code sạch) trước khi Lead nghiệm thu.
6. **Git Là Nguồn Chân Lý Duy Nhất (SSoT):** Trạng thái được đọc trực tiếp từ Git repo và `checkpoint.md`. Không lưu file rác trên ổ cứng.
