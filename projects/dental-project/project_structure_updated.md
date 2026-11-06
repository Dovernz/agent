# TIẾN ĐỘ DỰ ÁN NHA KHOA MINH SINH - BẢN NÂNG CẤP V3
**Branch:** `wordpress_udpate`  
**Ngày:** 06/11/2026

---

## 1. Cấu Trúc Menu Sidebar Django Admin (Sau Tinh Gọn)

Hệ thống đã rút gọn từ 7 nhóm cồng kềnh xuống còn **6 nhóm chuẩn nghiệp vụ**:

1. **Quản lý Booking:**
   - Lịch Ngày (`/admin/operations/dailyschedule/`)
   - Lịch Tuần (`/admin/operations/weeklyschedule/`)
   - Chi tiết Bookings (`/admin/operations/managebooking/`)
   - Tạo Booking (`/admin/booking-embed/`)
2. **Giao dịch:**
   - Thanh toán POS (`/admin/pos-system/`)
   - Thu hồi Công nợ (`/admin/pos-debt/`)
   - Hóa đơn & Thanh toán (`/admin/booking/payment/`) *(Đã chuẩn hóa, hợp nhất từ mục trùng)*
3. **Khách hàng & Dịch vụ:**
   - Khách hàng (`/admin/booking/customer/`)
   - Cơ sở / Clinics (`/admin/booking/clinic/`) *(Master Data quan trọng - Được bảo tồn)*
   - Danh mục Dịch vụ (`/admin/booking/servicecategory/`)
   - Chi tiết Dịch vụ (`/admin/booking/servicedetail/`)
   - Khung giờ (`/admin/booking/timeslot/`)
   - Khuyến mãi (`/admin/services_menu/catalogdiscount/`)
4. **Tài chính & Vật tư:**
   - Hoa hồng Bác sĩ (`/admin/commissions-embed/`)
   - Cấu hình Thanh toán (`/admin/booking/topupinfo/`)
   - Vật tư Kho (`/admin/booking/inventorydetail/`)
   - Tiêu hao Vật tư (`/admin/booking/inventoryusage/`)
   *(Đã gỡ bỏ mục "Thanh toán" trùng lặp trỏ cùng model Payment)*
5. **Bài viết & Blog (WordPress):**
   - Quản lý Bài viết (SSO `edit.php`)
   - Viết Bài Mới (SSO `post-new.php`)
   - Thư viện Hình ảnh (SSO `upload.php`)
6. **Hệ thống & Quản trị User:**
   - Cấu hình Commission Rate (`/admin/booking/commissionrate/`)
   - Phân quyền RBAC (`/admin/auth/group/`)
   - Người dùng (`/admin/auth/user/`)
   - Nhân viên (`/admin/booking/employee/`)

*(Nhóm `Cấu hình Web` đã được gỡ bỏ hoàn toàn khỏi Sidebar)*

---

## 2. Báo Cáo Nghiệm Thu
- Báo cáo đồng bộ Header & Footer: [`qa_header_footer_sync_report.md`](file:///C:/Users/thanhcaotien/.gemini/antigravity/brain/e836e051-9249-4417-b718-8bbc5e0435fb/qa_header_footer_sync_report.md)
- Ảnh minh chứng Sidebar tinh gọn: [`qa_proof_admin_expanded_sidebar.png`](file:///C:/Users/thanhcaotien/.gemini/antigravity/brain/e836e051-9249-4417-b718-8bbc5e0435fb/qa_proof_admin_expanded_sidebar.png)
