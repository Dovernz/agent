# Nhóm Skill Agent - Dự án Hạ Tầng Dữ Liệu Vietjet Airflow (`vietjet-airflow`)

Thư mục này chứa toàn bộ cấu hình, bộ nhớ kiến trúc, bộ kiểm thử Docker và nhóm Agent chuyên trách cho hệ thống **Vietjet Airflow Pipelines**.

## Vị trí Source Code & Môi trường
- **Mã nguồn DAGs Production:** `D:\Vietjet\Gitlab\vj-prod-airflow-cc`
- **Môi trường Test Docker:** `D:\Vietjet\Gitlab\test`
- **Tài liệu hướng dẫn:** `D:\Vietjet\Gitlab\AGENT_SYSTEM_GUIDE.md`

## Danh sách Agent chuyên trách
1. **`vj-pm-orchestrator`**: Project Manager / Điều phối tổng thể. Nhận yêu cầu, điều phối Spec -> Coder -> QA, kiểm soát QA Loop, đồng bộ Model inherit, KHÔNG tự commit Git.
2. **`vj-lead-architect`**: Data Architect Lead. Phân tích yêu cầu, sinh JSON AST Spec tối giản theo chuẩn M2M Zero-Fat, xác định schema kết nối (Postgres, SFTP, Oracle, S3, v.v.).
3. **`vj-lead-coder`**: Data Engineer Lead. Chuyển hóa JSON Spec thành mã DAG Python chuẩn TaskFlow API (`@dag`, `@task`), thiết lập timezone `Asia/Ho_Chi_Minh` và params date.
4. **`vj-lead-qa`**: Data QA Lead. Chạy kiểm thử cú pháp AST, cycle graph và kiểm thử DagBag trực tiếp trong container Docker `test-airflow-webserver-1`, Auto-Cleanup file tạm, xuất JSON log lỗi.

## Kiến trúc & Quy chuẩn
- Đọc chi tiết tại `knowledge/tech-stack.md` và `rules/airflow-rules.md`.
- Giao thức chung: `../../common/rules/m2m-protocol.md`.
- Tiết kiệm token cực hạn: Giao tiếp M2M chỉ trao đổi qua code và JSON schema nén, tuyệt đối không trò chuyện văn bản.
