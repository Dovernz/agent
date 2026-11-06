# Project Checkpoint: dental-project (Phòng Khám Nha Khoa Minh Sinh)

- **Cập nhật lần cuối:** 2026-11-06 15:40
- **Trạng thái hiện tại:** 
  - Đang ở nhánh Git `wordpress_udpate` (Mã nguồn đã commit sạch sẽ, không merge với master).
  - Toàn bộ 4 phân hệ (Booking Web, EMR 32 Răng, Django Unfold Admin, WordPress CMS) đã được đồng bộ nhận diện thương hiệu và hoạt động trơn tru 100%.

---

## 📌 Các Mốc Tính Năng Đã Hoàn Thành (Milestone Progress)

1. **Đồng Bộ Giao Diện Header / Footer (WordPress & Booking Portal):**
   - Đồng bộ hoàn toàn Header và Footer của Cổng đặt lịch (`/booking/` và `/booking/success/`) theo WordPress Theme `minhsinh-dental`.
   - Màu sắc Header trắng thanh lịch, nút CTA đặt lịch dạng pill bo góc `border-radius: 9999px` xanh dương `#2563eb`.
   - Footer đổi sang tone màu sáng `#f8fafc`, loại bỏ nền đen tối cũ (`#0b132b`).
   - Xóa bỏ triệt để Cơ sở 3 (789 Cầu Giấy, Hà Nội), chuẩn hóa hệ thống 2 cơ sở chính thức:
     - *Cơ sở 1:* 123 Phố Huế, Hai Bà Trưng, Hà Nội.
     - *Cơ sở 2:* 456 Nguyễn Trãi, Thanh Xuân, Hà Nội.

2. **Cơ Chế Phân Quyền Động & Tối Ưu UX Phân Quyền (Dynamic RBAC):**
   - Loại bỏ cơ chế fix cứng chỉ Admin & Marketing; hỗ trợ cấp quyền linh hoạt theo từng menu cho từng User cụ thể (ví dụ: Bác sĩ được cấp quyền viết bài thì sidebar tự mở mục WordPress).
   - Bộ lọc Tab nhanh (Quick Tabs Filter) theo từng nhóm menu giúp chọn phân quyền tức thì mà không cần cuộn trang.
   - Thẻ Pills gọn gàng cho việc chọn Nhóm quyền (Group/Role Selector).
   - Sửa lỗi tràn màu trắng khi mở form chỉnh sửa thông tin nhân viên (`employee change form`) trên cả Light mode và Dark mode.

3. **Thuật Toán Tính Hoa Hồng Bác Sĩ (Thực Thu & Phân Loại Hợp Đồng):**
   - Bóc tách phân loại nhân sự: Bác sĩ có hợp đồng (trả lương cứng, không tính hoa hồng) vs Bác sĩ Part-time (được tính hoa hồng).
   - Trong 1 ca khám có cả 2 loại bác sĩ: Bảng hoa hồng bóc tách chính xác chỉ ghi nhận hoa hồng cho bác sĩ Part-time.
   - Tính hoa hồng theo từng đợt thanh toán (Thực thu): Khi khách thanh toán nhiều đợt (trả góp), hoa hồng được tính tương ứng theo số tiền thực thu của từng đợt thay vì tạm tính 1 cục ban đầu.

4. **Tinh Gọn Hệ Thống Menu Sidebar Django Unfold Admin:**
   - **Gỡ bỏ Nhóm `Cấu hình Web`:** Vì toàn bộ Header/Footer đã do WordPress quản lý, tránh nhập liệu thừa thãi và gây nhầm lẫn cho quản trị viên.
   - **Loại bỏ trùng lặp `Thanh toán`:** Xóa mục `Thanh toán` ở nhóm `Tài chính & Vật tư`, đổi tên mục ở nhóm `Giao dịch` thành **`Hóa đơn & Thanh toán`** (`/admin/booking/payment/`).
   - **Bảo tồn Danh mục `Cơ sở (Clinics)`:** Giữ nguyên trong nhóm `Khách hàng & Dịch vụ` vì đây là Master Data bắt buộc cho Booking và phân bổ ghế khám.

---

## 🛠️ Trạng Thái Hạ Tầng & Git
- **Docker Containers:** `dental_backend` (Port 8000), `dental_wordpress` (Port 80), `dental_wp_db` (Port 3306) đang hoạt động ổn định.
- **Git Branch:** `wordpress_udpate` (Commits: `b1ce621`, `8df60ff`, `4d4c289`).
- **QA Verification:** Đạt `100% PASS` trên Playwright E2E và Linter Guard.
