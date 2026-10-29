# Case Study Thực tế: Di chuyển SQL Procedure sang Databricks & Lập Báo cáo Đối chiếu Ancillary

Case study này ghi lại quá trình điều phối thực tế giữa **Orchestrator** và **4 Subagents** để giải quyết trọn vẹn bài toán di chuyển hệ thống tính toán chi phí & hoa hồng Ancillary của Vietjet từ SQL Server sang Databricks Medallion Architecture.

---

## 1. Yêu cầu Đầu vào & Tập tin Tài liệu
- **Tập tin SQL cũ**: `gl_charges_detail.sql` (Stored procedure nguyên khối chứa hàng loạt `CASE WHEN` và hardcoded IDs).
- **Tập tin Chính sách Nghiệp vụ**: `KPI SAN BAY.docx`, `[Anci reply FIN comment] TTr Chuong trinh hoa hong Anci.docx`.
- **Tập tin Dữ liệu Danh mục**: `surcharge.csv`, `ssr.csv`, `Ancillary Type.xlsx` (bảng cũ 110 dòng).

---

## 2. Quá trình Điều phối Phân rã cho các Subagents

### Bước 1: `code-analyzer` Phân tích Stored Procedure
- **Phát hiện**:
  - Hơn 50 `surcharge_id` và 10 `ssr_definition_id` bị hardcode cố định để xác định số cân hành lý (1kg, 2kg, 5kg, 10kg, 15kg, 20kg).
  - Logic phân bổ doanh thu theo chặng nối chuyến: `factor = leg_mileage / total_journey_mileage`.
  - Phí thuế sân bay (`AIRPORT_TAX`) chỉ được hạch toán cho chặng bay đầu tiên (`connecting_first_segment_flag = 'Y'`).
- **Đề xuất kỹ thuật**:
  - Thay thế hardcode bằng Regex: `TRY_CAST(REGEXP_EXTRACT(surcharge_desc, '(\\d{1,3})\\s*kg', 1) AS INT)`.
  - Phân tách thành 2 tầng Silver Models (`pss_surcharge` và `pss_ssr_detail`) để tái sử dụng.

### Bước 2: `policy-doc-reader` Bóc tách Tờ trình KPI Sân bay
- **Phát hiện**:
  - Chính sách chi hoa hồng phân định theo **Vị trí thu**: Quầy làm thủ tục (`Counter`) vs Cửa khởi hành (`Gate`).
  - Phân định theo **Loại hành lý**: Gói/kiện (`G`), Quá cước theo kg (`L`), Quá khổ (`O`).
  - Ma trận đơn giá hoa hồng:
    + Counter G: Nội địa 8,000 VND / Quốc tế 12,000 VND
    + Counter L: Nội địa 3,000 VND/kg / Quốc tế 5,000 VND/kg
    + Gate G: Nội địa 5,000 VND / Quốc tế 10,000 VND
    + Gate L: Nội địa 2,000 VND/kg / Quốc tế 4,000 VND/kg
    + Oversize O: Nội địa 30,000 VND / Quốc tế 60,000 VND

### Bước 3: `data-catalog-inspector` Thẩm định Danh mục & Khử Nhiễu
- **Phát hiện**:
  - Bảng cũ `Ancillary Type.xlsx` có 110 dòng, nhưng chứa cả các mã thuế sân bay, phí an ninh soi chiếu và giá vé (`AI`, `SG`, `OO`, `OP`, `AS`, `APPS`, `BKK E8`, `SF`, `MO`, `FA`).
  - Sau khi loại trừ 10 mã trên, còn lại chính xác **100 sản phẩm Ancillary thuần túy**.
- **Quy hoạch**:
  - Phân bổ 100 sản phẩm cũ vào **9 nhóm sản phẩm quy chuẩn**:
    1. Baggage & Cabin Baggage (24 mã)
    2. Seat Assignment (11 mã)
    3. Meals & Beverages (24 mã)
    4. Priority & Airport Convenience (6 mã)
    5. Special Services (6 mã)
    6. Travel Insurance (6 mã)
    7. Inflight Merchandise & Duty Free (2 mã)
    8. Flight Modification, Penalty & Admin Fees (7 mã)
    9. Other System & Legacy Charges (14 mã)

---

## 3. Tổng hợp Logic & Xây dựng Kiến trúc Databricks Medallion

Orchestrator hợp nhất các kết quả và chỉ đạo tạo 5 Views:
1. `silver_dev.models.pss_surcharge`: Master Surcharge + Bóc tách số kg tự động + UTC+7.
2. `silver_dev.models.pss_ssr_detail`: Master SSR + Category Name + IATA code.
3. `silver_dev.analytics.gl_booking_charges`: Booking charges + Factor phân bổ nối chuyến + Tỷ giá chuẩn + Master Data Joins (thay thế CASE WHEN).
4. `gold_dev.shared.gl_charges`: Bảng Data Mart dùng chung toàn hãng, chuẩn hóa tên cột Analytics (loại bỏ `str_`, `dtm_`, `lng_`).
5. `gold_dev.com.ancillary_commission_baggage_detail`: Bảng tính hoa hồng hành lý sân bay chuẩn hóa theo ma trận Tờ trình.

---

## 4. `excel-report-builder` Sản xuất File Báo cáo Hoàn chỉnh
Workbook `Ancillary_Product_Groups_VN.xlsx` được tự động sinh với 3 sheets:
- **Sheet 1 (`Ancillary_Product_Groups`)**: Ma trận phân loại mới 12 cột, 60 dòng đối chiếu trực tiếp giữa PSS Surcharge và PSS SSR.
- **Sheet 2 (`Legacy_Ancillary_Products`)**: Đối chiếu toàn bộ 100 sản phẩm từ bảng cũ vào 9 nhóm chuẩn, gắn kèm logic chuyển đổi trên Databricks.
- **Sheet 3 (`Databricks_Medallion_Views`)**: Đặc tả kiến trúc, bảng nguồn, regex và file DDL lưu trữ của 5 views.
- **Tiêu chuẩn giao diện**: Font Segoe UI, Super-headers 2 tầng, bảng màu nhận diện (Dark Blue, Crimson, Forest Green, Regal Purple), freeze panes, auto-fit, viền mỏng xám.
