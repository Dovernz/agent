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

---

## 📋 Danh Mục Lệnh CLI Tái Sử Dụng (Reusable CLI Registry)

Bảng tra cứu nhanh các lệnh chuẩn hóa phục vụ kiểm thử DAG, nạp DagBag, phân tích dữ liệu Maureva và soi dữ liệu:

### 1. Kiểm Thử Cú Pháp & Cấu Trúc AST DAG (Zero-Token Static Check)
> Chạy kiểm tra AST, phát hiện chu trình phụ thuộc (cyclic dependency), quy chuẩn timezone Asia/Ho_Chi_Minh và params:

- **Kiểm thử tĩnh AST file DAG:**
  ```powershell
  & "C:\Users\thanhcaotien\.local\bin\uv.exe" run python "D:\Thành\Agent\projects\vietjet-airflow\scripts\fast_test_dag.py" "<đường_dẫn_file_dag.py>"
  ```

### 2. Nạp & Kiểm Thử DagBag Trong Docker Container `test-airflow-webserver-1`
> Xác thực nạp DAG thực tế trong môi trường Airflow không gây lỗi Import Error:

- **Chạy kiểm thử toàn diện kèm nạp DagBag trong Docker:**
  ```powershell
  & "C:\Users\thanhcaotien\.local\bin\uv.exe" run python "D:\Thành\Agent\projects\vietjet-airflow\scripts\fast_test_dag.py" "<đường_dẫn_file_dag.py>" --docker
  ```
- **Kiểm tra trực tiếp Import Errors của DagBag trong container:**
  ```powershell
  docker exec test-airflow-webserver-1 python -c "from airflow.models import DagBag; bag = DagBag('/opt/airflow/dags'); print('Import errors count:', len(bag.import_errors)); [print(k, '-->', v) for k, v in bag.import_errors.items()]"
  ```
- **Kiểm tra danh sách DAG đã load thành công trong container:**
  ```powershell
  docker exec test-airflow-webserver-1 airflow dags list
  ```

### 3. Phân Tích & Bóc Tách Dữ Liệu Maureva (`inspect_maureva.py`)
> Trích xuất và đối chiếu các trường doanh thu, coupon, phụ phí từ file CSV Maureva:

- **Chạy script phân tích Maureva:**
  ```powershell
  & "C:\Users\thanhcaotien\.local\bin\uv.exe" run python "D:\Thành\Agent\projects\vietjet-airflow\scripts\inspect_maureva.py"
  ```

### 4. Soi Dữ Liệu Cột & Mẫu File Tiết Kiệm Token (Peek Data Utility)
> Soi nhanh file cấu hình, metadata CSV/JSON của pipeline Airflow mà không tràn ngữ cảnh:

- **Soi file dữ liệu/metadata:**
  ```powershell
  & "C:\Users\thanhcaotien\.local\bin\uv.exe" run python "D:\Thành\Agent\common\scripts\peek_data.py" "<đường_dẫn_file>" --rows 3
  ```
