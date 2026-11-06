# Antigravity Workspace Directives (Auto-Active Core)

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
