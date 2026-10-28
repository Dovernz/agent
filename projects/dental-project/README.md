# Nhóm Skill Agent - Dự án Minh Sinh Dental (`dental_project`)

Thư mục này chứa toàn bộ cấu hình, bộ nhớ kiến trúc và nhóm Agent chuyên trách cho dự án **Minh Sinh Dental**.

## Vị trí Source Code
- **Mã nguồn:** `d:\Thành\WEB\Code\dental_project`
- **Tài liệu cấu trúc:** `d:\Thành\WEB\project_structure_updated.md`

## Danh sách Agent chuyên trách
1. **`dental-pm-orchestrator`**: Project Manager. Nhận yêu cầu, điều phối luồng, kiểm soát QA Loop, báo cáo User.
2. **`dental-lead-architect`**: Architect Lead. Thiết kế schema DB trong Docker, sinh OpenAPI spec, định nghĩa Security Gate.
3. **`dental-lead-frontend`**: Frontend Lead. Dàn trang Mobile-First, tự sinh API client từ spec, chạy linter trong Docker.
4. **`dental-lead-backend`**: Backend Lead. Xây dựng API, cấu hình CORS/Security, DB Seeding dữ liệu giả, linter trong Docker.
5. **`dental-lead-qa`**: QA Lead. Chạy E2E test trong Docker, code review, tear-down dữ liệu rác, dọn sạch script tạm.

## Kiến trúc & Quy chuẩn
- Đọc chi tiết tại `knowledge/tech-stack.md` và `rules/dental-rules.md`.
- Giao thức chung: `../../common/rules/m2m-protocol.md`.
