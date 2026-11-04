# Quy Chuẩn Cấu Trúc Tài Liệu BRD Vietjet (BRD Standards)

Tài liệu này định nghĩa cấu trúc chuẩn hóa cho tất cả các tài liệu Business Requirements Document (BRD) của Vietjet Air.

---

## 1. Bố Cục Trang Bìa (Cover Page)
- **Header Top**: Logo Vietjet Air (`vietjetair.com` màu đỏ thương hiệu).
- **Tên báo cáo**: In hoa, Bold, cỡ chữ 24pt, font Times New Roman.
- **Phụ đề**: `Business Requirements Document (BRD)`.
- **Ngày tạo**: Định dạng `DD-MM-YYYY` (Ví dụ: `29-10-2026`).
- **Phiên bản**: `Version 1.0` (hoặc `Version 1.1` khi có sửa đổi).
- **Khung thông tin tài liệu (Table 0)**:
  * Dự án / Project: `Báo cáo quản trị thương mại` (hoặc tên dự án cụ thể).
  * Mã tài liệu / Document ID: Mã định danh nội bộ hoặc để trống.
  * Soạn thảo / Issued By: `Cao Tiến Thành` (hoặc tên người tạo).
  * Phiên bản / Version: `1.0`.
  * Ngày hiệu lực / Effective Date: Ngày ký duyệt hoặc để trống.
- **Footer Trụ sở**:
  ```text
  VIETJET AVIATION JOINT STOCK COMPANY
  302/3 Kim Ma Street, Ngoc Khanh Ward, Ba Dinh District, Ha Noi, Viet Nam
  Phone number: (84-28) 3547 1866    Fax: (84-28) 3547 1866
  ```

---

## 2. Các Mục Thủ Tục Bắt Buộc (Immutable Front Sections)
Các mục sau **LUÔN GIỮ NGUYÊN BỐ CỤC VÀ BẢNG CHUẨN**:
- **A. Danh sách phân phối / List of distribution**: Bảng gồm STT, Đơn vị sử dụng (Bộ phận Công Nghệ, Khối Thương Mại, v.v.), Bản giấy, CD, Ghi chú.
- **B. Danh sách sửa đổi / Record of Revision**: Bảng gồm Số sửa đổi, Ngày ban hành, Ngày hiệu lực, Ngày nhận, Chữ ký người nhận.
- **C. Danh mục trang có hiệu lực / List of effective pages**: Bảng gồm Chương, Trang, Sửa đổi, Ban hành, Hiệu lực, Ghi chú.
- **D. Căn cứ vào tài liệu / References**: Bảng gồm STT, Tên tài liệu, Số tài liệu, Ngày ban hành.
- **E. Kiểm tra và phê duyệt / Check and Approval**:
  * Khung Header gồm Logo Vietjet, chữ `BUSINESS REQUIREMENTS DOCUMENT`, `PHÒNG CÔNG NGHỆ THÔNG TIN IT DEPARTMENT`.
  * Cấp trình/Phê duyệt:
    - Bộ phận Công Nghệ IT Department: Lê Hải Bình - ICT Director.
    - Khối nghiệp vụ: Ví dụ Khối Thương Mại (Hà Năng Việt - Director of Commercial Division), Khai Thác Bay (Tony Quek), Contact Center (Chử Thị Thanh Hà).
- **F. Xác nhận đơn vị tham gia rà soát / Check and Approval**:
  * Bộ phận Công Nghệ: Trần Phước Duy - Data Manager.
  * Đơn vị nghiệp vụ: Quản lý hoặc Team Leader tương ứng.
- **G. Danh sách phân phối / List of distribution**: Bảng gồm STT, Người nhận, Ghi chú.

---

## 3. Nội Dung Nghiệp Vụ Chính (Dynamic Report Body)

### I. MỤC TIÊU BÁO CÁO VÀ ĐỀ XUẤT
- **1.1. Mục tiêu báo cáo**: Nêu rõ 3-4 gạch đầu dòng mục đích: phục vụ giám sát doanh thu, quản lý đại lý, push sale, theo dõi load factor, đối soát dữ liệu.
- **1.2. Phạm vi báo cáo**:
  * Mạng bay: Toàn mạng bay Vietjet (VJ) và Thái Vietjet (VZ).
  * Thị trường: Nội địa (Vietnam, Thailand) và Quốc tế (China, Korea, India, Kazakhstan, Australia, Japan, v.v.).
  * Kênh bán: Website/App, OTA, GDS, Đại lý truyền thống (PSA).
- **1.3. Đối tượng sử dụng**: Bảng 2 cột: `Khối` và `Phòng ban` được phân quyền xem báo cáo.

### II. BÁO CÁO [TÊN BÁO CÁO]
- **2.1. Tổng quan báo cáo**: Đoạn văn tóm tắt chức năng và luồng dữ liệu của báo cáo.
- **2.2. Định nghĩa (nếu có)**: Bảng gồm các cột `STT`, `Nội dung`, `Định nghĩa`.
- **2.3. Tham số đầu vào (Input Parameters / Filters)**:
  * Bảng gồm 5 cột chuẩn: `STT`, `Tên cột`, `Định nghĩa`, `Ví dụ`, `Notes`.
  * Bắt buộc có các tham số: `Flight Date From`, `Flight Date To`, `Market`, `Airline Code` (VJ/VZ), `Route`, và các bộ lọc đặc thù (Agency, Fare Class, Add-on, Status...).
