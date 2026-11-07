## ⚡ 3. Giao Thức Giao Việc Chuẩn Hóa M2M JSON (Code Dispatch)

Master Agent gửi gói giao việc M2M cho Project PM hoặc Tech Lead:
```json
{
  "sender": "master-agent",
  "dispatch_to": "<TÊN_PM_DỰ_ÁN>",
  "action": "EXECUTE_TASK",
  "task_id": "TASK-<TIMESTAMP>",
  "user_request": "<Yêu cầu nguyên bản của người dùng>",
  "constraints": {
    "model": "inherit",
    "docker_first": true,
    "allow_subagent_recursion": true,
    "max_subagents": 5,
    "code_via_api": true,
    "isolated_execution": true
  }
}
```

Nhận kết quả M2M JSON từ cấp dưới:
```json
{
  "sender": "<TÊN_PM_DỰ_ÁN>",
  "task_id": "TASK-<TIMESTAMP>",
  "status": "DONE | FAIL | ESCALATE",
  "summary": "<Tóm tắt kỹ thuật 1-2 câu>",
  "artifacts": ["<Đường dẫn file mã nguồn đã sinh qua API>"],
  "verified_score": 100,
  "tokens_saved": "<Số token tiết kiệm>"
}
```

---

## ⏱️ 4. Quy Trình Vận Hành 4 Bước (Zero-Execution & Zero-Polling)

```mermaid
flowchart TD
    User["Người dùng gửi prompt / gõ /master-agent"] --> Master["Master Agent<br/>(Chỉ giao tiếp tự nhiên với User)"]
    Master -->|1. Khớp Routing Matrix| Shard["hub shard auto (Chỉ nạp đúng context dự án)"]
    Shard -->|2. invoke_subagent| PM["Project PM / Lead Agent<br/>(Chạy hoàn toàn trong Subagent Context)"]
    
    Master -.->|3. DỪNG LẠI - KHÔNG POLLING / KHÔNG SCHEDULE<br/>Chờ Reactive Wakeup| Wait((Sleep))
    
    subgraph SubagentExecution ["Thực thi kỹ thuật cô lập 100% ngoài Main Chat"]
        PM --> Leads["Tech Leads & Workers"]
        Leads --> API["hub gemini / hub gemini --batch<br/>(Offload 100% code qua API 0 VNĐ)"]
        API --> Verify["hub verify (Quality Gate 100/100)"]
        Verify --> Docker["Kiểm thử Docker / hub smoke"]
    end
    
    Docker -->|4. M2M JSON Báo Cáo ~100 tok| Master
    Master -->|5. Tổng hợp ngắn gọn| ReportUser["Báo cáo 2-3 câu súc tích kèm Clickable Links"]
    Master -->|6. Reset Shard| ResetCore["hub shard reset"]
```

---

## 📤 5. Báo Cáo Kết Quả Cho User (Bằng Ngôn Ngữ Tự Nhiên)

Master Agent sau khi nhận M2M JSON sẽ phản hồi ngắn gọn cho User:
> "Đã thực thi thành công yêu cầu cho dự án **[Tên Dự Án]** qua Hệ Thống Agent:
> - Các file đã hoàn thành: [file_link](file:///...) (Quality Gate 100/100).
> - Hạ tầng Docker: 100% Endpoints sẵn sàng (`hub smoke`).
> - Tiết kiệm: ~X tokens bằng cách offload qua Gemini API Key Pool ngoài."
