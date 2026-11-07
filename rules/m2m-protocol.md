# M2M Agent Communication Protocol (Quy Tắc Giao Tiếp Đa Tác Nhân)

> Phiên bản cô đọng. Toàn bộ chi tiết tại: @[M2M Protocol Detail](./m2m-protocol-detail.md)

1. **Giao tiếp Zero-Fat:**: Tuyệt đối không chào hỏi, giải thích dài dòng, hay lặp lại câu hỏi. CHỈ dùng Cờ tín hiệu hoặc JSON Payload tối giản.
2. **Cờ tín hiệu chuẩn hóa:**: - `[ACK]`: Đã nhận lệnh.
3. **Tiết kiệm Context Code:**: Khi fix bug, KHÔNG in lại file code ra chat. Tự dùng tool ghi thẳng vào file ổ cứng.
4. **Đồng bộ Model (Inherit):**: Mọi Sub-agent được gọi lên BẮT BUỘC dùng chế độ cấu hình `Model: inherit` để kế thừa chính xác Model gốc mà User đang dùng. Tuyệt đối không tự ý đổi model.
5. **Quy tắc Peek-and-Script (Bảo toàn Token cho File Dữ liệu / Excel / CSV):**: - **TUYỆT ĐỐI CẤM** đọc toàn bộ nội dung file Excel/CSV lớn vào context chat (no full read, no dumping thousands of lines).
6. **Cơ Chế Diệt Sub-Agent & Task Treo Quá Lâu (Timeout & Kill Zombie Sub-Agents):**: - **Giám sát thời gian thực thi:** Mỗi sub-agent hoặc tác vụ nền chỉ được phép chạy trong khoảng thời gian hợp lý (< 5 phút).
7. **Kiểm Soát Phân Tầng 3 Cấp & Cấm Đệ Quy Cấp 4 (Bounded 3-Tier Hierarchy & Anti-Nesting Policy):**: - Mô hình 3 tầng phân cấp chuẩn mực: Master Agent -> Project PM -> Tech Lead / Workers. Cấm lồng nhau quá sâu.
8. **Chuẩn Hóa Giao Tiếp Nội Bộ Bằng Code & JSON Payload:**: - Mọi giao tiếp giữa Thư ký (Master Secretary) và Project PM, hoặc giữa các Lead Agent với nhau **BẮT BUỘC** được bọc trong JSON Code Payload tối giản.
9. **Cơ Chế Cảnh Báo Ngân Sách Token Thời Gian Thực (Token Budget Watchdog & Hyper-Zero-Fat Mode):**: - **Giám sát ngưỡng token:** Ngưỡng cảnh báo mềm cho phiên làm việc là `120,000 tokens`.
10. **Cơ Chế Bàn Giao Ngữ Cảnh Xuyên Phiên (Cross-Session Checkpoint Protocol):**: - **Tệp lưu trữ chuẩn:** Mỗi dự án BẮT BUỘC duy trì tệp `projects/<project_name>/knowledge/checkpoint.md`.
11. **Quy Tắc Tự Động Dọn Dẹp Tập Tin Rác & Ảnh Chụp Màn Hình (Workspace Hygiene & Auto-Cleanup Protocol):**: - **Cấm để lại file rác:** Toàn bộ các script tạm chạy 1 lần và các file ảnh chụp màn hình debug phải được tự động dọn dẹp.
12. **Git Là Nguồn Chân Lý Duy Nhất (Git-As-Single-Source-Of-Truth - SSoT):**: - **Không lưu dữ liệu thừa trên máy:** Sau khi commit và push lên remote Git, toàn bộ tiến độ, lịch sử và trạng thái đều được lưu trữ an toàn.
13. **Truy Vấn Tức Thì Gemini Key Pool (Instant Pool Status Trigger):**: - Khi người dùng hỏi `pool status`, `kiểm tra pool`, `quota api`, `hub usage`: Tự động kích hoạt hiển thị tình trạng 7 key.
14. **Quy Trình Kiểm Định & Hội Đồng Thẩm Định Output (Output Verification & Multi-Tier Review Gate):**: - **Không tin tưởng mù quáng:** 100% output phải qua `hub verify` đạt 100/100 Quality Gate.
15. **Quy Trình Phân Nhánh Động Của Nhóm Lead & Phối Hợp API Worker (Dynamic Lead Fan-Out & API Worker Protocol):**: - Đánh giá độ phức tạp và chia nhỏ cho các Workers con thực thi độc lập.
16. **Quy Tắc Ép Buộc Ủy Thác API Lên Mức Tối Đa (Maximal API Offloading & Zero In-Chat Coding):**: - **CẤM TUYỆT ĐỐI việc tự sinh code trong ngữ cảnh chat Antigravity:** 100% code, tests, DDL phải sinh qua `hub gemini` (7 Projects Free Tier 0 VNĐ).
17. **Quy Tắc Kích Hoạt Hệ Thống Toàn Quyền (`/master-agent`, `/agent-system` & "sử dụng hệ thống agent"):**: - Master Agent nhận lệnh, định tuyến đúng Project PM và giao việc M2M.
18. **Quy Tắc Phân Mảnh Ngữ Cảnh & Cô Lập Subagent (Dynamic Context Sharding & Subagent Isolation):**: - Không nạp monolithic context. Dùng `hub shard auto` để nạp đúng shard dự án và `hub shard reset` khi xong việc.
19. **Quy Tắc Zero-Execution Trong Main Chat & Chuyển Giao Phản Ứng Tự Động (Zero-Execution & Reactive Wakeup):**: - **CẤM TUYỆT ĐỐI** Master Agent tự đọc file code dự án, tự sửa code, tự chạy docker/build/test/migrate trong Main Chat. **CẤM DÙNG `schedule` HOẶC VÒNG LẶP POLLING.** Master Agent chỉ chọn đúng Project PM, gọi `invoke_subagent` rồi DỪNG TOOL ngay. Chờ Reactive Wakeup từ tin nhắn M2M kết quả của Subagent để báo cáo 2-3 câu súc tích cho User.
