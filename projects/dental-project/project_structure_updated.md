# TIẾN ĐỘ DỰ ÁN NHA KHOA MINH SINH - CƠ CHẾ PHÂN QUYỀN ĐỘNG (GRANULAR RBAC)

**Branch hiện tại:** `wordpress_udpate`  
**Ngày cập nhật:** 05/11/2026

## 1. Tính Năng Đã Hoàn Thiện
- **Granular Dynamic RBAC (Phân quyền động theo Permission):**
  - Không hardcode theo role/group cố định.
  - Sidebar Django Unfold kiểm tra quyền động ở cả cấp Section và cấp Item.
  - Khi một User (ví dụ Bác sĩ) được gán quyền `booking.manage_wordpress_posts` hoặc bất kỳ quyền nào của một section $\rightarrow$ Menu tương ứng lập tức hiển thị.
  - Khi thu hồi quyền $\rightarrow$ Menu lập tức ẩn đi, link SSO bị chặn 403 Forbidden.
- **Single Sign-On (SSO):** Hoạt động mượt mà cho mọi user có quyền bài viết.
- **SEO & Schema Nha Khoa:** Rank Math SEO + Schema Dentist JSON-LD chuẩn Google Search.

## 2. Báo Cáo Nghiệm Thu
[`qa_booking_and_system_report.md`](file:///C:/Users/thanhcaotien/.gemini/antigravity/brain/e836e051-9249-4417-b718-8bbc5e0435fb/qa_booking_and_system_report.md)
