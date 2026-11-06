# Multi-Project Agent Hub (`.agents`)

Trung tâm quản lý và điều phối các nhóm **AI Agent chuyên biệt theo từng dự án**, tích hợp trực tiếp với Google Antigravity và Biệt đội Kỹ sư Toàn cục (Universal Squad).

---

## 🏗️ Cấu Trúc Hệ Thống

```text
.agents/
├── common/
│   ├── rules/                # Giao thức M2M & Zero-Fat
│   ├── docs/                 # Tài liệu kiến trúc & onboarding
│   ├── scripts/              # Thư viện script CLI & công cụ tự động hóa dùng chung
│   ├── mcp/                  # MCP servers mở rộng (web-search-interactive)
│   └── skills/               # Universal Squad (Architect, Backend, Frontend, QA, BA, Cyber, GitOps)
├── rules/                    # Quy tắc kích hoạt tự động toàn cục (m2m-protocol.md)
├── projects/
│   ├── dental-project/       # Nha Khoa Minh Sinh (Django / React / Docker)
│   ├── pc-builder/           # Chuyên gia Tư vấn Cấu hình PC & Giá linh kiện
│   ├── vietjet-airflow/      # Hạ Tầng Dữ Liệu & DAG Pipelines Vietjet Air
│   ├── vietjet-ancillary/    # Doanh Thu Phụ Trợ PSS & Di Trú Databricks
│   ├── vietjet-brd/          # Soạn Thảo BRD Chuẩn Hãng Hàng Không Vietjet
│   ├── agent-supervisor/     # Giám Sát, Đo Đạc Token & Tối Ưu Hóa Kỹ Năng
│   └── _template/            # Template mẫu 1-click cho dự án mới
├── hub.bat                   # CLI Launcher cho Windows CMD
├── hub.ps1                   # CLI Launcher cho Windows PowerShell
├── skills.json               # Registry đăng ký kỹ năng với Antigravity
└── README.md
```

---

## 🚀 Bảng Lệnh Tiện Ích (`hub` / `hub.ps1`)

| Lệnh | Mô tả | Script thực thi |
| :--- | :--- | :--- |
| `hub status` | Xem dashboard tiến độ Git & checkpoint tất cả dự án | `hub_status.py` |
| `hub doctor` | Bác sĩ kiểm toán Docker, ports, Git, token watchdog | `hub_doctor.py` |
| `hub gemini` | Chạy tác vụ nặng qua Gemini API ngoài (0đ, 7 keys pool) | `gemini_offloader.py` |
| `hub verify [file]` | Cổng kiểm định chất lượng, cú pháp AST & bảo mật code | `output_verifier.py` |
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

## 🌐 Biệt Đội Kỹ Sư Toàn Cục (Universal Squad in `common/skills/`)

Được thiết kế dùng chung cho toàn bộ các dự án, không phụ thuộc vào công nghệ đơn lẻ:

- **`lead-ba`**: Phân tích nghiệp vụ, quét repo sinh `tech-stack.md`, bóc tách User Stories & AC chuẩn Gherkin.
- **`lead-architect`**: Thiết kế kiến trúc, DB Schema, chuẩn hóa đặc tả OpenAPI 3.0 / JSON Schemas.
- **`lead-backend`**: Lập trình API, xử lý DB Migrations & Seeding, chống lỗi N+1, tối ưu hiệu năng.
- **`lead-frontend`**: Thiết kế UI/UX Mobile-First, tự sinh API client từ spec, mock server độc lập.
- **`lead-qa`**: Kiểm thử Shift-Left, chạy test matrix E2E/Unit trong Docker, code review và dọn dẹp.
- **`lead-cyber-security`**: Rà soát OWASP Top 10, quét lọt lộ Secret/API key, audit phụ thuộc, vá bảo mật phòng thủ.
- **`gitops-gatekeeper`**: Gác cổng Git, rà soát diff, soạn Conventional Commit và release notes chuẩn mực.
- **`master-secretary`**: Thư ký điều phối trung ương, định tuyến yêu cầu thông minh giữa các dự án.

---

## 📁 Danh Sách Dự Án Đang Hoạt Động

