---
name: m2m-protocol
description: Quy định giao tiếp Machine-to-Machine nội bộ. Tự động kích hoạt (always_on) để ÉP XUNG tối đa hiệu năng và siêu tiết kiệm Token.
trigger: always_on
---

# M2M Communication Protocol (Rules)

Mọi Agent BẮT BUỘC tuân thủ luật tiết kiệm Token cực hạn (Extreme Token Saving) sau:

1. **Giao tiếp Zero-Fat:** Tuyệt đối không chào hỏi, giải thích dài dòng, hay lặp lại câu hỏi. CHỈ dùng Cờ tín hiệu hoặc JSON Payload tối giản.
2. **Cờ tín hiệu chuẩn hóa:**
   - `[ACK]`: Đã nhận lệnh.
   - `[STATUS: DONE]`: Hoàn thành.
   - `[STATUS: FAIL] {"log_file": "..."}`: Thất bại. (Chỉ gửi đường dẫn, cấm in log ra chat).
   - `[STATUS: ESCALATE]`: Lặp quá 3 lần hoặc sự cố nghẽn luồng, dừng lại tránh đốt Token.
   - `[SPEC_CHANGED]`: Báo thay đổi Spec.
   - `[STATUS: TIMEOUT_KILLED]`: Đã tự động kill sub-agent/task bị treo quá giờ.
3. **Tiết kiệm Context Code:** Khi fix bug, KHÔNG in lại file code ra chat. Tự dùng tool ghi thẳng vào file ổ cứng.
4. **Đồng bộ Model (Inherit):** Mọi Sub-agent được gọi lên BẮT BUỘC dùng chế độ cấu hình `Model: inherit` để kế thừa chính xác Model gốc mà User đang dùng. Tuyệt đối không tự ý đổi sang model khác.
5. **Quy tắc Peek-and-Script (Bảo toàn Token cho File Dữ liệu / Excel / CSV):**
   - **TUYỆT ĐỐI CẤM** đọc toàn bộ nội dung file Excel/CSV lớn vào context chat (no full read, no dumping thousands of lines).
   - Khi nhận file hoặc đường dẫn, **BẮT BUỘC chỉ khảo sát (Peek)** tên Sheet, kích thước, dòng Header và tối đa 3-5 dòng mẫu đầu tiên (sử dụng `peek_data_sample.ps1` hoặc lệnh `-Head 5`).
   - Sau khi nắm cấu trúc cột, **BẮT BUỘC viết script (PowerShell / Python)** để lọc, join, nhóm và tổng hợp dữ liệu trực tiếp trên máy hoặc xuất ra file kết quả.
   - **CHỈ đưa vào context chat** các số liệu thống kê rút gọn (Counts, Categories) hoặc đường dẫn file kết quả.
6. **Cơ Chế Diệt Sub-Agent & Task Treo Quá Lâu (Timeout & Kill Zombie Sub-Agents):**
   - **Giám sát thời gian thực thi:** Mỗi sub-agent hoặc tác vụ nền (background task / command) chỉ được phép chạy trong một khoảng thời gian hợp lý (ngưỡng timeout tối đa 5-10 phút tùy độ phức tạp).
   - **Tự động Kill khi Treo/Hold:** Nếu một sub-agent bị treo (hang), đứng hình (idle/hold quá lâu), lặp vô tận hoặc không trả về phản hồi/tín hiệu:
     * PM / Orchestrator **BẮT BUỘC** gọi ngay công cụ `manage_subagents` với `Action: "kill"` (truyền `ConversationIds`) hoặc `Action: "kill_all"` để lập tức tiêu diệt sub-agent bị treo.
     * Với command / tiến trình chạy ngầm bị nghẽn, gọi ngay `manage_task` với `Action: "kill"` (truyền `TaskId`).
   - **Xử lý sau khi Kill:** Báo cờ `[STATUS: ESCALATE] {"reason": "Subagent/Task timeout killed"}` và xin ý kiến User hoặc chia nhỏ task để chạy lại, **TUYỆT ĐỐI KHÔNG** để sub-agent treo ngầm vô thời hạn làm cạn kiệt Quota và treo máy.
7. **Kiểm Soát Phân Tầng Sub-Agent & Cấm Đệ Quy (Sub-Agent Boundary & Anti-Nesting Policy):**
   - **Khóa quyền tự tạo:** Khi định nghĩa sub-agent bằng `define_subagent`, **BẮT BUỘC** thiết lập `EnableSubagentTools: false` cho tất cả các sub-agent cấp con (Lead, Worker, Tester).
   - **Cấm tự do sinh Sub-Agent:** Các sub-agent do Agent tạo ra **TUYỆT ĐỐI KHÔNG ĐƯỢC PHÉP** tự ý tạo hoặc gọi thêm sub-agent cấp dưới nữa (ngăn chặn phân nhánh đệ quy không kiểm soát gây cạn kiệt CPU, RAM và Token).
   - **Ngoại lệ duy nhất:** Chỉ những dự án có cấu hình đặc thù được khai báo tường minh trong file SKILL của Manager dự án đó mới được cấp quyền phân nhánh, và tối đa không quá 2 tầng phân cấp (Master Secretary $\rightarrow$ Project PM $\rightarrow$ Lead/Worker). Cấp Worker cuối cùng luôn luôn là `EnableSubagentTools: false`.
