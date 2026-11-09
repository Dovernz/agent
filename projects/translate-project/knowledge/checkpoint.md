# Checkpoint Dự Án GeminiTrans

## Trạng Thái Hiện Tại (2026-11-09)
- **Container Docker:** `geminitrans_app` đang chạy ở trạng thái `healthy` tại port `8090`.
- **Git Repo:** Đã đồng bộ 2 nhánh `main` và `master` trên `https://github.com/Dovernz/translate-project.git`.
- **Bảo mật:** `.env` chứa 7 API keys đã được cô lập an toàn trong `.gitignore`, chỉ commit `.env.example` và `.env.sample`. Quét an ninh với linter_guard đạt 100% PASS.
- **Tính năng hoàn thành:**
  * [x] Tab 1: Dịch văn bản & tài liệu streaming qua SSE.
  * [x] Tab 2: Dịch video/phim realtime kèm player & Floating Subtitle Overlay.
  * [x] Tab 3: Transcribe giọng nói qua Mic/File và dịch song ngữ.
  * [x] **Tính năng mới (AI Video Subtitling & Hardsub):**
    - Tải video lên (.mp4, .mov, .mkv) -> AI tự động quét âm thanh, chia mốc thời gian và dịch phụ đề.
    - Che mờ / đè sạch phụ đề cũ của video bằng hộp phụ đề nền tối bo góc (tương tự Netflix / ảnh mẫu).
    - Bộ tùy chỉnh style phụ đề: Đổi màu chữ, màu nền, thanh trượt Opacity 0-100%, cỡ chữ 14-36px, khoảng cách đáy Margin Y.
    - Xem trước phụ đề nhảy thời gian thực trên HTML5 player.
    - Xuất video hardsub vĩnh viễn bằng ffmpeg và cho phép tải video .MP4 hoặc tải file .SRT.
  * [x] Bảng điều khiển Live HUD giám sát 7 API keys.
  * [x] Dockerfile & docker-compose.yml đóng gói chuẩn Docker-First.
