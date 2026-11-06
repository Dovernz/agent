# Dự Án Hạ Tầng Dữ Liệu Vietjet Airflow (`vietjet-airflow`)

Quản lý hạ tầng dữ liệu và Airflow Pipelines cho Vietjet Air, tích hợp trực tiếp với Universal Squad và Docker container `test-airflow-webserver-1`.

## 📁 Cấu Trúc Dự Án
- `knowledge/`: Tech stack Airflow 2.10, TaskFlow API và checkpoint tiến độ.
- `rules/`: Quy định Docker test và chuẩn giao tiếp M2M Zero-Fat.
- `schemas/`: JSON Schemas đặc tả DAG spec.
- `scripts/`: Bộ kiểm thử siêu tốc (`fast_test_dag.py`).
- `templates/`: DAG template chuẩn Vietjet (`vietjet_dag_base.py`).
- `skills/`:
  - `vj-pm-orchestrator`: PM điều phối luồng thực thi xuống Universal Squad.

## 🛠️ Điều Phối Thực Thi (Universal Squad)
- **Thiết kế Pipeline:** `lead-architect` (sinh spec theo `schemas/dag_spec.json`).
- **Lập trình DAG Python:** `lead-backend` (sinh code theo `templates/vietjet_dag_base.py`).
- **Kiểm thử Đa tầng:** `lead-qa` (chạy `scripts/fast_test_dag.py` trong Docker).
- **An toàn Bảo mật:** `lead-cyber-security` (rà soát connections & secrets).
