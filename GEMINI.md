# Antigravity Workspace Directives (Auto-Active Core)

## 🌐 QUY TẮC NGÔN NGỮ (BẮT BUỘC TUYỆT ĐỐI)
- **LUÔN LUÔN PHẢN HỒI BẰNG TIẾNG VIỆT** cho Người Dùng — không có ngoại lệ, kể cả khi User viết tiếng Anh.
- Nội dung kỹ thuật (code, JSON, file path, CLI command) vẫn giữ nguyên định dạng gốc; chỉ phần giải thích & giao tiếp là Tiếng Việt.


## ⚡ CHỈ THỊ BẮT BUỘC: ÉP DÙNG API TỐI ĐA & BẢO TOÀN TOKEN

1. **Khẩu lệnh kích hoạt (`/master-agent`, `/agent-system`, "sử dụng hệ thống agent"):**
   - Kích hoạt `master-agent` làm đầu não điều phối duy nhất giao tiếp tự nhiên với User.
   - Mọi PM, Tech Lead, Worker cấp dưới **TUYỆT ĐỐI CẤM** chat văn xuôi, 100% dùng chuẩn M2M JSON Code Protocol.
   - Toàn bộ dữ liệu agent chỉ lưu tại `D:\Thành\Agent` duy nhất.

2. **Ép Sử Dụng API Lên Mức Tối Đa (Rule 16 - CẤM ĐỐT TOKEN TRONG CHAT):**
   - **CẤM TUYỆT ĐỐI** tự sinh code, serializers, views, test suite, mock data, regex, DDL trực tiếp trong chat.
   - **100% MÃ NGUỒN PHẢI SINH QUA API NGOÀI (7 Projects Free Tier 0 VNĐ):**
     * Đơn lẻ: `hub gemini --prompt "..." --out "<filepath>" --tier <auto|bulk|standard|deep|ultra|embed|robotics|tts|transcribe|live_translate|live_dialog|live_thinking>`
     * Đa luồng: `hub gemini --batch <tasks.json>`
     * Thẩm định: `hub verify <filepath>` (đạt 100/100 Quality Gate) | Kiểm thử: `hub smoke`
   - **Cơ Chế Auto-Triage & Đánh Giá Tự Động:**
     * Tự động phân tích prompt để chọn đúng Tier tối ưu (Live Translate, Live Audio Dialog, Live Extended Thinking, Transcribe, Deep, Standard, Bulk, Ultra).
     * Tận dụng tối đa các model Live API với Unlimited RPD & Unlimited RPM từ Google AI Studio cho tác vụ âm thanh, video, bóc băng, dịch trực tiếp.
   - **Phân Vai Subagent (Code Reviewer & Storekeeper - BẢO TOÀN TOKEN CONTEXT):**
     * Subagent tuyệt đối không sinh code trong chat hoặc tự viết hàng nghìn dòng qua `write_file`.
     * Mọi mã nguồn bắt buộc gọi qua API ngoài: `hub gemini --prompt "..." --out "<filepath>"`.
     * Nếu API tự ghi file qua `--out`: Subagent chỉ thẩm định cú pháp qua `hub verify` hoặc `python -m py_compile`.
     * Nếu API không thể tự ghi file trực tiếp: Subagent chỉ nhận luồng stream/kết quả từ API, review cú pháp, lưu vào đúng tệp dự án trên đĩa, TUYỆT ĐỐI CẤM in lại nội dung code vào khung chat context.
     * Báo cáo M2M lên Agent cấp cao hơn chỉ chứa JSON tóm tắt 3 dòng: `{"status": "SUCCESS", "file": "<filepath>", "verification": "PASS"}`.

3. **Chốt Chặn Output Terminal (Hard-Limit Cấm Dump Context):**
   - Mọi lệnh terminal (`run_command`) khi quét file, xem log, chạy test, build, Docker BẮT BUỘC pipe qua `| Select-Object -First 30`, `tail -n 30`, hoặc `peek_data.py`.
   - TUYỆT ĐỐI CẤM in > 30 dòng output vào context chat. Nếu có lỗi dài (Docker build, pytest, compiler), BẮT BUỘC chuyển hướng ra file log tạm (vd: `> logs/build_error.log 2>&1`) và chỉ gửi đường dẫn file log kèm mã lỗi M2M: `[STATUS: FAIL] {"log_file": "logs/build_error.log"}`.

