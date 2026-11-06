---
name: agent-system
description: >-
  Kích hoạt Master Agent & Trung tâm điều hành Multi-Agent & Gemini API Pool. Sử dụng khi người dùng gõ /agent-system, nói 'sử dụng hệ thống agent', hoặc yêu cầu giải quyết bài toán cần điều phối qua Master Agent, các PM dự án và bắt buộc offload code ra API ngoài để tiết kiệm token.
---
# Hệ Thống Điều Hành Multi-Agent & API Key Pool (`agent-system`)

[COMMAND]: `/agent-system` | [TRIGGER]: "sử dụng hệ thống agent" | [ROUTER]: Trực tiếp gọi Master Agent (`master-agent`) | [REF]: `D:\Thành\Agent\rules\m2m-protocol.md`

---

## ⚡ CHỈ THỊ CỐT LÕI: GỌI TRỰC TIẾP MASTER AGENT

Khi nhận được lệnh `/agent-system` hoặc khẩu lệnh **"sử dụng hệ thống agent"**:
1. **Trực tiếp gọi `master-agent` (`D:\Thành\Agent\common\skills\master-agent/SKILL.md`):**
   - `master-agent` là đầu não duy nhất được dùng ngôn ngữ tự nhiên để trò chuyện, tiếp nhận và trả kết quả cho User.
   - Toàn bộ các PM dự án, Tech Leads và Workers cấp dưới **bắt buộc 100% giao tiếp bằng M2M JSON Code Protocol**.
2. **Toàn Bộ Hệ Thống Agent Lưu Tại `D:\Thành\Agent`:**
   - Không đọc hoặc định nghĩa agent ở bất kỳ folder nhỏ lẻ nào khác.
3. **CẤM TỰ SINH CODE DÀI TRONG NGỮ CẢNH CHAT (Rule 16):**
   - Tuyệt đối không dùng `write_file` hoặc in code dài hàng chục dòng vào chat gây phình to ngữ cảnh (hụt ngân sách token).
   - Bắt buộc offload cho Gemini API Key Pool ngoài: `hub gemini` hoặc `hub gemini --batch` ra đĩa và thẩm định qua `hub verify`.

---

## 🧭 QUY TRÌNH 4 BƯỚC THỰC THI CHUẨN MỰC

```
[User: /agent-system hoặc "sử dụng hệ thống agent"]
               │
               ▼
[Bước 1: Phân tích & Định tuyến Dự án]
               │
               ├─► Nha Khoa Minh Sinh  ──► dental-pm-orchestrator (Django/React/Docker)
               ├─► Vietjet Airflow     ──► vj-pm-orchestrator (Airflow 2.10/Postgres)
               ├─► Vietjet Ancillary   ──► vietjet-pm-orchestrator (Databricks Medallion)
               ├─► PC Builder          ──► pc-builder (Phần cứng & Giá VN)
               ├─► Vietjet BRD         ──► vietjet-brd-architect (Word BRD)
               └─► Dự án khác / Chung  ──► lead-pm (Universal PM Base)
               │
               ▼
[Bước 2: Phân Rã Việc Xuống Tech Leads (M2M Protocol)]
(lead-ba, lead-architect, lead-backend, lead-frontend, lead-qa, lead-cyber-security)
               │
               ▼
[Bước 3: Worker Sinh Code Qua API Pool Ngoài (hub gemini)]
(Bắn API qua 7 keys pool song song 0đ -> Ghi đĩa -> hub verify đạt 100/100)
               │
               ▼
[Bước 4: Nghiệm Thu Docker & Báo Cáo Súc Tích (Zero-Fat)]
(Chạy test trong Docker -> hub smoke -> Báo cáo 1-2 câu kèm link file)
```

---

## 📋 MA TRẬN PHÂN LOẠI MODEL TIERS KHI GỌI API

Khi gọi `hub gemini`, hệ thống tự động điều phối theo ma trận:
- **`bulk` (`gemini-3.5-flash-lite`, 1.05s | 3.5k req/ngày):** Tóm tắt tài liệu lớn, sinh mock data, đọc log dài, format văn bản.
- **`standard` (`gemini-3.6-flash`, 1.79s | 140 req/ngày):** Viết API serializers, viewsets, React components, unit tests, scripts.
- **`deep` (`gemini-3.8-flash` / fallback `3.6`, 140 req/ngày):** Thiết kế kiến trúc sâu, tối ưu câu lệnh SQL phức tạp, audit RBAC.
- **`ultra` (`gemma-4-26b-a4b-it`, 2.86s | 100.8k req/ngày):** Regex bóc tách chuỗi, mapping dữ liệu danh mục hàng vạn dòng.

---

## 📤 MẪU PHẢN HỒI KẾT QUẢ CHO USER (ZERO-FAT)

Sau khi hoàn thành qua API và Quality Gate, phản hồi ngắn gọn:
```markdown
[STATUS: DONE] Đã tiếp nhận và thực thi qua Hệ Thống Agent (Dự án: <Tên Dự Án>).
- Mã nguồn đã sinh & lưu tại: [<file_path>](file:///<file_path>) (Quality Gate: 100/100).
- Kiểm tra dịch vụ: 100% Docker Endpoints sẵn sàng (`hub smoke`).
- Quota bảo toàn: Tiết kiệm ~<N> tokens ngữ cảnh bằng cách ủy thác cho Gemini API Key Pool.
```
