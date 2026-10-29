# Dự Án Tư Vấn & Thiết Kế Cấu Hình PC Thích Ứng (`pc-builder`)

Nhóm Agent chuyên gia phần cứng thích ứng theo nhu cầu cá nhân hóa của người dùng, phân tích tương thích kỹ thuật, so sánh giá thời gian thực và tự động hóa build thử trên web bán lẻ.

---

## 1. Mục Tiêu & Phạm Vi (Nguyên Tắc Thích Ứng Động)

* **Hoàn toàn theo nhu cầu người dùng (Zero-Assumptions)**:
  - **Không cố định ngân sách**: Hỗ trợ từ phân khúc học sinh/sinh viên tiết kiệm (8–12 triệu) đến tầm trung (15–25 triệu), đồ họa chuyên nghiệp (30–50 triệu) hay High-End Gaming / Deep Learning (>60 triệu).
  - **Không cố định tác vụ**: Phân tích tỷ trọng linh kiện linh hoạt cho mọi nhu cầu: Gaming (Esports / AAA 2K–4K), Lập trình & Docker, Data Science, Render 3D / Edit Video, Local AI / Offline LLM, hoặc Văn phòng phổ thông.
  - **Chốt chặn khảo sát (Intake Gate)**: Nếu người dùng chưa nêu rõ ngân sách hoặc tác vụ, Agent **bắt buộc hỏi lại để làm rõ** trước khi search hoặc build; chỉ áp dụng cấu hình mặc định khi người dùng yêu cầu *"lấy mặc định"* hoặc *"tùy bạn chọn"*.
* **Tương thích kỹ thuật nghiêm ngặt**: Socket CPU (LGA1700, AM5), chuẩn RAM (DDR4 vs DDR5), số khe nâng cấp (4 khe), công thức tính công suất nguồn an toàn (chuẩn tối thiểu 80 Plus Bronze).
* **So sánh giá thời gian thực**: Sử dụng `common/skills/web-search-interactive` để quét giá tại GearVN, An Phát, HACOM, KCCShop, Nguyễn Công PC, MemoryZone.
* **Tự động build thử trên web (Live Auto-Builder)**: Điều khiển Google Chrome tự động chọn linh kiện trên các trang build PC trực tuyến (như HACOM, Phong Vũ) và chụp ảnh bảng báo giá thực tế.

---

## 2. Cấu Trúc Thư Mục
```text
projects/pc-builder/
├── README.md                          # Tài liệu dự án
├── knowledge/
│   ├── tech-stack.md                  # Ma trận phân bổ tỷ trọng ngân sách động
│   ├── hardware-compatibility.md      # Ma trận tương thích CPU/Mainboard/PSU
│   └── vietnam-retailers.md           # Danh mục website và công cụ build PC
├── rules/
│   └── pc-rules.md                    # Quy tắc intake gate & chống nghẽn cổ chai
└── skills/
    └── pc-builder/
        ├── SKILL.md                   # Kịch bản khảo sát & build PC thích ứng
        └── scripts/
            ├── calc_wattage.py        # Script tính công suất nguồn
            ├── pc_builder_links.py    # Script sinh link cấu hình trực tiếp
            └── auto_builder_hacom.py  # Script tự động build thử trên web bán lẻ
```
