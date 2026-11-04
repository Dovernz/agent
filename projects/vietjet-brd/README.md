# Vietjet BRD Automation Hub (`vietjet-brd`)

Hệ thống Agent chuyên biệt tự động hóa lập tài liệu **Business Requirements Document (BRD)** chuẩn doanh nghiệp Vietjet Aviation Joint Stock Company.

---

## 🎯 Mục Tiêu & Nguyên Tắc Bất Di Bất Dịch
1. **Bảo tồn 100% Format Chuẩn Vietjet**:
   - Trang bìa (Cover page) với logo Vietjet Air sắc nét, mã tài liệu, tên dự án, ngày tạo, phiên bản, thông tin trụ sở công ty.
   - Bảng kiểm soát tài liệu và các mục thủ tục phê duyệt bắt buộc:
     * **A.** Danh sách phân phối / List of distribution
     * **B.** Danh sách sửa đổi / Record of Revision
     * **C.** Danh mục trang có hiệu lực / List of effective pages
     * **D.** Căn cứ vào tài liệu / References
     * **E.** Kiểm tra và phê duyệt / Check and Approval (ICT Director + Business Division Director)
     * **F.** Xác nhận đơn vị tham gia rà soát / Check and Approval (Data Manager + Business Lead)
     * **G.** Danh sách phân phối / List of distribution
   - Running Header ở Section 1 tự động đồng bộ Tên báo cáo và Ngày tạo.
   - Bảng đối tượng sử dụng (Khối, Phòng ban).
2. **Chỉ thay đổi linh hoạt theo từng báo cáo**:
   - Tên báo cáo (Tiếng Việt in hoa chuẩn & Tiếng Anh nếu cần).
   - Ngày tạo báo cáo (tự động theo ngày hiện tại `DD-MM-YYYY` hoặc ngày chỉ định).
   - Nội dung Mục I (Mục tiêu, Phạm vi, Đối tượng sử dụng).
   - Nội dung Mục II (Tổng quan, Bảng định nghĩa nghiệp vụ, Bảng tham số đầu vào / Filters, Bảng dữ liệu chi tiết / Schema).
   - Nội dung Mục III (Dashboard tổng quan, KPI cards, Bảng ma trận cấp Route, Bảng chi tiết cấp Flight, Mockup giao diện).
3. **Nguồn Dữ Liệu Linh Hoạt**:
   - Nhận mô tả trực tiếp từ User Prompt.
   - Đọc trực tiếp từ file Excel yêu cầu (ví dụ `20260108_REPORT REQUEST TO IT.xlsx`).
   - Đọc từ data dictionary, DDL SQL, hoặc API/Dashboard mockups.

---

## 📂 Cấu Trúc Dự Án
```text
vietjet-brd/
├── README.md                          # Tài liệu tổng quan dự án
├── knowledge/
│   ├── brd-standards.md               # Quy chuẩn cấu trúc văn bản, styling, XML properties
│   └── vietjet-domain-dictionary.md   # Từ điển thuật ngữ nghiệp vụ hàng không Vietjet
├── rules/
│   └── brd-rules.md                   # Bộ nguyên tắc bắt buộc khi tạo BRD
├── templates/
│   └── template_vietjet_brd.docx      # Master template chuẩn trích xuất từ tài liệu Vietjet
├── scripts/
│   ├── brd_builder.py                 # Engine sinh file docx tự động từ JSON / Config
│   └── excel_reader.py                # Script trích xuất spec trực tiếp từ file Excel
└── skills/
    └── vietjet-brd-architect/
        └── SKILL.md                   # Skill định nghĩa cho Antigravity Agent Hub
```

---

## 🚀 Hướng Dẫn Sử Dụng
### 1. Sinh BRD từ dòng lệnh (CLI):
```bash
uv run --with python-docx python scripts/brd_builder.py --config config.json --output "D:\Vietjet\2026\COM - Sale Reports\BRD\BRD_Sample.docx"
```

### 2. Trích xuất từ Excel và sinh BRD:
```bash
uv run --with openpyxl --with python-docx python scripts/excel_reader.py
```
