# Nhóm Skill Agent - Dự Án Vietjet Ancillary & Databricks Migration (`vietjet-ancillary`)

Thư mục này chứa toàn bộ cấu hình, bộ nhớ kiến thức và nhóm 5 Agent chuyên trách cho dự án **Vietjet PSS Ancillary & Databricks Medallion Migration**.

---

## 1. Vị trí Source Code & Dữ liệu
- **Mã nguồn & Dữ liệu làm việc:** `d:\Vietjet\2026\Tờ trình`
- **Tài liệu PSS & Stored Procedure gốc:** `d:\Vietjet\Docs\PSS` (chứa `gl_charges_detail.sql`, `Dictionary`)
- **Tập tin Báo cáo Tổng hợp:** `d:\Vietjet\2026\Tờ trình\Ancillary_Product_Groups_VN.xlsx`

---

## 2. Danh sách Agent Chuyên trách
1. **`vietjet-pm-orchestrator`**: Project Manager. Nhận yêu cầu, điều phối luồng 4 subagents, phân tách nhiệm vụ song song, kiểm soát luồng tổng hợp, đồng bộ Model inherit, KHÔNG tự ý commit Git.
2. **`vietjet-code-analyzer`**: Senior Data Engineer / Code Analyzer. Phân tích Stored Procedure cũ (`gl_charges_detail.sql`), DDL views, bóc tách CTEs, loại bỏ hardcoded IDs, xây dựng quy tắc Regex và thiết kế kiến trúc Databricks Medallion (Silver Models, Silver Analytics, Gold Marts).
3. **`vietjet-policy-reader`**: Business Analyst & Policy Specialist. Đọc hiểu tài liệu chính sách, Word/PDF (`KPI SAN BAY.docx`, Tờ trình hoa hồng), trích xuất ma trận đơn giá hoa hồng theo Counter vs Gate, G/L/O, Domestic vs International.
4. **`vietjet-catalog-inspector`**: Data Steward & Catalog Profiler. Thẩm định danh mục Master Data (`surcharge.csv`, `ssr.csv`, `Ancillary Type.xlsx`), loại trừ 10 mã thuế phí sân bay/vé (`AI`, `SG`, `SF`, `FA`...), thực hiện Gap Analysis (`In Both Tables`, `Surcharge Only`, `SSR Only`).
5. **`vietjet-excel-builder`**: Executive Spreadsheet Engineer. Tự động hóa xây dựng và cập nhật workbook Excel tổng hợp chuẩn Ban Tổng Giám đốc (`Ancillary_Product_Groups_VN.xlsx`) với 2-tier headers, bảng màu nhận diện thương hiệu, freeze panes, auto-fit.

---

## 3. Kiến trúc Databricks Medallion 5 Views
Hệ thống chuyển đổi Stored Procedure cũ thành 5 views phân định rạch ròi trách nhiệm:
- **Silver Models:**
  - `silver_dev.models.pss_surcharge`: Chuẩn hóa Master Surcharge, múi giờ UTC+7, bóc tách số cân hành lý tự động.
  - `silver_dev.models.pss_ssr_detail`: Chuẩn hóa Master SSR, Category Name, Active flags, IATA code.
- **Silver Analytics:**
  - `silver_dev.analytics.gl_booking_charges`: Hợp nhất giao dịch charges với chặng bay kết nối (`factor`), phân bổ thuế sân bay (`AIRPORT_TAX`), tỷ giá chuẩn, join động qua Master Data.
- **Gold Shared Mart:**
  - `gold_dev.shared.gl_charges`: Bảng dữ liệu dùng chung toàn hãng, loại bỏ tiền tố `str_`, `dtm_`, `lng_`, hiển thị sẵn thông tin SSR & Surcharge.
- **Gold Commission Mart:**
  - `gold_dev.com.ancillary_commission_baggage_detail`: Báo cáo chi tiết và tính tiền hoa hồng hành lý sân bay chuẩn hóa theo Tờ trình KPI Sân bay.

---

## 4. Kiến trúc & Quy chuẩn
- Đọc chi tiết tại `knowledge/tech-stack.md`, `knowledge/ancillary-taxonomy.md` và `rules/vietjet-rules.md`.
- Giao thức M2M chung: `../../common/rules/m2m-protocol.md`.
