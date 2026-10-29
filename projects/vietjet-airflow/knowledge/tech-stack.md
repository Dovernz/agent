# Tech Stack Knowledge Base - Vietjet Airflow (`vietjet-airflow`)

Mọi Agent làm việc trên dự án Vietjet Airflow BẮT BUỘC tuân thủ:

- **Đường dẫn dự án:**
  - Production DAGs: `D:\Vietjet\Gitlab\vj-prod-airflow-cc\dags`
  - Local Test Environment: `D:\Vietjet\Gitlab\test`
- **Docker-First (BẢO VỆ MÁY GỐC):**
  - Mọi thao tác kiểm thử DAG, test nạp DagBag, check import error BẮT BUỘC chạy BÊN TRONG container Docker `test-airflow-webserver-1` (hoặc thông qua runner script `scripts/fast_test_dag.py --docker`).
  - Tuyệt đối KHÔNG cài đặt gói thư viện linh tinh hay chạy script gây rác môi trường Python máy host.
- **Airflow Standards (Chuẩn Vietjet):**
  - **API:** Ưu tiên Airflow 2.x TaskFlow API (`@dag`, `@task`). Tránh dùng các Operator cũ cồng kềnh nếu TaskFlow giải quyết gọn hơn.
  - **Timezone:** BẮT BUỘC dùng `pendulum.timezone("Asia/Ho_Chi_Minh")`. CẤM dùng `datetime.now()` không múi giờ.
  - **Backfill Storm Protection:** Luôn đặt `catchup=False`.
  - **Tham số chạy ngày (Batch T-1):** Luôn khai báo `params` với `date_from` và `date_to` dạng `Param(..., type="string", format="date")`. Cho phép đọc đè giá trị qua `context.get("dag_run").conf`.
  - **Connections & Secret:** Sử dụng Airflow Connections (`PostgresHook`, `SFTPHook`, `MySqlHook`, `OracleHook`, `S3Hook`). Không hardcode mật khẩu, host IP trong file DAG.
  - **Top-Level Code Prevention:** Tuyệt đối không query DB, request HTTP hoặc đọc file nặng ở phạm vi top-level scope (ngoài `@task`). Parse time của DAG phải < 0.5s.
- **Auto-Cleanup:**
  - Mọi file tạm tạo ra trong container `/tmp/_test_check_dag.py` hoặc file scratch trên máy phải được tự động xóa sạch sau khi kiểm thử xong.
- **Giao thức M2M & Model Inherit:**
  - Tuân thủ nghiêm ngặt `../../common/rules/m2m-protocol.md`.
  - Sub-agents BẮT BUỘC khai báo `Model: inherit` khi spawn.
