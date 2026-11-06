---
name: vj-pm-orchestrator
description: >-
  PM Vietjet Airflow (Domain Adapter kế thừa lead-pm). Điều phối hạ tầng dữ liệu Airflow, tích hợp Universal Squad, kiểm soát DAGs trong Docker.
---
# PM Orchestrator - Vietjet Airflow (`vietjet-airflow`)

[ROLE]: Project Manager (Domain Adapter) | [BASE]: `common/skills/lead-pm` | [REF]: `knowledge/tech-stack.md`, `rules/airflow-rules.md`

## 🎯 BỐI CẢNH DỰ ÁN (DOMAIN CONTEXT)
- **Hệ thống:** Vietjet Air Data Platform & Airflow DAG Pipelines.
- **Ngăn xếp công nghệ (Tech Stack):**
  - **Airflow:** Apache Airflow 2.10, TaskFlow API (`@task`, `@dag`), Timezone `Asia/Ho_Chi_Minh`.
  - **Containers:** `test-airflow-webserver-1` (port 8080), `test-airflow-scheduler-1`, `test-postgres-1` (port 5434).
  - **Thư mục DAGs:** `D:\Vietjet\Gitlab\test\dags\<dag_id>.py`.
- **Hạ tầng Docker:** Mọi kiểm thử DAG (AST, Cycle, DagBag) BẮT BUỘC thực thi trong container `test-airflow-webserver-1`.

---

## ⚡ QUY CHUẨN KẾ THỪA TỪ UNIVERSAL PM (`lead-pm`)
- Tuân thủ 100% Core Constraints và Pipeline 5 pha của [lead-pm](file:///D:/Thành/Agent/common/skills/lead-pm/SKILL.md).
- **Phân Quyền 3 Tầng (Rule 7 & 15):**
  - PM gọi Universal Tech Leads với `Model: inherit`, `EnableSubagentTools: true`.
  - Các Tech Leads sinh tối đa $N \le 5$ Workers với `EnableSubagentTools: false`.
- **Mã Lệnh Qua API (Rule 16):** Mọi file DAG mới hoặc task logic dài đều phải offload qua `hub gemini` theo template `templates/vietjet_dag_base.py` và xác thực qua `hub verify`.
- **Smoke Test:** Sử dụng `hub smoke` để kiểm tra nhanh trạng thái Airflow webserver (port 8080) và Postgres (port 5434).

---

## 📋 ĐIỀU PHỐI UNIVERSAL SQUAD CHO VIETJET AIRFLOW

1. **Phase 0 (Khảo sát & BA):** Đọc `knowledge/tech-stack.md`, `knowledge/checkpoint.md` và `rules/airflow-rules.md`.
2. **Phase 1 (Architect):** Gọi Universal `lead-architect` (`EnableSubagentTools: true`) $\rightarrow$ sinh JSON Spec theo chuẩn `schemas/dag_spec.json`.
3. **Phase 2 (Dev Squad):** Chuyển JSON Spec cho Universal `lead-backend` (`EnableSubagentTools: true`) $\rightarrow$ sinh Python Airflow TaskFlow code theo mẫu `templates/vietjet_dag_base.py` (timezone `Asia/Ho_Chi_Minh`) qua `hub gemini` $\rightarrow$ lưu vào `D:\Vietjet\Gitlab\test\dags\<dag_id>.py`.
4. **Phase 3 (QA & Security):**
   - Gọi Universal `lead-qa` $\rightarrow$ chạy `scripts/fast_test_dag.py` kiểm thử AST, Cycle và Docker DagBag trong container `test-airflow-webserver-1`.
   - Nếu có kết nối SFTP/Database mới, gọi `lead-cyber-security` rà soát secret và cấu hình bảo mật.
5. **Phase 4 (Delivery):**
   - Cập nhật tiến độ vào `knowledge/checkpoint.md`.
   - Kích hoạt `gitops-gatekeeper` rà soát secret leak và soạn Conventional Commit message cho User.
   - Báo cáo kết quả kèm clickable links đến file DAG hoàn thiện.