4. **Kỷ Luật Phản Hồi Zero-Fat & Token Budget Watchdog:**
   - Trả lời tối đa 2-3 câu súc tích kèm clickable links đến file đã tạo. CẤM in lại khối code vào chat.
   - **Token Watchdog (120,000 Tokens):** Khi phiên chạm ngưỡng 120,000 tokens, tự động kích hoạt **Hyper-Zero-Fat Mode** — CẤM toàn bộ giải thích văn xuôi, 100% trả về JSON đường dẫn file kết quả.

5. **Quy Tắc Zero-Execution Trong Main Chat & Bắt Buộc Ủy Thác Đúng Subagent (Rule 19 - BẢO TOÀN TOÀN BỘ QUOTA 5H):**
   - **CẤM TUYỆT ĐỐI Master Agent tự thực thi tác vụ dự án trong Main Chat:**
     * **CẤM** đọc file mã nguồn của dự án vào Main Chat (không gọi `read_file` trên code dự án).
     * **CẤM** tự sửa file mã nguồn dự án trong Main Chat (không `edit_file` / `write_file` trên code dự án).
     * **CẤM** tự chạy lệnh Docker, build, test, migrate của dự án trong Main Chat.
     * **CẤM TUYỆT ĐỐI DÙNG `schedule` HOẶC VÒNG LẶP ĐỂ POLLING** trong Main Chat (hành vi gây lặp context và đốt sạch token quota 5h!).
   - **MASTER AGENT CHỈ ĐƯỢC PHÉP LÀM 4 BƯỚC ĐIỀU PHỐI DUY NHẤT:**
     1. Nhận diện dự án từ prompt User theo Routing Matrix.
     2. Đọc `projects/<project>/knowledge/checkpoint.md` nếu cần nắm tiến độ ngắn gọn.
     3. Gọi `hub shard auto "<prompt>"` để nạp đúng shard dự án.
     4. **GỌI NGAY `invoke_subagent` CHỌN ĐÚNG SUBAGENT PM DỰ ÁN** (như `dental-pm-orchestrator`, `vj-pm-orchestrator`, `translate-pm-orchestrator`, v.v. với `Workspace: "inherit"`) và **DỪNG LẠI NGAY LẬP TỨC** (kết thúc lượt gọi tool). Hệ thống tự động kích hoạt lại qua **Reactive Wakeup** khi Subagent gửi tin nhắn M2M xong — KHÔNG ĐƯỢC POLLING!
     5. Khi nhận tin nhắn M2M kết quả từ Subagent: Báo cáo súc tích 2-3 câu Tiếng Việt kèm liên kết file cho User, gọi `hub shard reset` và kết thúc.
   - **TOÀN BỘ CÔNG VIỆC KỸ THUẬT SÂU:** Đọc code, sửa code qua Gemini API ngoài, chạy test/docker ĐỀU DO SUBAGENT THỰC HIỆN ĐỘC LẬP trong context con của Subagent, hoàn toàn cách ly với Main Chat!

## ⚡ QUY TẮC PHÂN MẢNH NGỮ CẢNH TỰ ĐỘNG (Rule 18)
- **TRƯỚC KHI thực thi bất kỳ task dự án nào:** BẮT BUỘC gọi `hub shard auto "<user_prompt>"` để chỉ nạp đúng context dự án tương ứng.
- **SAU KHI hoàn thành task:** BẮT BUỘC gọi `hub shard reset` để về shard `core` (tiết kiệm 89% token System Prompt).
- **CẤM** giữ shard dự án chuyên dụng (dental/vietjet/pc-builder/supervisor) sang lượt chat khác khi không còn thực thi dự án đó.
- Xem danh sách shard: `hub shard --list` | Chuyển thủ công: `hub shard set <id>`
