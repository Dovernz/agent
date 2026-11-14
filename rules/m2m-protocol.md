# M2M Agent Communication Protocol (Quy Tắc Giao Tiếp Đa Tác Nhân)

> Phiên bản cô đọng. Toàn bộ chi tiết tại: @[M2M Protocol Detail](./m2m-protocol-detail.md)

1. **Giao tiếp Zero-Fat:** Tuyệt đối không chào hỏi, giải thích dài dòng, hay lặp lại câu hỏi. CHỈ dùng Cờ tín hiệu hoặc JSON Payload tối giản.
2. **Cờ tín hiệu chuẩn hóa:** - `[ACK]`: Đã nhận lệnh. `[STATUS: DONE]`: Xong. `[STATUS: FAIL] {"log_file": "..."}`: Lỗi (chỉ gửi path, cấm dump log). `[STATUS: ESCALATE]`: Lặp >3 lần hoặc bế tắc.
3. **Tiết kiệm Context Code:** Khi fix bug, KHÔNG in lại file code ra chat. Tự dùng tool ghi thẳng vào file ổ cứng.
4. **Đồng bộ Model (Inherit):** Mọi Sub-agent được gọi lên BẮT BUỘC dùng chế độ cấu hình `Model: inherit` để kế thừa chính xác Model gốc mà User đang dùng. Tuyệt đối không tự ý đổi model.
5. **Quy tắc Peek-and-Script (Bảo toàn Token cho File Dữ liệu / Excel / CSV):**
   - **TUYỆT ĐỐI CẤM** đọc toàn bộ nội dung file Excel/CSV/code lớn vào context chat. Chỉ khảo sát Header + 3-5 dòng mẫu, xử lý bằng script bên ngoài.
6. **Cơ Chế Diệt Sub-Agent & Task Treo Quá Lâu (Timeout & Kill Zombie Sub-Agents):**
   - Giám sát thời gian thực thi (< 5 phút). Quá thời gian gọi ngay `manage_subagents(kill)` hoặc `manage_task(kill)` và phát `[STATUS: ESCALATE]`.
7. **Kiểm Soát Phân Tầng 3 Cấp & Cấm Đệ Quy Cấp 4 (Bounded 3-Tier Hierarchy & Anti-Nesting Policy):**
   - Mô hình 3 tầng: Master Agent -> Project PM -> Tech Lead / Workers. Cấp Worker BẮT BUỘC đặt `EnableSubagentTools: false` và `Workspace: inherit`.
8. **Chuẩn Hóa Giao Tiếp Nội Bộ Bằng Code & JSON Payload:**
   - Mọi giao tiếp giữa PM và Leads chỉ dùng JSON Code Payload tối giản.
9. **Cơ Chế Cảnh Báo Ngân Sách Token Thời Gian Thực (Token Budget Watchdog & Hyper-Zero-Fat Mode):**
   - Ngưỡng cảnh báo mềm cho phiên làm việc là `120,000 tokens`. Khi chạm ngưỡng, chuyển sang Hyper-Zero-Fat (chỉ gửi JSON path file, cấm mọi giải thích).
10. **Cơ Chế Bàn Giao Ngữ Cảnh Xuyên Phiên (Cross-Session Checkpoint Protocol):**
    - Mỗi dự án BẮT BUỘC duy trì và ĐỌC `projects/<project_name>/knowledge/checkpoint.md` trước khi bắt đầu bất kỳ task nào.
11. **Quy Tắc Tự Động Dọn Dẹp Tập Tin Rác & Ảnh Chụp Màn Hình (Workspace Hygiene & Auto-Cleanup Protocol):**
    - Cấm để lại file rác, script tạm hay ảnh chụp màn hình trong source code. Quét sạch bằng `hub_cleaner.py`.
12. **Git Là Nguồn Chân Lý Duy Nhất (Git-As-Single-Source-Of-Truth - SSoT):**
    - Đọc trực tiếp từ Git repo và duy trì working tree sạch sẽ.
13. **Truy Vấn Tức Thì Gemini Key Pool (Instant Pool Status Trigger):**
    - Khi hỏi `pool status`, `quota api`, `hub usage` $\rightarrow$ tự động chạy `hub usage` và in bảng trạng thái.