- **2.4. Bảng dữ liệu chi tiết (Detailed Data Fields Schema)**:
  * Bảng gồm 5 cột chuẩn: `STT`, `Tên cột`, `Định nghĩa`, `Ví dụ`, `Notes` (hoặc Công thức).
  * Các trường dữ liệu cốt lõi: Flight_Date, Flight_Nmbr, Dep, Arr, Market, PNR, Pax_Name, Agent_Code, Agent_Name, Fare_Amount, Ancillary_Amount, Currency, v.v.

### III. DASHBOARD BÁO CÁO
- **3.1. Tổng quan Dashboard**:
  * Các thẻ KPI Cards chính: Total Revenue, Total Pax/Volume, Top Route, Average Load Factor/Yield.
  * Khu vực bộ lọc trực quan.
- **3.2. Báo cáo tổng hợp cấp đường bay (Route Level Matrix)**: Ma trận tỷ lệ hoặc doanh thu theo đường bay.
- **3.3. Báo cáo chi tiết cấp chuyến bay (Flight Level Detail)**: Chi tiết từng chuyến bay theo ngày.
- **Mockup giao diện**: Dạng bảng ASCII hoặc layout trực quan mô phỏng giao diện portal/dashboard.

---

## 4. Bảng Quy Chuẩn Định Dạng & Cỡ Chữ Chi Tiết Từng Phần (Typography Matrix)

Qua phân tích và thống kê tự động 100% tài liệu BRD chính thức trong thư mục `D:\Vietjet\2026\COM - Sale Reports\BRD`, quy chuẩn phông chữ và cỡ chữ chung cho **từng phần riêng biệt** được xác lập như sau:

| STT | Phần / Hạng mục | Kiểu phông chữ | Cỡ chữ (Size) | Định dạng (Style) | Màu sắc (Color) | Ghi chú |
| :---: | :--- | :---: | :---: | :---: | :---: | :--- |
| 1 | **Tiêu đề trang bìa (Cover Title)** | Times New Roman | **24.0 pt** | In đậm (`Bold=True`) | Đen (`#000000`) | Căn giữa, in hoa toàn bộ |
| 2 | **Nhãn BRD trang bìa** | Times New Roman | **12.0 pt** | In đậm (`Bold=True`) | Xanh lá (`#009900`) | `Business Requirements Document (BRD)` |
| 3 | **Ngày tạo & Phiên bản trang bìa** | Times New Roman | **12.0 pt** | Thường (`Regular`) | Xanh lá (`#009900`) | `DD-MM-YYYY` / `Version 1.0` |
| 4 | **Tiêu đề Mục lục (TOC Title)** | Times New Roman | **16.0 pt** | In đậm (`Bold=True`) | Đen (`#000000`) | Chữ `MỤC LỤC` |
| 5 | **Heading 1 (Tiêu đề mục lớn A-F, I, II, III)** | Times New Roman | **13.0 pt** | In đậm (`Bold=True`) | Đỏ Vietjet (`#EE0000`) | 100% BRD Vietjet chuẩn hóa |
| 6 | **Heading 2 (Tiêu đề mục con 1.1, 2.1, 2.3...)** | Times New Roman | **13.0 pt** | In đậm (`Bold=True`) | Đen (`#000000`) | Có thụt lề 1 tab |
| 7 | **Nội dung văn bản (Body text, gạch đầu dòng)** | Times New Roman | **12.0 pt** | Thường (`Regular`) | Đen (`#000000`) | Line spacing 1.15, space after 2pt |
| 8 | **Tiêu đề cột các bảng (Table Header)** | Times New Roman | **12.0 pt** | In đậm (`Bold=True`) | Đen (`#000000`) | Nền xám `#D7D7D7` |
| 9 | **Dữ liệu ô bảng (Table Data Cell)** | Times New Roman | **12.0 pt** | Thường (`Regular`) | Đen (`#000000`) | Đệm lề trái/phải 108 dxa |
| 10 | **Bảng kiểm soát tài liệu (Table 0)** | Times New Roman | **12.0 pt** | Cột 1 Đậm / Cột 2 Thường | Đen (`#000000`) | Dự án, Mã tài liệu, Người tạo... |
| 11 | **Running Header (Header trang Section 1)** | Times New Roman | **9.0 pt** | Tiêu đề Đậm / Ngày Thường | Đen (`#000000`) | Bảng 3 ô trên đầu trang |

### Khóa Cứng Kỹ Thuật (OpenXML Preservation)
Toàn bộ các run văn bản được sinh ra bắt buộc phải gán trực tiếp:
- `<w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman" w:eastAsia="Times New Roman"/>`
- `<w:sz w:val="26"/>` (13pt) cho Heading 1 và Heading 2
- `<w:sz w:val="24"/>` (12pt) cho Body text và các ô bảng
- `<w:sz w:val="48"/>` (24pt) cho Tiêu đề trang bìa
- `<w:sz w:val="18"/>` (9pt) cho Header trang
