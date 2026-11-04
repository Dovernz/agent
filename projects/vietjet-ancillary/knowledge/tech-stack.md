# Tech Stack Knowledge Base - Vietjet Ancillary & Databricks Migration

Mọi Agent làm việc trên dự án **Vietjet Ancillary (`vietjet-ancillary`)** BẮT BUỘC tuân thủ:

---

## 1. Vị trí Thư mục & Dữ liệu Thực tế
- **Thư mục làm việc chính:** `d:\Vietjet\2026\Tờ trình`
- **Thư mục tài liệu PSS:** `d:\Vietjet\Docs\PSS`
- **Mã nguồn Stored Procedure gốc:** `d:\Vietjet\Docs\PSS\gl_charges_detail.sql`
- **Master Data Files:**
  - `d:\Vietjet\2026\Tờ trình\surcharge.csv`: Danh mục 490+ PSS Surcharges.
  - `d:\Vietjet\2026\Tờ trình\ssr.csv`: Danh mục 575+ PSS SSR Definitions.
  - `d:\Vietjet\2026\Tờ trình\Ancillary Type.xlsx`: Bảng phân loại 110 mã cũ.
- **Tập tin Báo cáo Đầu ra:** `d:\Vietjet\2026\Tờ trình\Ancillary_Product_Groups_VN.xlsx`

---

## 2. Công nghệ & Nền tảng Kỹ thuật
- **Data Platform:** Databricks Lakehouse Platform (Spark SQL / Delta Lake).
- **Kiến trúc Dữ liệu:** Medallion Architecture (Bronze -> Silver Models -> Silver Analytics -> Gold Data Marts).
- **Bộ máy Tự động hóa Báo cáo:** PowerShell 5.1/7.x + Module `ImportExcel` (EPPlus OpenXML Engine).
- **Mã hóa Ký tự:** Bắt buộc UTF-8 cho toàn bộ text, CSV và PowerShell script để đảm bảo tiếng Việt có dấu (`Tờ trình`, `Hành lý`, `Ghế`, `Suất ăn`).

---

## 3. Quy tắc Biến đổi Dữ liệu (ETL & SQL Patterns)
- **Khử Hardcode ID:**
  - Không sử dụng `surcharge_id IN (135, 123, 6, ...)` hoặc `ssr_definition_id IN (558, 559, ...)`.
  - Bắt buộc dùng Regex bóc tách số cân:
    ```sql
    TRY_CAST(REGEXP_EXTRACT(surcharge_desc, '(\\d{1,3})\\s*kg', 1) AS INT)
    TRY_CAST(REGEXP_EXTRACT(ssr_description, '(\\d{1,3})\\s*kg', 1) AS INT)
    ```
  - Bắt buộc dùng Pattern matching phân loại Gate vs Counter:
    ```sql
    CASE 
      WHEN UPPER(surcharge_ident) LIKE '%GD' 
        OR UPPER(surcharge_ident) LIKE '%GI%' 
        OR UPPER(surcharge_ident) LIKE '%GATE%' 
        OR UPPER(surcharge_ident) LIKE 'CBG%' 
        OR UPPER(surcharge_desc) LIKE '%GATE%' 
      THEN 'Gate' ELSE 'Counter' END AS baggage_category
    ```
- **Hệ số Chặng bay Nối chuyến (`factor`):**
  - Doanh thu VND của các dịch vụ gắn với chặng bay được nhân theo hệ số `factor` từ `_pmv_res_legs_connecting_BH`.
  - Riêng thuế sân bay (`AIRPORT_TAX`) chỉ hạch toán vào chặng bay đầu tiên (`connecting_first_segment_flag = 'Y'`).
- **Chuẩn hóa Tên Cột:**
  - Loại bỏ hoàn toàn các tiền tố dữ liệu kiểu cũ (`str_`, `dtm_`, `lng_`).
  - Sử dụng định dạng `snake_case` chuẩn Analytics (vd: `res_number`, `flight_date`, `charges_amount`, `baggage_kg`).

---

## 4. Tiêu chuẩn Giao tiếp
- Tuân thủ tuyệt đối `m2m-protocol.md` (Zero-Fat, cờ tín hiệu, kế thừa model).
- Không tự ý commit Git. Giữ nguyên working tree để User tự kiểm tra và commit.

---

## 📋 Danh Mục Lệnh CLI Tái Sử Dụng (Reusable CLI Registry)

Bảng tra cứu nhanh các lệnh chuẩn hóa phục vụ kiểm tra danh mục dữ liệu PSS và sinh file Excel báo cáo:

### 1. Soi Dữ Liệu Master Data Chuẩn Peek-and-Script (`peek_data.py`)
> Đọc Header và các dòng mẫu đầu tiên, tiết kiệm 99% token context cho các file danh mục lớn:

- **Soi danh mục Phụ phí PSS (`surcharge.csv`):**
  ```powershell
  & "C:\Users\thanhcaotien\.local\bin\uv.exe" run python "D:\Thành\Agent\common\scripts\peek_data.py" "d:\Vietjet\2026\Tờ trình\surcharge.csv" --rows 3
  ```
- **Soi danh mục Dịch vụ Đặc biệt PSS (`ssr.csv`):**
  ```powershell
  & "C:\Users\thanhcaotien\.local\bin\uv.exe" run python "D:\Thành\Agent\common\scripts\peek_data.py" "d:\Vietjet\2026\Tờ trình\ssr.csv" --rows 3
  ```
- **Soi bảng phân loại cũ (`Ancillary Type.xlsx`):**
  ```powershell
  & "C:\Users\thanhcaotien\.local\bin\uv.exe" run python "D:\Thành\Agent\common\scripts\peek_data.py" "d:\Vietjet\2026\Tờ trình\Ancillary Type.xlsx" --rows 3
  ```

### 2. Tự Động Sinh File Excel Báo Cáo Chuẩn Ban Tổng Giám Đốc
> Tạo file Excel đa tầng (2-tier headers, bảng màu nhận diện Vietjet, freeze panes, định dạng tiền tệ và căn lề tự động):

- **Xây dựng toàn bộ workbook 3 sheets đối chiếu Ancillary:**
  ```powershell
  powershell -ExecutionPolicy Bypass -File "D:\Thành\Agent\projects\vietjet-ancillary\skills\excel-builder\scripts\build_consolidated_workbook.ps1" -TargetFolder "D:\Vietjet\2026\Tờ trình" -OutputFileName "Ancillary_Product_Groups_VN.xlsx"
  ```
- **Sinh bảng tính điều hành nhanh (Executive Summary):**
  ```powershell
  powershell -ExecutionPolicy Bypass -File "D:\Thành\Agent\projects\vietjet-ancillary\skills\excel-builder\scripts\generate_executive_excel.ps1"
  ```
