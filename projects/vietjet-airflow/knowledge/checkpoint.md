# Project Checkpoint: vietjet-airflow (Hạ Tầng Dữ Liệu & Airflow Pipelines Vietjet)

- **Cập nhật lần cuối:** 2026-11-06 14:10
- **Trạng thái hiện tại:**
  - Đã chuẩn hóa và tinh gọn: Chuyển giao toàn bộ kỹ năng lập trình và kiểm thử sang **Universal Squad** trong `common/skills/`.
  - Quy chuẩn DAG TaskFlow API chuẩn Airflow 2.10, timezone `Asia/Ho_Chi_Minh`.
  - Bộ kiểm thử đa tầng siêu tốc (`scripts/fast_test_dag.py` trong Docker `test-airflow-webserver-1`) hoạt động ổn định.
- **Hạng mục đang xử lý dở dang:** Không có pipeline bị lỗi. Hệ thống đạt chuẩn 100%.
- **Hành động tiếp theo cần thực hiện:**
  1. Khi nhận yêu cầu pipeline dữ liệu mới: `vj-pm-orchestrator` gọi Universal `lead-architect` sinh JSON DAG Spec.
  2. Bàn giao Universal `lead-backend` sinh mã DAG TaskFlow theo `templates/vietjet_dag_base.py`.
  3. Bàn giao Universal `lead-qa` chạy kiểm thử Docker DagBag và rà soát an ninh qua `lead-cyber-security`.
  4. Kích hoạt `gitops-gatekeeper` kiểm tra an toàn trước khi push GitLab.
