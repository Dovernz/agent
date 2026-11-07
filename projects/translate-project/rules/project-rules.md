# Project Rules - GeminiTrans

1. **Docker-First Bắt Buộc:**
   - Mọi thay đổi code hoặc kiểm thử đều chạy trên hoặc qua container `geminitrans_app`.
   - Cổng truy cập mặc định là `8090` (tránh xung đột port `8000` của `dental_backend` và `8080` của `airflow`).
2. **Bảo Mật API Keys Tuyệt Đối:**
   - Tuyệt đối không commit file `.env` vào Git.
   - Luôn sử dụng `.env.example` làm mẫu cấu hình.
3. **Cơ Chế Điều Phối Pool:**
   - Khi dịch luồng chunk video/phim, bắt buộc sử dụng `KeyPool.acquire_key()` để luân chuyển qua 7 API Keys nhằm bảo đảm không bao giờ chạm rate limit RPM/TPM.
4. **Giữ Nguyên Cấu Trúc Tài Liệu:**
   - Prompt dịch tài liệu bắt buộc yêu cầu giữ nguyên định dạng Markdown, code block, table và line-breaks.
