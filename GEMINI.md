# Antigravity Workspace Directives (Auto-Active Memory)

## ⚡ CHỈ THỊ BẮT BUỘC: KÍCH HOẠT HỆ THỐNG AGENT & BẢO TOÀN TOKEN

### 1. Khẩu lệnh kích hoạt (`/agent-system` & "sử dụng hệ thống agent")
Khi người dùng gõ lệnh **`/agent-system`** hoặc nói **"sử dụng hệ thống agent"**:
- Ngay lập tức chuyển sang chế độ Master Agent điều phối tối cao, kích hoạt skill `agent-system` $\rightarrow$ `master-agent`.
- **CHỈ CÓ DUY NHẤT `master-agent`** được phép sử dụng ngôn ngữ tự nhiên để giao tiếp và báo cáo kết quả cho User.
- Toàn bộ Project PMs, Tech Leads và Workers cấp dưới **TUYỆT ĐỐI CẤM chat văn xuôi**, 100% bắt buộc dùng chuẩn M2M JSON Code Protocol.
- Toàn bộ thông tin agent chỉ được đọc và lưu tại **`D:\Thành\Agent`** duy nhất.
- Phân tích yêu cầu và định tuyến đến đúng Project PM:
  * Nha Khoa Minh Sinh $\rightarrow$ `dental-pm-orchestrator` (Django/React/Docker ports 80, 8000)
  * Vietjet Airflow $\rightarrow$ `vj-pm-orchestrator` (Airflow 2.10 DAGs, ports 8080, 5434)
  * Vietjet Ancillary $\rightarrow$ `vietjet-pm-orchestrator` (Databricks Medallion views)
  * PC Builder $\rightarrow$ `pc-builder` (Phần cứng PC & Giá linh kiện VN)
  * Vietjet BRD $\rightarrow$ `vietjet-brd-architect` (Tài liệu Word BRD chuẩn)
  * Dự án chung / mới $\rightarrow$ `lead-pm` (Universal PM Base)

### 2. Chính sách Code-Via-API (Rule 16 - CẤM ĐỐT TOKEN TRONG CHAT)
- **CẤM TUYỆT ĐỐI** việc tự sinh code dài (>30 dòng), JSON to, DDL, hoặc test scripts trực tiếp vào ngữ cảnh chat Antigravity gây phình to token.
- **BẮT BUỘC** offload 100% công việc sinh mã nguồn thô cho Gemini API Key Pool ngoài (7 Projects, 0 VNĐ):
  * Tác vụ đơn: `hub gemini --prompt "..." --out "<filepath>" --tier <auto|bulk|standard|deep|ultra>`
  * Tác vụ đa luồng: `hub gemini --batch <tasks.json>`
- **BẮT BUỘC** kiểm định chất lượng: `hub verify <filepath>`
- **BẮT BUỘC** kiểm tra endpoints: `hub smoke`

### 3. Giao tiếp Zero-Fat
- Không chat văn xuôi giải thích dài dòng.
- Báo cáo kết quả 1-2 câu kèm link file clickable và lượng token đã bảo toàn.
