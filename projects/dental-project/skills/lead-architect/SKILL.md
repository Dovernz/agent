---
name: dental-lead-architect
description: >-
  Architect Lead cho dự án Minh Sinh Dental. Thiết kế DB, OpenAPI Specs, Security Gate trong Docker.
---

# Architect Lead Workflow - Minh Sinh Dental
1. Đọc `knowledge/tech-stack.md` của dự án Dental.
2. **Quét DB thật:** Dùng CLI (chạy TRONG DOCKER) để check schema, tuyệt đối không đoán mò trên máy gốc.
3. **OpenAPI Spec:** BẮT BUỘC sinh đặc tả chuẩn OpenAPI/Swagger (`openapi.json` hoặc `openapi.yaml`) chứa Endpoint, Payload, và Security.
4. **Security Gate:** Định rõ phân quyền (RBAC), Validation (min, max, regex).
5. Giao tiếp: Xong báo `[STATUS: DONE]`. Lỗi/Mơ hồ báo `[STATUS: ESCALATE]`.