### 1. Phòng Khám Nha Khoa Minh Sinh (`dental-project`)
- **Đặc tả:** Web app quản lý khám bệnh, đặt lịch, hồ sơ nha khoa (Django / React / Docker).
- **Điều phối:** `dental-pm-orchestrator` $\rightarrow$ phân việc xuống **Universal Squad** trong `common/skills/`.

### 2. Tư Vấn & Build Cấu Hình PC (`pc-builder`)
- **Đặc tả:** Chuyên gia phần cứng, kiểm tra tương thích linh kiện CPU/VGA/Mainboard, tính công suất nguồn PSU và so sánh giá bán lẻ Việt Nam qua web search.
- **Kỹ năng:** `pc-builder` + `web-search-interactive`.

### 3. Hạ Tầng Dữ Liệu Vietjet Airflow (`vietjet-airflow`)
- **Đặc tả:** Hạ tầng ETL dữ liệu lớn và quản lý pipelines Airflow 2.10 (TaskFlow API, múi giờ `Asia/Ho_Chi_Minh`, container Docker `test-airflow-webserver-1`).
- **Điều phối:** `vj-pm-orchestrator` $\rightarrow$ phân việc trực tiếp xuống **Universal Squad**:
  - `lead-architect`: Thiết kế DAG JSON spec.
  - `lead-backend`: Viết code TaskFlow theo `templates/vietjet_dag_base.py`.
  - `lead-qa`: Chạy test `fast_test_dag.py` trong Docker.
  - `lead-cyber-security`: Kiểm tra bí mật kết nối và hooks.

### 4. Doanh Thu Phụ Trợ & Di Trú Databricks (`vietjet-ancillary`)
- **Đặc tả:** Chuyên sâu nghiệp vụ hàng không: bóc tách Stored Procedures Oracle sang Databricks PySpark Medallion, đối chiếu danh mục phụ trợ (suất ăn, hành lý) và đọc chính sách KPI.
- **Kỹ năng Chuyên biệt:** `vietjet-pm-orchestrator`, `code-analyzer`, `policy-reader`, `catalog-inspector`, `excel-builder`.

### 5. Soạn Thảo Tài Liệu BRD Vietjet (`vietjet-brd`)
- **Đặc tả:** Tự động hóa soạn thảo tài liệu yêu cầu nghiệp vụ BRD định dạng Word (.docx) chuẩn nhận diện thương hiệu Vietjet Air từ prompt hoặc file Excel.
- **Kỹ năng:** `vietjet-brd-architect` (kèm template và engine sinh `.docx`).

### 6. Giám Sát, Đo Đạc Token & Tối Ưu Hệ Thống (`agent-supervisor`)
- **Đặc tả:** Giám sát chất lượng sau phiên chạy, đo đạc token tiêu thụ qua log transcript, phát hiện điểm nóng và đề xuất tối ưu hóa kỹ năng.
- **Kỹ năng Chuyên biệt:** `supervisor-orchestrator`, `token-cost-profiler`, `performance-evaluator`, `skill-meta-optimizer`.

---

## ⚡ Nguyên Tắc Vận Hành Cốt Lõi (M2M Protocol)

1. **Docker-First:** Mọi thao tác build, test, lint, migrations BẮT BUỘC thực thi trong Docker container.
2. **Giao tiếp Zero-Fat:** Agent chỉ trao đổi tín hiệu M2M (`[ACK]`, `[STATUS: DONE]`, `[STATUS: ESCALATE]`) và JSON payload tối giản.
3. **Phân Tầng Bậc 3 (Bounded Fan-Out):**
   - Executive (Master / PM) $\rightarrow$ Tech Lead (có quyền sinh $N \le 5$ Workers) $\rightarrow$ Worker (bị khóa cứng, không đẻ tiếp cấp 4).
4. **API Offloader & 7 Keys Pool:** Đẩy tác vụ nặng/lặp lại sang Gemini API ngoài (0đ, 7 cloud projects, 100k+ req/ngày) để bảo toàn quota Antigravity.
5. **Cổng Thẩm Định Chất Lượng:** Output code sinh ra bắt buộc qua `hub verify` (kiểm tra cú pháp AST, bảo mật, bóc tách code sạch) trước khi Lead nghiệm thu.
6. **Git Là Nguồn Chân Lý Duy Nhất (SSoT):** Trạng thái được đọc trực tiếp từ Git repo và `checkpoint.md`. Không lưu file rác trên ổ cứng.
