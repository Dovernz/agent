# Dự Án Tư Vấn & Thiết Kế Cấu Hình PC (`pc-builder`)

Nhóm Agent chuyên gia phần cứng, phân tích tương thích linh kiện và so sánh giá thời gian thực từ các nhà bán lẻ công nghệ hàng đầu tại Việt Nam.

---

## 1. Mục Tiêu & Phạm Vi
- **Tư vấn cấu hình tối ưu theo ngân sách & tác vụ**: Data Science, Machine Learning, Docker Containers, Multi-Agent AI System, Gaming, Đồ họa 3D.
- **Tương thích kỹ thuật**: Socket CPU, chuẩn RAM DDR4/DDR5, khe cắm mở rộng, công suất nguồn PSU (80 Plus).
- **So sánh giá thời gian thực**: Sử dụng `common/skills/web-search-interactive` để quét giá tại GearVN, An Phát, HACOM, KCCShop, Nguyễn Công PC, MemoryZone.

---

## 2. Cấu Trúc Thư Mục
```text
projects/pc-builder/
├── README.md
├── knowledge/
│   ├── tech-stack.md                  # Quy định linh kiện & hướng dẫn phân bổ
│   ├── hardware-compatibility.md      # Ma trận tương thích CPU/Mainboard/PSU
│   └── vietnam-retailers.md           # Danh mục website và công cụ build PC
├── rules/
│   └── pc-rules.md                    # Nguyên tắc thiết kế phần cứng không nghẽn cổ chai
└── skills/
    └── pc-builder/
        ├── SKILL.md                   # Skill chính của PC Builder
        └── scripts/
            ├── calc_wattage.py        # Script tính công suất nguồn
            └── pc_builder_links.py    # Script sinh link cấu hình trực tiếp
```
