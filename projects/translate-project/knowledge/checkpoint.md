# Checkpoint Dự Án GeminiTrans

## Trạng Thái Hiện Tại (2026-11-11)
- **Container Docker:** `geminitrans_app` chạy tại port `8090`.
- **Git Repo:** Đồng bộ trên `https://github.com/Dovernz/translate-project.git`.
- **Bảo mật:** `.env` chứa 7 API keys được cô lập an toàn trong `.gitignore`. Quét an ninh đạt 100% PASS Quality Gate.
- **Tính năng hoàn thành:**
  * [x] Tab 1: Dịch văn bản & tài liệu streaming qua SSE, giữ nguyên định dạng docx/pdf.
  * [x] Tab 2: Dịch video/phim realtime kèm player & Floating Subtitle Overlay.
  * [x] Tab 3: Transcribe giọng nói qua Mic/File và dịch song ngữ.
  * [x] Tab 4: Manga Translator với AI inpainting & balloon detection.
  * [x] **AI Video Subtitling & Hardsub (Đa Ngôn Ngữ - Multi-Language):**
    - Hỗ trợ lựa chọn ngôn ngữ mục tiêu linh hoạt (Tiếng Việt, Tiếng Anh, Tiếng Nhật, Tiếng Hàn, Tiếng Trung, Tiếng Pháp, Tiếng Đức, Tiếng Tây Ban Nha, Tiếng Nga, Tiếng Thái, v.v.).
    - Tùy chọn "Đa ngôn ngữ" (Multi-Language) tạo đồng thời nhiều track phụ đề (vi, en, ja, zh, ko).
    - Bộ chuyển đổi ngôn ngữ tức thời trên giao diện (Zero-token switch nếu đã lưu, hoặc dịch nhanh AI không cần quét lại audio qua `/api/video/translate-subtitles`).
    - Che mờ / đè sạch phụ đề cũ của video bằng hộp phụ đề nền tối bo góc (Netflix style).
    - Bộ tùy chỉnh style phụ đề: Đổi màu chữ, màu nền, thanh trượt Opacity 0-100%, cỡ chữ 14-36px, khoảng cách đáy Margin Y.
    - Xem trước phụ đề nhảy thời gian thực trên HTML5 player.
    - Xuất video hardsub và tải file .SRT/.VTT theo ngôn ngữ mục tiêu đã chọn.
    - Bộ nhớ đệm phụ đề phân tách theo mã ngôn ngữ chống ghi đè cache.
  * [x] Bảng điều khiển Live HUD giám sát 7 API keys.
  * [x] Dockerfile & docker-compose.yml đóng gói chuẩn Docker-First.
  * [x] **Fix Điều Hướng Tabs Khi Nhấn Chuột Giữa (Middle-Click / Ctrl-Click):**
    - Chuyển đổi toàn bộ các thẻ điều hướng tab (Desktop & Mobile Drawer: video, document, web, transcribe, manga) từ `<button>` sang `<a href="?tab=...">`.
    - Cập nhật CSS Light Mode đồng bộ cho thẻ `nav a`.
    - Chuẩn hóa hàm định tuyến `normalizeTab()` hỗ trợ đầy đủ alias (`text`, `doc`, `translate`, `subtitles`, `audio`, `voice`, `comic`, `webpage`).
    - Đồng bộ `window.history.pushState` với tham số `?tab=...` khi chuyển tab mượt mà trên cùng trang.
    - Tự động kích hoạt đúng tab khi mở tab mới hoặc reload qua `initRouteTab()` trên `DOMContentLoaded`, `popstate`, và `hashchange`.
    - Bảo toàn hành vi native của trình duyệt cho chuột giữa (middle-click / auxclick), Ctrl+Click, Shift+Click mở tab mới trực tiếp với URL chuẩn, ngăn chặn `preventDefault()` không mong muốn.
    - Cập nhật route `get_home(tab: Optional[str] = None)` trong `app.py`.
