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
7. **Kiểm Soát Phân Tầng 3 Cấp & Cấm Đệ Quy Cấp 4 (Bounded 3-Tier Hierarchy & Anti-Nesting Policy):**
   - **Mô hình 3 tầng phân cấp chuẩn mực:**
     * **Tầng 1 (Executive):** Master Secretary & Project PMs điều phối toàn dự án.
     * **Tầng 2 (Tech Lead):** Nhóm Lead (`lead-backend`, `lead-frontend`, `lead-qa`, `lead-architect`, `lead-ba`, `lead-cyber-security`). Nhóm Lead **ĐƯỢC CẤP QUYỀN** sinh ra các Sub-agent Worker con dưới quyền (`EnableSubagentTools: true`) để phân rã công việc song song.
     * **Tầng 3 (Task Worker):** Các Sub-agent con do Lead sinh ra (`backend-worker`, `qa-worker`, `data-worker`...).
   - **Khóa cứng cấp Worker (Cấm đệ quy tầng 4):** Khi định nghĩa Worker cấp con bằng `define_subagent`, **BẮT BUỘC** thiết lập `EnableSubagentTools: false`. Cấp Worker tuyệt đối không được sinh thêm sub-agent nào khác để ngăn chặn phân nhánh đệ quy vô hạn làm cạn kiệt CPU, RAM và tài nguyên.
   - **Giới hạn số lượng Worker đồng thời:** Mỗi Lead Agent chỉ được phép duy trì tối đa $N \le 5$ Worker Sub-agents đồng thời tại một thời điểm.
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
    - **Khôi phục ngữ cảnh tức thì (Session Resumption):** Khi người dùng mở phiên chat mới và nhắc đến dự án, Master Agent (`master-agent`) hoặc PM ưu tiên đọc tệp `knowledge/checkpoint.md` để nắm bắt toàn bộ tiến độ trong 1 bước, loại bỏ hoàn toàn việc bắt người dùng phải giải thích lại lịch sử từ đầu.
11. **Quy Tắc Tự Động Dọn Dẹp Tập Tin Rác & Ảnh Chụp Màn Hình (Workspace Hygiene & Auto-Cleanup Protocol):**
    - **Cấm để lại file rác:** Toàn bộ các script tạm chạy 1 lần (`tmp_*.py`, `debug_*.py`, `qa_inspect*.py`, `scratch_*.py`) và các file ảnh chụp màn hình (`.png`, `.jpg`, `.webp`) do Playwright / E2E test sinh ra **BẮT BUỘC** phải được dọn dẹp sạch sẽ sau khi kiểm thử.
    - **Lưu trữ ảnh bằng chứng hợp lệ:** Nếu ảnh chụp màn hình cần giữ lại làm bằng chứng nghiệm thu cho User, Agent **BẮT BUỘC** lưu vào thư mục Artifacts của Antigravity (`brain/<conversation-id>/`) hoặc nhúng vào artifact report. TUYỆT ĐỐI KHÔNG để các tệp ảnh `.png` vương vãi trong thư mục mã nguồn dự án làm rác Git working tree.
    - **Chốt chặn kích hoạt tự động:** Trước khi báo cáo `[STATUS: DONE]`, `lead-qa` và `gitops-gatekeeper` **BẮT BUỘC** kích hoạt công cụ dọn rác:
      ```powershell
      uv run python "D:\Thành\Agent\common\scripts\hub_cleaner.py" "<duong_dan_repo_hoac_du_an>" --clean
      ```
12. **Git Là Nguồn Chân Lý Duy Nhất (Git-As-Single-Source-Of-Truth - SSoT):**
    - **Không lưu dữ liệu thừa trên máy:** Sau khi commit và push lên remote Git (`https://github.com/Dovernz/agent.git`), toàn bộ tiến độ, lịch sử và mã nguồn đã được bảo toàn vĩnh viễn trên đám mây Git.
    - **Đọc trực tiếp từ Git:** Mọi tác vụ tra cứu tiến độ (như `hub_status.py`, `master-agent`) **BẮT BUỘC** đọc trực tiếp từ thư mục làm việc Git và nhật ký `git log -1`. Tuyệt đối không sinh thêm các file cache trạng thái hay file ghi nhớ ngoài luồng trên ổ cứng.
    - **Duy trì Working Tree sạch sẽ:** Khi hoàn tất công việc, thư mục làm việc của dự án phải sạch (`git status` clean), toàn bộ file rác/ảnh chụp màn hình được quét sạch qua `hub_cleaner.py`.
