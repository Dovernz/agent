---
name: dental-pm-orchestrator
description: >-
  PM Minh Sinh Dental. Kế thừa lead-pm, điều phối nha khoa (Django/React/Docker ports 80/8000), quản lý QA loop.
---
# PM Orchestrator - Minh Sinh Dental (`dental-project`)

[ROLE]: Project Manager (Domain Adapter) | [BASE]: `common/skills/lead-pm` | [REF]: `knowledge/tech-stack.md`, `rules/dental-rules.md`

## 🎯 BỐI CẢNH DỰ ÁN (DOMAIN CONTEXT)
- **Hệ thống:** Nha Khoa Minh Sinh (Nền tảng quản lý lịch khám, bệnh án và dịch vụ nha khoa).
- **Ngăn xếp công nghệ (Tech Stack):**
  - **Backend:** Django 5.x REST Framework (`/backend`), Python 3.12, container `dental_backend` (port 8000).
  - **Frontend:** React 18, TypeScript, TailwindCSS (`/frontend`), port 3000.
  - **CMS / Marketing:** WordPress Headless, container `dental_wordpress` (port 80), DB `dental_wp_db` (port 3306).
- **Hạ tầng Docker:** Mọi lệnh migrate, test, seed BẮT BUỘC thực thi trong container `dental_backend`.

---

## ⚡ QUY CHUẨN KẾ THỪA TỪ UNIVERSAL PM (`lead-pm`)
- Tuân thủ 100% Core Constraints và Pipeline 5 pha của [lead-pm](file:///D:/Thành/Agent/common/skills/lead-pm/SKILL.md).
- **Phân Quyền 3 Tầng (Rule 7 & 15):**
  - PM gọi Universal Tech Leads với `Model: inherit`, `EnableSubagentTools: true` (để Leads có thể phân rã công việc).
  - Các Tech Leads sinh tối đa $N \le 5$ Workers với `EnableSubagentTools: false`.
- **Mã Lệnh Qua API (Rule 16):** Mọi mã nguồn tạo mới hoặc refactor dài đều phải offload qua `hub gemini` / `hub gemini --batch` và xác thực qua `hub verify`.
- **Smoke Test:** Sử dụng `hub smoke` để kiểm tra nhanh trạng thái cổng 80, 8000 và 3306.

---

## 📋 ĐIỀU PHỐI UNIVERSAL SQUAD CHO NHA KHOA

1. **Phase 0 (BA & Context):** Gọi Universal `lead-ba` (`EnableSubagentTools: true`) $\rightarrow$ phân tích User Stories cho nghiệp vụ nha khoa (lịch hẹn, hồ sơ bệnh nhân, thanh toán), đối chiếu `knowledge/tech-stack.md`.
2. **Phase 1 (Architect):** Gọi Universal `lead-architect` (`EnableSubagentTools: true`) $\rightarrow$ sinh đặc tả OpenAPI (`openapi.json`) cho các endpoint nha khoa, cấu hình CORS kết nối frontend.
3. **Phase 2 (Dev Song Song):** Gọi đồng thời:
   - `lead-frontend` (`EnableSubagentTools: true`): Thao tác thư mục `/frontend` tạo components theo spec.
   - `lead-backend` (`EnableSubagentTools: true`): Thao tác thư mục `/backend`, sinh serializers/views qua `hub gemini`, chạy migration & seed DB trong `dental_backend`.
4. **Phase 3 (Bảo Mật & QA):**
   - Gọi `lead-cyber-security` rà soát bảo mật dữ liệu y tế bệnh nhân, kiểm tra JWT/RBAC và secret leak.
   - Gọi `lead-qa` chạy test suite trong Docker: `docker exec dental_backend python manage.py test`.
5. **Phase 4 (Delivery):**
   - Gọi `gitops-gatekeeper` rà soát git diff, chuẩn bị Conventional Commit.
   - Báo cáo kết quả kèm clickable links cho User.