8. **Chuẩn Hóa Giao Tiếp Nội Bộ Bằng Code & JSON Payload:**
   - Mọi giao tiếp giữa Thư ký (Master Secretary) và Project PM, hoặc giữa các Lead Agent với nhau **BẮT BUỘC** được bọc trong JSON Code Payload tối giản:
     * Lệnh điều phối: `{"dispatch_to": "<TÊN_PM>", "action": "EXECUTE_TASK", "task_id": "...", "payload": {...}}`
     * Báo cáo tiến độ: `{"status": "DONE|FAIL|ESCALATE", "task_id": "...", "summary": "...", "artifacts": [...]}`
   - Nghiêm cấm hội thoại tự nhiên giữa các Agent để tiết kiệm 100% token context.
9. **Cơ Chế Cảnh Báo Ngân Sách Token Thời Gian Thực (Token Budget Watchdog & Hyper-Zero-Fat Mode):**
   - **Giám sát ngưỡng token:** Ngưỡng cảnh báo mềm cho phiên làm việc là `120,000 tokens`.
   - **Kích hoạt Hyper-Zero-Fat:** Khi nhận tín hiệu `[STATUS: TOKEN_BUDGET_WARNING]`, toàn bộ các Agent **BẮT BUỘC** chuyển sang chế độ Siêu Nén:
     * CẤM in bất kỳ đoạn văn bản phân tích dài dòng hay giải thích lý do vào chat.
     * CHỈ trả về cờ M2M và JSON đường dẫn file kết quả: `[STATUS: DONE] {"artifacts": ["path/to/file"]}`.
     * Ưu tiên 100% chạy script ngoài context (Code-Over-Prompt), ngăn chặn context window phình to.
10. **Cơ Chế Bàn Giao Ngữ Cảnh Xuyên Phiên (Cross-Session Checkpoint Protocol):**
    - **Tệp lưu trữ chuẩn:** Mỗi dự án BẮT BUỘC duy trì tệp `projects/<project_name>/knowledge/checkpoint.md`.
    - **Cập nhật sau mỗi chu kỳ (Delivery Phase):** Khi kết thúc một task hoặc phiên làm việc, PM hoặc Lead BA cập nhật 4 thông tin cốt lõi:
      * Thời điểm cập nhật;
      * Trạng thái tính năng vừa hoàn thành và nhánh Git hiện tại;
      * Các hạng mục còn đang xử lý dở dang (In-progress/Blockers);
      * 2-3 hành động ưu tiên tiếp theo cần thực hiện khi mở lại dự án.
    - **Khôi phục ngữ cảnh tức thì (Session Resumption):** Khi người dùng mở phiên chat mới và nhắc đến dự án, Thư ký (`master-secretary`) hoặc PM ưu tiên đọc tệp `knowledge/checkpoint.md` để nắm bắt toàn bộ tiến độ trong 1 bước, loại bỏ hoàn toàn việc bắt người dùng phải giải thích lại lịch sử từ đầu.
11. **Quy Tắc Tự Động Dọn Dẹp Tập Tin Rác & Ảnh Chụp Màn Hình (Workspace Hygiene & Auto-Cleanup Protocol):**
    - **Cấm để lại file rác:** Toàn bộ các script tạm chạy 1 lần (`tmp_*.py`, `debug_*.py`, `qa_inspect*.py`, `scratch_*.py`) và các file ảnh chụp màn hình (`.png`, `.jpg`, `.webp`) do Playwright / E2E test sinh ra **BẮT BUỘC** phải được dọn dẹp sạch sẽ sau khi kiểm thử.
    - **Lưu trữ ảnh bằng chứng hợp lệ:** Nếu ảnh chụp màn hình cần giữ lại làm bằng chứng nghiệm thu cho User, Agent **BẮT BUỘC** lưu vào thư mục Artifacts của Antigravity (`brain/<conversation-id>/`) hoặc nhúng vào artifact report. TUYỆT ĐỐI KHÔNG để các tệp ảnh `.png` vương vãi trong thư mục mã nguồn dự án làm rác Git working tree.
    - **Chốt chặn kích hoạt tự động:** Trước khi báo cáo `[STATUS: DONE]`, `lead-qa` và `gitops-gatekeeper` **BẮT BUỘC** kích hoạt công cụ dọn rác:
      ```powershell
      uv run python "D:\Thành\Agent\common\scripts\hub_cleaner.py" "<duong_dan_repo_hoac_du_an>" --clean
      ```
12. **Git Là Nguồn Chân Lý Duy Nhất (Git-As-Single-Source-Of-Truth - SSoT):**
    - **Không lưu dữ liệu thừa trên máy:** Sau khi commit và push lên remote Git (`https://github.com/Dovernz/agent.git`), toàn bộ tiến độ, lịch sử và mã nguồn đã được bảo toàn vĩnh viễn trên đám mây Git.
    - **Đọc trực tiếp từ Git:** Mọi tác vụ tra cứu tiến độ (như `hub_status.py`, `master-secretary`) **BẮT BUỘC** đọc trực tiếp từ thư mục làm việc Git và nhật ký `git log -1`. Tuyệt đối không sinh thêm các file cache trạng thái hay file ghi nhớ ngoài luồng trên ổ cứng.
    - **Duy trì Working Tree sạch sẽ:** Khi hoàn tất công việc, thư mục làm việc của dự án phải sạch (`git status` clean), toàn bộ file rác/ảnh chụp màn hình được quét sạch qua `hub_cleaner.py`.
