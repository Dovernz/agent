# Blueprint Kiến Trúc Multi-Agent Phân Tích Nghiệp Vụ & Báo Cáo Excel

Tài liệu này lưu trữ kiến trúc mẫu **Multi-Agent Requirement-to-Excel** để tham khảo kỹ thuật. 
Kiến trúc thực chiến đã được chuyển hóa và vận hành trực tiếp tại dự án [`projects/vietjet-ancillary`](file:///D:/Thành/Agent/projects/vietjet-ancillary).

---

## 1. Mô Hình 4 Subagents Chuyên Môn
- `code-analyzer`: Bóc tách CTEs, joins, phát hiện hardcoded IDs, chuyển đổi Stored Procedure sang Databricks Medallion.
- `policy-reader`: Đọc hiểu tài liệu chính sách, Tờ trình Word/PDF, trích xuất ma trận đơn giá hoa hồng.
- `catalog-inspector`: Thẩm định danh mục Master Data qua Peek-and-Script, loại trừ thuế phí, thực hiện Gap Analysis.
- `excel-builder`: Dựng workbook Excel báo cáo tổng hợp đa tầng (2-tier headers, freeze panes, auto-fit).

## 2. Nguyên Tắc Cốt Lõi
- Khảo sát dữ liệu mẫu qua Peek-and-Script (chỉ đọc Header + 3 dòng mẫu).
- Xử lý lọc, gộp, đối chiếu bằng script ngoài context.
- Chỉ in số liệu thống kê rút gọn vào context chat.