14. **Quy Trình Kiểm Định & Hội Đồng Thẩm Định Output (Output Verification & Multi-Tier Review Gate):**
    - 100% output mã nguồn phải qua `hub verify <filepath>` đạt 100/100 Quality Gate.
15. **Quy Trình Phân Nhánh Động Của Nhóm Lead & Phối Hợp API Worker (Dynamic Lead Fan-Out & API Worker Protocol):**
    - Đánh giá độ phức tạp và chia nhỏ cho các Workers con thực thi độc lập ($N \le 5$).
16. **Quy Tắc Ép Buộc Ủy Thác API & Phân Vai Subagent (Code via API & Subagent as Reviewer):**
    - **CẤM TUYỆT ĐỐI tự sinh code trong chat:** 100% code phải sinh qua `hub gemini`:
      ```powershell
      hub gemini --prompt "<yêu_cầu>" --out "<đường_dẫn_file>" --tier <auto|bulk|standard|deep|ultra|live_translate|transcribe>
      ```
    - **Subagent chỉ đóng vai trò Reviewer & Storekeeper:** Nếu API không tự ghi file được, Subagent chỉ nhận kết quả, review cú pháp, lưu vào file đĩa, thẩm định qua `hub verify` và báo cáo M2M 3 dòng lên cấp trên. TUYỆT ĐỐI CẤM in lại code vào khung chat context.
17. **Chốt Chặn Terminal Output (Cấm Dump Log Vào Context):**
    - Mọi lệnh terminal (`run_command`) khi xem log, quét thư mục, chạy test, build, Docker BẮT BUỘC pipe qua `| Select-Object -First 30` hoặc `tail -n 30` hoặc xuất ra file log tạm. CẤM in > 30 dòng.
18. **Quy Tắc Kích Hoạt Hệ Thống Toàn Quyền (`/master-agent`, `/agent-system` & "sử dụng hệ thống agent"):**
    - Master Agent nhận lệnh, định tuyến đúng Project PM và giao việc M2M.
19. **Quy Tắc Phân Mảnh Ngữ Cảnh & Cô Lập Subagent (Dynamic Context Sharding & Subagent Isolation):**
    - Không nạp monolithic context. Dùng `hub shard auto "<prompt>"` để nạp shard dự án và `hub shard reset` khi xong việc.
20. **Quy Tắc Zero-Execution Trong Main Chat & Chuyển Giao Phản Ứng Tự Động (Zero-Execution & Reactive Wakeup):**
    - **CẤM TUYỆT ĐỐI** Master Agent tự đọc file code dự án, tự sửa code, tự chạy docker/build/test/migrate trong Main Chat. **CẤM DÙNG `schedule` HOẶC VÒNG LẶP POLLING.** Master Agent chỉ chọn đúng Project PM, gọi `invoke_subagent` rồi DỪNG TOOL ngay. Chờ Reactive Wakeup từ tin nhắn M2M kết quả của Subagent để báo cáo 2-3 câu súc tích cho User.

21. **Quy Tắc Zero-Execution Cho Project PM (PM Zero-Execution & Mandatory Squad Delegation):**
    - **CẤM TUYỆT ĐỐI PM tự viết code, sửa file cấu hình hoặc tự chạy script terminal để vá lỗi:** PM chỉ là Tổng công trình sư điều phối (Orchestrator), KHÔNG PHẢI Worker.
    - **BẮT BUỘC ỦY THÁC CHO GLOBAL DEV SQUAD:** Khi nhận task từ Master Agent, PM bắt buộc phải phân rã và gọi invoke_subagent giao việc cho các Tech Leads tương ứng (lead-frontend, lead-backend, lead-devops, lead-qa, gitops-gatekeeper).
    - **Tech Leads phân rã thành Workers:** Workers gọi API ngoài (hub gemini --prompt ... --out ...) để sinh code / sửa file, kiểm định cú pháp qua hub verify, sau đó báo cáo ngược lên Tech Lead -> PM -> Master Agent.
