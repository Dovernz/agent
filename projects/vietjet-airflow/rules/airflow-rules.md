---
name: airflow-rules
description: Quy định riêng cho dự án Hạ tầng Airflow Vietjet.
trigger: model_decision
---

# Quy định riêng - Dự án Vietjet Airflow

1. **Vị trí tệp tin:** Mọi DAG mới phải được lưu và kiểm thử trong `D:\Vietjet\Gitlab\test\dags\` trước khi chuyển sang `D:\Vietjet\Gitlab\vj-prod-airflow-cc\dags\`.
2. **Docker-First:** Mọi kiểm thử DAG phải thực hiện qua Docker container `test-airflow-webserver-1` (sử dụng script `scripts/fast_test_dag.py --docker`). Không làm ô nhiễm môi trường máy host.
3. **Giao tiếp Zero-Fat M2M:** Các subagent chỉ trao đổi tín hiệu cờ chuẩn và JSON payload:
   - `[ACK]`
   - `[STATUS: DONE]`
   - `[STATUS: FAIL] {"log_file": "path/to/error.log"}` (CẤM dán error stacktrace dài vào chat context)
   - `[STATUS: ESCALATE]` (Khi sửa lỗi quá 3 lần thất bại)
   - `[SPEC_CHANGED]`
4. **Git Safety:** KHÔNG tự động chạy lệnh `git commit` hay `git push`. Để lại toàn bộ staged/unstaged changes cho User tự kiểm tra và commit.
5. **Auto-Cleanup:** Tự động dọn sạch các file DAG kiểm thử tạm (`/tmp/_test_check_dag.py` trong Docker và các file scratch trên ổ cứng).