13. **Truy Vấn Tức Thì Gemini Key Pool (Instant Pool Status Trigger):**
    - Khi người dùng hỏi bất kỳ biến thể nào như: `pool status`, `trạng thái pool`, `kiểm tra pool`, `xem pool`, `gemini pool`, `quota api`, `hub usage`:
    - Agent **BẮT BUỘC** tự động chạy lệnh mà không bắt người dùng phải gõ terminal:
      ```powershell
      hub usage
      ```
    - Hiển thị ngay lập tức bảng trạng thái Markdown gồm các cột STT, Mã Khóa, Trạng Thái (SẴN SÀNG / COOLDOWN), và Tổng Hạn Mức Toàn Hệ Thống.
14. **Quy Trình Kiểm Định & Hội Đồng Thẩm Định Output (Output Verification & Multi-Tier Review Gate):**
    - **Không tin tưởng mù quáng:** Tuyệt đối không tin tưởng ngay vào kết quả sinh thô từ API ngoài hoặc mã nguồn do Sub-agent tạo ra.
    - **Cổng thẩm định tự động (Automated Verification Gate):** Bất kỳ tệp mã nguồn (`.py`, `.sql`) hoặc dữ liệu (`.json`, `.md`) nào trước khi đưa vào codebase BẮT BUỘC phải vượt qua cổng kiểm định:
      ```powershell
      uv run python "D:\Thành\Agent\common\scripts\output_verifier.py" "<duong_dan_tep>"
      ```
    - **Hội đồng Thẩm định & Đánh giá chuyên trách:**
      * `lead-qa`: Chạy ma trận kiểm thử E2E/Unit test, bắt lỗi HTTP 500, đảm bảo tính đúng đắn logic.
      * `lead-cyber-security`: Thẩm định an ninh, rà soát lệnh nguy hiểm (`eval`, `exec`, `os.system`), ngăn chặn SQL Injection và hardcoded secret.
      * `lead-ba`: Đối chiếu kết quả với User Story và Tiêu chí chấp nhận (Acceptance Criteria) ban đầu.
    - **Cơ chế Tự sửa lỗi (Self-Correction Loop):** Nếu cổng thẩm định báo `[VERIFIED: FAIL]`, Sub-agent tự động gửi lại log lỗi để API sửa (tối đa 2 lần). Nếu vẫn không đạt, kích hoạt Antigravity Agent can thiệp bằng logic cấp cao để hoàn thiện trước khi báo cáo User.
15. **Quy Trình Phân Nhánh Động Của Nhóm Lead & Phối Hợp API Worker (Dynamic Lead Fan-Out & API Worker Protocol):**
    - **Đánh giá Khối lượng & Độ phức tạp (Lead Assessment):**
      Khi Lead nhận một Feature hoặc User Story lớn từ PM, Lead tiến hành bóc tách:
      * Nếu task nhỏ ($\le 3$ files hoặc công việc tuần tự): Lead tự xử lý hoặc chỉ gọi 1 Worker.
      * Nếu task lớn, có các luồng độc lập: Lead xác định số lượng $N$ Worker con cần thiết ($2 \le N \le 5$). Có thể dùng công cụ tính toán:
        ```powershell
        uv run python "D:\Thành\Agent\common\scripts\task_fanout_planner.py" --role <backend|frontend|qa|ba|architect|cyber> --scope "<mo_ta>" --files <so_file>
        ```
    - **Phân bổ Worker Chuyên biệt theo Luồng công việc:**
      * *Ví dụ Lead Backend:* Worker 1 (Data Models & Migration), Worker 2 (API ViewSets & Serializers), Worker 3 (DB Seeder & Mock data).
      * *Ví dụ Lead Frontend:* Worker 1 (Routing & Layout), Worker 2 (Components & UI), Worker 3 (API Client Integration).
      * *Ví dụ Lead QA:* Worker 1 (Unit Test Suite), Worker 2 (Integration/E2E Test Suite).
    - **Worker Tương Tác Trực Tiếp Với API Pool (`hub gemini`):**
      * Các Worker con được giao task chi tiết và chủ động gọi `hub gemini` (`common/scripts/gemini_offloader.py`) để cày token nặng (sinh code hàng trăm dòng, phân tích dữ liệu lớn).
      * Cơ chế Smart Key Pool (7 Projects) tự động phân bổ round-robin các cuộc gọi API từ nhiều Worker song song, không bị nghẽn rate-limit.
    - **Tự Động Kiểm Định Cú Pháp Tại Cấp Worker:**
      * Mỗi Worker sau khi nhận output từ API **BẮT BUỘC** chạy `hub verify <file>` (`common/scripts/output_verifier.py`). Nếu đạt 100/100 mới nộp bài về cho Lead.
    - **Hội Đồng Lead Thẩm Định Hợp Nhất & Báo Cáo:**
      * Lead thu thập kết quả từ $N$ Worker, kiểm tra tính tương thích giữa các module, chạy `test_matrix_runner.py` / `linter_guard.py` toàn cục.
      * Khi tất cả pass, Lead đóng gói payload M2M báo cáo lên PM / Master Secretary:
        `[STATUS: DONE] {"lead": "<ROLE>", "workers_count": N, "artifacts": [...]}`.
