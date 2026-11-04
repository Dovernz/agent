# Nhóm Agent Giám Sát, Đo Đạc Token & Tối Ưu Hóa Kỹ Năng (`agent-supervisor`)

Nhóm Agent chuyên trách độc lập có nhiệm vụ kiểm toán phiên chạy, định lượng chính xác mức tiêu thụ Token, đánh giá hiệu năng và đưa ra khuyến nghị nâng cấp kỹ năng (Meta-Learning) cho toàn bộ hệ thống Antigravity.

---

## 👥 Danh Sách 4 Agent Chuyên Trách
1. **`supervisor-orchestrator`**: Chánh thanh tra & Trưởng nhóm giám sát. Điều phối phân tích sau phiên chạy, kích hoạt engine đo đạc và báo cáo kết quả cho User.
2. **`token-cost-profiler`**: Chuyên viên đo đạc token. Bóc tách Input/Output/Thinking tokens, phát hiện điểm nóng đốt token.
3. **`performance-evaluator`**: Kỹ sư đánh giá hiệu năng. Đo thời gian thực thi, tỷ lệ lỗi tool, phát hiện sub-agent treo hoặc lặp vô tận.
4. **`skill-meta-optimizer`**: Chuyên gia tối ưu hóa kỹ năng (Meta-Learning). Đề xuất cải tiến và cập nhật trực tiếp vào các file `SKILL.md`.

---

## 🛠️ Công Cụ Đi Kèm
- **Script kiểm toán tự động:** `scripts/audit_performance.py`
  - Đọc transcript JSONL của Antigravity.
  - Tính toán chính xác tổng tokens (Prompt, Completion, Thinking).
  - Xuất báo cáo Markdown và lưu tự động vào thư mục `reports/`.
- **Thư mục báo cáo lịch sử:** `reports/audit_report_<timestamp>.md`
- **Bộ chỉ số đo lường:** `knowledge/evaluation-metrics.md`
