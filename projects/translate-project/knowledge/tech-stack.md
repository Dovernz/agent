# Tech Stack Specification - GeminiTrans

## 1. Tổng Quan Kiến Trúc
- **Tên dự án:** Gemini Universal Translator & Realtime Subtitler (GeminiTrans)
- **Thư mục mã nguồn:** `d:\Thành\Translate`
- **Mô hình hoạt động:** Single Page Application (FastAPI + HTML5/Tailwind/Lucide) kết hợp SSE/REST Backend và Docker Compose.

## 2. Công Nghệ Chi Tiết
| Phân Lớp | Công Nghệ / Thư Viện | Phiên Bản | Ghi Chú |
| :--- | :--- | :--- | :--- |
| **Backend Runtime** | Python | 3.12 (Docker) / 3.14 (Host) | Quản lý package qua Astral `uv` |
| **API Framework** | FastAPI | >= 0.162.0 | Xử lý streaming qua `StreamingResponse` (SSE) |
| **Web Server** | Uvicorn | >= 0.54.0 | Asynchronous ASGI Server |
| **Containerization** | Docker & Docker Compose | Docker 29.x | Container `geminitrans_app`, Port `8090:8000` |
| **Video/Audio Engine**| yt-dlp & ffmpeg | 2026.10+ / Debian | Trích xuất video metadata & chia audio chunk |
| **HTTP Client** | HTTPX | >= 0.28.1 | Asynchronous HTTP/2 streaming client |
| **Frontend UI** | HTML5, Tailwind CSS, Lucide Icons | CDN | Glassmorphism Dark Theme, không phụ thuộc Node/npm |

## 3. Ma Trận AI Models & Hạn Mức Tận Dụng (Google AI Studio)
- **Live Stream Subtitles:** `gemini-2.5-flash` / `gemini-3.5-live-translate` (RPD Unlimited | 1M TPM).
- **Bulk Document Translation:** `gemini-3.5-flash-lite` (7.000 req/ngày | 210 RPM).
- **Ultra-Frequency Translation:** `gemma-4-26b-a4b-it` (100.800 req/ngày | 210 RPM).
- **Standard Deep Context:** `gemini-3.6-flash` (420 req/ngày | 105 RPM).
- **Academic / Medical Translation:** `gemini-3.8-flash` (140 req/ngày | 35 RPM).

## 4. Cơ Chế Xoay Vòng Smart Key Pool
- Kết nối trực tiếp 7 Cloud Projects qua `GEMINI_API_KEYS`.
- Phân phối Round-Robin luân phiên giữa các chunk phụ đề video (4s - 5s).
- Tự động cách ly Cooldown 60s khi phát hiện HTTP 429 và fallback sang key kế tiếp.
