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
     * Đơn lẻ: `hub gemini --prompt "..." --out "<filepath>" --tier <auto|bulk|standard|deep|ultra>`
     * Đa luồng: `hub gemini --batch <tasks.json>`
     * Thẩm định: `hub verify <filepath>` (đạt 100/100 Quality Gate) | Kiểm thử: `hub smoke`

3. **Chốt Chặn Output Terminal (Cấm Dump Context):**
   - Khi chạy lệnh xem log, quét file: BẮT BUỘC dùng `Select-Object -First 30`, `tail -n 30`, `peek_data.py`. Cấm in > 30 dòng.

4. **Kỷ Luật Phản Hồi Zero-Fat:**
   - Trả lời tối đa 2-3 câu súc tích kèm clickable links đến file đã tạo. CẤM in lại khối code vào chat.

5. **Quy Tắc Zero-Execution Trong Main Chat & Bắt Buộc Ủy Thác Đúng Subagent (Rule 19 - BẢO TOÀN TOÀN BỘ QUOTA 5H):**
   - **CẤM TUYỆT ĐỐI Master Agent tự thực thi tác vụ dự án trong Main Chat:**
     * **CẤM** đọc file mã nguồn của dự án vào Main Chat (không gọi `read_file` trên code dự án).
     * **CẤM** tự sửa file mã nguồn dự án trong Main Chat (không `edit_file` / `write_file` trên code dự án).
     * **CẤM** tự chạy lệnh Docker, build, test, migrate của dự án trong Main Chat.
     * **CẤM TUYỆT ĐỐI DÙNG `schedule` HOẶC VÒNG LẶP ĐỂ POLLING** trong Main Chat (hành vi gây lặp context và đốt sạch token quota 5h!).
   - **MASTER AGENT CHỈ ĐƯỢC PHÉP LÀM 4 BƯỚC ĐIỀU PHỐI DUY NHẤT:**
     1. Nhận diện dự án từ prompt User theo Routing Matrix.
     2. Gọi `hub shard auto "<prompt>"` để nạp đúng shard dự án.
     3. **GỌI NGAY `invoke_subagent` CHỌN ĐÚNG SUBAGENT PM DỰ ÁN** (như `dental-pm-orchestrator`, `vj-pm-orchestrator`, v.v.) và **DỪNG LẠI NGAY LẬP TỨC** (kết thúc lượt gọi tool). Hệ thống tự động kích hoạt lại qua **Reactive Wakeup** khi Subagent gửi tin nhắn M2M xong — KHÔNG ĐƯỢC POLLING!
     4. Khi nhận tin nhắn M2M kết quả từ Subagent: Báo cáo súc tích 2-3 câu Tiếng Việt kèm liên kết file cho User, gọi `hub shard reset` và kết thúc.
   - **TOÀN BỘ CÔNG VIỆC KỸ THUẬT SÂU:** Đọc code, sửa code qua Gemini API ngoài, chạy test/docker ĐỀU DO SUBAGENT THỰC HIỆN ĐỘC LẬP trong context con của Subagent, hoàn toàn cách ly với Main Chat!

## ⚡ QUY TẮC PHÂN MẢNH NGỮ CẢNH TỰ ĐỘNG (Rule 18)
- **TRƯỚC KHI thực thi bất kỳ task dự án nào:** BẮT BUỘC gọi `hub shard auto "<user_prompt>"` để chỉ nạp đúng context dự án tương ứng.
- **SAU KHI hoàn thành task:** BẮT BUỘC gọi `hub shard reset` để về shard `core` (tiết kiệm 89% token System Prompt).
- **CẤM** giữ shard dự án chuyên dụng (dental/vietjet/pc-builder/supervisor) sang lượt chat khác khi không còn thực thi dự án đó.
- Xem danh sách shard: `hub shard --list` | Chuyển thủ công: `hub shard set <id>`
