# Project Checkpoint: vietjet-airflow (Hạ Tầng Dữ Liệu & Airflow Pipelines Vietjet)

- **Cập nhật lần cuối:** 2026-11-05 10:35
- **Trạng thái hiện tại:**
  - Quy chuẩn DAG TaskFlow API chuẩn Airflow 2.10, timezone `Asia/Ho_Chi_Minh`.
  - Bộ kiểm thử đa tầng siêu tốc (AST parsing, cycle detection, nạp DagBag trong container Docker `test-airflow-webserver-1`) hoạt động ổn định.
- **Hạng mục đang xử lý dở dang:** Không có pipeline bị lỗi.
- **Hành động tiếp theo cần thực hiện:**
  1. Khi nhận yêu cầu pipeline dữ liệu mới: `vj-pm-orchestrator` gọi `vj-lead-architect` sinh JSON AST Spec.
  2. Bàn giao `vj-lead-coder` sinh mã DAG.
  3. Bàn giao `vj-lead-qa` chạy kiểm thử Docker DagBag.
  4. Kích hoạt `gitops-gatekeeper` kiểm tra an toàn trước khi push GitLab.
