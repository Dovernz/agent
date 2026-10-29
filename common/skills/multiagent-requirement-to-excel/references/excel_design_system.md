# Quy chuẩn Thiết kế Bảng tính Doanh nghiệp (Executive Excel Design System)

Quy chuẩn này áp dụng cho toàn bộ các file Excel báo cáo tổng hợp, ma trận đối chiếu và báo cáo tài chính tạo bởi `excel-report-builder`.

---

## 1. Hệ thống Bảng màu Doanh nghiệp (Corporate Color Palette)

### Nhóm Màu Chủ đạo (Primary Brand Colors)
- **Executive Dark Blue**: `#1F4E78` (RGB: 31, 78, 120) - Sử dụng cho Main Title, Banner phân khu, Cột ID/Mã chính.
- **Corporate Navy**: `#2F5496` (RGB: 47, 84, 150) - Sử dụng cho Super-header Nhóm Thông tin chung / Bảng nguồn 1.
- **Corporate Crimson Red**: `#C00000` (RGB: 192, 0, 0) - Sử dụng cho Super-header PSS Surcharge / Cảnh báo Data Gap.
- **Corporate Forest Green**: `#375623` (RGB: 55, 86, 35) - Sử dụng cho Super-header PSS SSR / Trạng thái Hoàn tất.
- **Corporate Regal Purple**: `#7030A0` (RGB: 112, 48, 160) - Sử dụng cho Super-header Trạng thái & Phạm vi / Ghi chú.

### Nhóm Màu Nền Header Cấp 2 (Pastel Sub-Header Colors)
- **Soft Blue**: `#D9E1F2` (RGB: 217, 225, 242) - Phân khu Thông tin chung.
- **Soft Steel / Orange**: `#FCF2E9` / `#DEEBF7` - Phân khu Bảng cũ / Surcharge.
- **Soft Green**: `#E2EFDA` (RGB: 226, 239, 218) - Phân khu Bảng mới / SSR.
- **Soft Purple**: `#E1D5E7` (RGB: 225, 213, 231) - Phân khu Trạng thái & Ghi chú.

### Nhóm Màu Nền Dữ liệu & Phân đoạn (Data & Section Colors)
- **Section Banner**: `#E6E6E6` (RGB: 230, 230, 230) - Nền phân đoạn các nhóm nghiệp vụ (SECTION 1 đến SECTION 9).
- **Zebra Striping (nếu dùng)**: Xen kẽ `#FFFFFF` và `#F9FBFD`.
- **Border Line**: `#D9D9D9` (RGB: 217, 217, 217) - Viền mỏng cho các ô dữ liệu.

---

## 2. Thang Kiểu chữ & Cỡ chữ (Typography Hierarchy)

| Thành phần | Font chữ | Cỡ chữ | Kiểu chữ | Màu chữ | Căn lề | Chiều cao dòng |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Main Title (Row 1)** | Segoe UI | 14pt | Bold | Trắng (`#FFFFFF`) | Giữa (Horizontal & Vertical) | 35pt |
| **Subtitle (Row 2)** | Segoe UI | 10pt | Italic | Xám đậm (`#595959`) | Giữa (Horizontal & Vertical) | 22pt |
| **Super-Headers (Row 3)**| Segoe UI | 10pt | Bold | Trắng (`#FFFFFF`) | Giữa (Horizontal & Vertical) | 25pt |
| **Sub-Headers (Row 4)** | Segoe UI | 9.5pt | Bold | Đen (`#000000`) | Giữa (Wrap Text) | 32pt |
| **Section Banner** | Segoe UI | 10.5pt | Bold | Dark Blue (`#1F4E78`) | Giữa dọc, Trái ngang | 22pt |
| **Data Cells (Text)** | Segoe UI | 9.5pt | Regular | Đen (`#000000`) | Giữa dọc, Trái ngang (Wrap) | Auto |
| **Data Cells (Codes/ID)**| Segoe UI | 9.5pt | Regular/Bold | Đen / Dark Blue | Giữa dọc & Giữa ngang | Auto |
| **Status Badges** | Segoe UI | 9.5pt | Bold | Green / Blue / Red | Giữa dọc & Giữa ngang | Auto |

---

## 3. Quy chuẩn Viền (Borders) & Khung nhìn (View Layout)

1. **Đường viền ô**:
   - Headers: Viền trên và viền dưới dày vừa (`Medium Border`).
   - Dữ liệu: Viền mỏng toàn bộ ô (`Thin Border`, `#D9D9D9`).
2. **Đường lưới (Gridlines)**:
   - Luôn bật hiển thị đường lưới: `$ws.View.ShowGridLines = $true`.
3. **Cố định dòng & cột (Freeze Panes)**:
   - Luôn cố định 4 dòng tiêu đề phía trên và các cột mã định danh bên trái:
     `$ws.View.FreezePanes(5, 4)` (Dữ liệu bắt đầu từ dòng 5, cột nội dung linh hoạt từ cột 4 trở đi).
4. **Độ rộng cột (Column Widths)**:
   - STT: 7
   - Mã/ID: 10 - 15
   - Tên ngắn/Danh mục: 18 - 25
   - Logic / Pattern: 30 - 38
   - Ghi chú chi tiết: 40 - 50
