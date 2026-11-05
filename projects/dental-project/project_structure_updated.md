# BÁO CÁO CẬP NHẬT TIẾN ĐỘ DỰ ÁN NHA KHOA MINH SINH

**Branch:** `wordpress_udpate`  
**Ngày:** 05/11/2026

## 1. Các Nâng Cấp Đã Hoàn Thành
- **Single Sign-On (SSO) Django $\rightarrow$ WordPress:**
  - Token signed HMAC-SHA256 (hạn 60s).
  - Tự động đăng nhập 1 chạm khi bấm từ Django Admin sang WordPress wp-admin.
- **Phân Quyền Hệ Thống:**
  - Chỉ Admin và Marketing (Group `Marketing` / user `marketing1`) được phép truy cập WordPress.
  - Sidebar Django Unfold tự động ẩn menu WordPress đối với các vai trò khác (Lễ tân, Bác sĩ, Thu ngân).
  - Chặn truy cập trực tiếp bằng HTTP 403 Forbidden.
- **Tối Ưu SEO Nha Khoa:**
  - Cài đặt plugin Rank Math SEO.
  - Tích hợp Schema y khoa JSON-LD chuẩn Google (`Dentist`, `MedicalWebPage`, `MedicalScholarlyArticle`).

## 2. Tài Liệu Báo Cáo Nghiệm Thu
Chi tiết báo cáo và toàn bộ bằng chứng hình ảnh (proof screenshots) xem tại:
[`qa_booking_and_system_report.md`](file:///C:/Users/thanhcaotien/.gemini/antigravity/brain/e836e051-9249-4417-b718-8bbc5e0435fb/qa_booking_and_system_report.md)
