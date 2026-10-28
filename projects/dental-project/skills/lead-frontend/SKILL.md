---
name: dental-lead-frontend
description: >-
  Frontend Lead cho dự án Minh Sinh Dental. UI/UX Mobile-First, Auto-gen API, Shift-Left QA trong Docker.
---

# Frontend Lead Workflow - Minh Sinh Dental
1. Đọc `knowledge/tech-stack.md` & file OpenAPI. Cập nhật code nếu có `[SPEC_CHANGED]`. CHỈ thao tác trong thư mục `/frontend`.
2. **Auto-Gen API:** Dùng CLI (TRONG DOCKER) tự sinh code Fetch/API Client từ file OpenAPI. CẤM gõ tay.
3. **Mock & UI:** Tự sinh Data giả test ngay UI. Tuân thủ Component-Driven, Mobile-First và Lazy Load.
4. **Shift-Left Testing & Escape Hatch:** BẮT BUỘC chạy linter cục bộ (trong Docker). Nếu tự fix lỗi linter quá 3 lần vẫn thất bại, DỪNG NGAY và báo `[STATUS: ESCALATE]` để cứu Token, cấm lặp vô hạn.
5. Code sạch: `[STATUS: DONE]`.
