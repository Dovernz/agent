# Kiến trúc Công nghệ (Tech Stack Knowledge Base)

File này chứa các nguyên tắc cốt lõi của dự án. Mọi Agent (Architect, Frontend, Backend) BẮT BUỘC đọc và tuân thủ trước khi bắt tay vào thiết kế hay code:

- **Nguyên tắc chung:** Giữ code ngắn gọn, không lặp lại (DRY), chia nhỏ component, ưu tiên tái sử dụng cao nhất có thể.
- **Dọn dẹp (Auto-Cleanup):** Luôn dọn dẹp các script tạm, file test chạy một lần (`one-off scripts/scratch files`) sau khi sử dụng để giữ workspace và dự án sạch sẽ.
- **Tiêu chuẩn Giao tiếp:** Tuân thủ chặt chẽ M2M Protocol (`.agents/rules/m2m-protocol.md`).

*(User có thể bổ sung các chuẩn công nghệ cụ thể của dự án vào file này, ví dụ: "Bắt buộc dùng Tailwind", "Sử dụng PostgreSQL", v.v.)*
