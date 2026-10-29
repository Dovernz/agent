---
name: vietjet-rules
description: Quy định và nguyên tắc bắt buộc cho nhóm Agent dự án Vietjet Ancillary & Databricks Migration.
trigger: model_decision
---

# Quy định Dự Án Vietjet Ancillary & Databricks Migration

1. **Phạm vi Thư mục Làm việc:**
   - Mọi file dữ liệu, script xử lý, và báo cáo kết quả đều nằm trong thư mục `d:\Vietjet\2026\Tờ trình`.
   - File Stored Procedure cũ và tài liệu PSS tham chiếu tại `d:\Vietjet\Docs\PSS`.

2. **Bảo vệ Dữ liệu Gốc:**
   - Tuyệt đối KHÔNG sửa đổi, ghi đè hoặc xóa các file dữ liệu master gốc của người dùng (`surcharge.csv`, `ssr.csv`, `Ancillary Type.xlsx`).
   - Khi cập nhật file Excel báo cáo (`Ancillary_Product_Groups_VN.xlsx`), luôn kiểm tra file lock trước khi ghi.

3. **Nguyên tắc Viết SQL Databricks:**
   - CẤM hardcode ID (`WHERE id IN (...)` hoặc `CASE WHEN id = ...`).
   - Sử dụng Regex để trích xuất thuộc tính tự động (`(\d{1,3})\s*kg`).
   - Sử dụng Master Data joins qua `surcharge_id` và `charges_id`.
   - Loại bỏ các tiền tố kiểu dữ liệu cũ (`str_`, `dtm_`, `lng_`).

4. **Tiêu chuẩn Bảng tính Excel:**
   - Bắt buộc sử dụng font `Segoe UI`.
   - Bắt buộc cấu trúc 2-tier headers với phân khu màu sắc nhận diện (Navy, Crimson, Forest Green, Regal Purple).
   - Luôn bật hiển thị đường lưới (`ShowGridLines = $true`) và đóng băng khung nhìn (`FreezePanes(5, 4)`).

5. **Quy tắc Git & Token:**
   - Tuân thủ `m2m-protocol.md`: Giao tiếp Zero-Fat bằng cờ tín hiệu (`[ACK]`, `[STATUS: DONE]`, `[STATUS: ESCALATE]`).
   - CẤM tự ý commit Git. Giữ nguyên nhánh hiện tại để người dùng tự kiểm tra và commit.
   - Khi gọi Subagents, BẮT BUỘC chọn `Model: inherit` để kế thừa model của phiên làm việc.
