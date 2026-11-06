# TIẾN ĐỘ THỰC HIỆN & GHI CHÚ KỸ THUẬT - MINH SINH DENTAL

**Branch Git hiện tại:** `wordpress_udpate`  
**Ngày cập nhật:** 06/11/2026

---

## 1. Chi Tiết Các Cải Tiến Mới Nhất

### A. Tinh gọn Sidebar Admin (Unfold)
- **File cập nhật:** `backend/core/settings.py` (cấu hình `UNFOLD['SIDEBAR']`).
- **Nghiệp vụ Thanh toán:**
  - *Trước:* Tồn tại 2 menu cùng trỏ vào `/admin/booking/payment/` gồm `Danh sách Hóa đơn` (trong Giao dịch) và `Thanh toán` (trong Tài chính).
  - *Sau:* Xóa mục `Thanh toán` trùng lặp tại nhóm Tài chính. Chuẩn hóa tên mục tại nhóm Giao dịch thành `Hóa đơn & Thanh toán`. Không làm mất bất kỳ dữ liệu hay tính năng nào (đầy đủ xem hóa đơn, mã VietQR động, in biên nhận).
- **Loại bỏ Cấu hình Web:**
  - Ẩn nhóm `Cấu hình Web` (`MenuLink` & `SiteSettings`) vì toàn bộ giao diện Header/Footer đã được quản lý bởi WordPress Theme và mã template Django độc lập.
- **Bảo tồn mục Cơ sở (Clinics):**
  - Giữ nguyên `/admin/booking/clinic/` làm master data cho form đặt lịch, phân chia ghế khám (`DentalChair`), và phân bổ ca làm việc.

### B. Đồng bộ Header / Footer & Xóa bỏ Cơ sở 3 Cầu Giấy
- **File cập nhật:**
  - `wordpress/wp-content/themes/minhsinh-dental/footer.php`
  - `backend/templates/booking_standalone.html`
  - `backend/templates/booking_success.html`
- **Kết quả:** Đồng bộ 100% nhận diện thương hiệu, bỏ hoàn toàn địa chỉ Cơ sở 3 (789 Cầu Giấy), chuẩn hóa 2 cơ sở chính thức:
  - Cơ sở 1: 123 Phố Huế, Hai Bà Trưng, Hà Nội
  - Cơ sở 2: 456 Nguyễn Trãi, Thanh Xuân, Hà Nội

### C. Quản lý Hoa hồng Bác sĩ & Hợp đồng lao động
- Phân biệt rõ loại hợp đồng lao động: Bác sĩ hợp đồng chính thức (không tính hoa hồng) vs Bác sĩ Part-time (được tính hoa hồng).
- Trong các đợt thanh toán nhiều lần (trả góp), hệ thống bóc tách tỷ lệ hoa hồng tương ứng với số tiền thực thu của từng đợt.

---

## 2. Danh Mục Bằng Chứng Kiểm Thử Tự Động (Artifacts)
- **Giao diện Sidebar Admin sau tinh gọn:**
  - [`qa_proof_admin_streamlined_sidebar.png`](file:///C:/Users/thanhcaotien/.gemini/antigravity/brain/e836e051-9249-4417-b718-8bbc5e0435fb/qa_proof_admin_streamlined_sidebar.png)
  - [`qa_proof_admin_expanded_sidebar.png`](file:///C:/Users/thanhcaotien/.gemini/antigravity/brain/e836e051-9249-4417-b718-8bbc5e0435fb/qa_proof_admin_expanded_sidebar.png)
- **Đồng bộ Footer 2 cơ sở:**
  - [`qa_proof_booking_footer_2branches.png`](file:///C:/Users/thanhcaotien/.gemini/antigravity/brain/e836e051-9249-4417-b718-8bbc5e0435fb/qa_proof_booking_footer_2branches.png)
  - [`qa_proof_landing_footer_2branches.png`](file:///C:/Users/thanhcaotien/.gemini/antigravity/brain/e836e051-9249-4417-b718-8bbc5e0435fb/qa_proof_landing_footer_2branches.png)
- **Báo cáo đồng bộ Header & Footer:**
  - [`qa_header_footer_sync_report.md`](file:///C:/Users/thanhcaotien/.gemini/antigravity/brain/e836e051-9249-4417-b718-8bbc5e0435fb/qa_header_footer_sync_report.md)