16. **Quy Tắc Ép Buộc Ủy Thác API Lên Mức Tối Đa (Maximal API Offloading & Zero In-Chat Coding):**
    - **CẤM TUYỆT ĐỐI việc tự sinh code trong ngữ cảnh chat Antigravity:** Mọi Agent/Sub-agent tuyệt đối không được dùng lệnh `write_file` hoặc in trực tiếp các đoạn code dài (> 30 dòng), serializers, viewsets, models, mock data lớn, regex, DDL, hoặc kịch bản test vào ngữ cảnh chat Antigravity (gây lãng phí nghiêm trọng token quota).
    - **100% Mã Nguồn, Dữ Liệu & Test BẮT BUỘC Ủy thác cho Gemini API Pool:**
      * Khi cần viết mã nguồn hoặc kịch bản kiểm thử:
        ```powershell
        hub gemini --prompt "<yêu_cầu_chi_tiết>" --out "<đường_dẫn_tệp>" --tier <auto|bulk|standard|deep|ultra>
        ```
      * Khi cần sinh hàng loạt files (ví dụ 3 serializers + 2 tests): BẮT BUỘC chạy đa luồng qua batch:
        ```powershell
        hub gemini --batch <tasks.json>
        ```
      * File mã nguồn sẽ được Gemini API sinh và ghi thẳng vào ổ cứng đĩa.
      * Cổng kiểm định `output_verifier` và `self-healing loop` tự động kiểm tra cú pháp và vá lỗi ngay tại chỗ.
    - **Phân định rõ ranh giới Brain vs Muscle:**
      * **Antigravity Agents (Brain):** Chỉ giữ vai trò Lập kế hoạch kiến trúc (Planning), Ra lệnh cho API (Prompting), Chạy test/lint (Execution), và Đánh giá nghiệm thu (Reviewing).
      * **Gemini API Pool (Muscle):** Đảm nhận 100% công việc cày xới mã nguồn thô và token nặng hoàn toàn miễn phí (0 VNĐ, 7 Cloud Projects).
17. **Quy Tắc Kích Hoạt Hệ Thống Toàn Quyền (`/master-agent`, `/agent-system` & "sử dụng hệ thống agent"):**
    - **Tín Hiệu Kích Hoạt:** Bất kỳ khi nào người dùng gõ lệnh `/master-agent`, `/agent-system` hoặc nói *"sử dụng hệ thống agent"*:
      * Antigravity **BẮT BUỘC** chuyển sang chế độ Master Agent (Tổng chỉ huy hệ thống Agent).
      * Phân tích ngay bài toán thuộc về dự án nào trong hệ thống (`dental-project`, `vietjet-airflow`, `vietjet-ancillary`, `pc-builder`, `vietjet-brd`, `agent-supervisor`, hoặc dự án mới kế thừa `lead-pm`).
      * Định tuyến và giao việc xuống đúng Project PM / Lead thông qua M2M Protocol.
      * **TUÂN THỦ TUYỆT ĐỐI QUY TẮC 16:** Nghiêm cấm Antigravity tự hì hục sinh code dài trong ngữ cảnh chat gây hao tổn token. BẮT BUỘC ủy thác 100% công việc sinh code, refactor, viết test, bóc tách dữ liệu cho Gemini API Pool ngoài thông qua `hub gemini` hoặc `hub gemini --batch`.
      * Tự động chạy `hub verify` và `hub smoke` / `hub test` trong Docker container trước khi báo cáo kết quả súc tích cho người dùng.
18. **Quy Tắc Phân Mảnh Ngữ Cảnh & Cô Lập Subagent (Dynamic Context Sharding & Subagent Isolation):**
    - **Nghiêm cấm Monolithic Context:** Không nạp đồng thời toàn bộ 23-24 skills của cả 7 dự án vào System Prompt. Bắt buộc phân mảnh `skills.json` theo đúng phạm vi dự án bằng `hub shard set <tên_shard>` hoặc `hub shard auto "<yêu_cầu>"` (giảm tới 90% token System Prompt).
    - **Cô Lập Ngữ Cảnh Tuyệt Đối (Subagent Context Isolation):** Khi xử lý tác vụ dự án, Master Agent KHÔNG đọc tài liệu chi tiết hoặc mã nguồn vào Main Chat. Master Agent ủy thác qua `invoke_subagent`, truyền đường dẫn `SKILL.md` cho Subagent tự đọc và thực thi độc lập, chỉ trả về JSON tóm tắt 100 token cho Main Chat. Main Chat luôn được giữ ở trạng thái Zero-Fat.
