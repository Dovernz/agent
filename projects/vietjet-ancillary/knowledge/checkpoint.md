# Project Checkpoint: vietjet-ancillary (PSS Ancillary & Databricks Migration)

- **Cập nhật lần cuối:** 2026-11-05 10:35
- **Trạng thái hiện tại:**
  - Quy chuẩn phân tích Stored Procedure cũ, logic phụ thu hành lý/chỗ ngồi/bữa ăn và kiến trúc Databricks Medallion đã sẵn sàng.
  - Công cụ Peek-and-Script giúp tiết kiệm 99% token khi khảo sát file dữ liệu PSS lớn.
- **Hạng mục đang xử lý dở dang:** Không có.
- **Hành động tiếp theo cần thực hiện:**
  1. Tiếp nhận tài liệu Tờ trình hoặc file DDL/SP mới từ User.
  2. `vietjet-pm-orchestrator` điều phối 4 subagents (`code-analyzer`, `policy-reader`, `catalog-inspector`, `excel-builder`).
  3. Bàn giao kết quả qua `gitops-gatekeeper`.
