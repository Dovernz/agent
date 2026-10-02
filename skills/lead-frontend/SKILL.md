---
name: lead-frontend
description: >-
  Frontend Lead. UI/UX Mobile-First, Auto-gen API, Shift-Left QA.
---

# Frontend Lead Workflow
1. Đọc `knowledge/tech-stack.md` & file OpenAPI. Cập nhật code nếu có `[SPEC_CHANGED]`.
2. **Auto-Gen API:** Dùng CLI (như `openapi-typescript-codegen` hoặc thư viện tương đương) để tự động sinh code Fetch/API Client từ file OpenAPI. CẤM gõ tay code call API để tiết kiệm Token.
3. **Mock & UI:** Tự sinh Data giả test ngay UI. Tuân thủ Component-Driven, Mobile-First và Lazy Load.
4. **Shift-Left Testing:** BẮT BUỘC dùng Terminal chạy linter cục bộ và tự fix 100% lỗi syntax TRƯỚC KHI báo QA `[STATUS: DONE]`.
