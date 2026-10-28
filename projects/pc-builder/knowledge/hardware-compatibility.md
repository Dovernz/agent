# Bảng Tra Cứu Tương Thích Phần Cứng (Hardware Compatibility Matrix)

## 1. Sockets & Chipsets

### Intel Platforms
| Thế Hệ | Tên Vi Xử Lý Tiêu Biểu | Socket | Chipset Bo Mạch Chủ Khuyên Dùng | Chuẩn RAM Hỗ Trợ |
| :--- | :--- | :--- | :--- | :--- |
| **Gen 12 (Alder Lake)** | i3-12100F, i5-12400F, i5-12600K | `LGA1700` | H610, B660, B760, Z690, Z790 | DDR4 hoặc DDR5 (Tùy phiên bản bo mạch chủ) |
| **Gen 13 (Raptor Lake)** | i5-13400F, i5-13500, i7-13700K | `LGA1700` | B760, Z790 (H610 cần cập nhật BIOS) | DDR4 hoặc DDR5 (Tùy phiên bản bo mạch chủ) |
| **Gen 14 (Raptor Lake Refresh)** | i5-14400F, i5-14500, i7-14700K | `LGA1700` | B760, Z790 | DDR4 hoặc DDR5 (Tùy phiên bản bo mạch chủ) |
| **Core Ultra 200 (Arrow Lake)** | Ultra 5 245K, Ultra 7 265K | `LGA1851` | Z890, B860 | Chỉ hỗ trợ DDR5 |

### AMD Platforms
| Thế Hệ | Tên Vi Xử Lý Tiêu Biểu | Socket | Chipset Bo Mạch Chủ Khuyên Dùng | Chuẩn RAM Hỗ Trợ |
| :--- | :--- | :--- | :--- | :--- |
| **Ryzen 5000 Series** | Ryzen 5 5600, Ryzen 7 5700X | `AM4` | A520, B550, X570 | Chỉ hỗ trợ DDR4 |
| **Ryzen 7000 / 9000 Series** | Ryzen 5 7600, Ryzen 7 7700, Ryzen 7 9700X | `AM5` | A620, B650, X670, B850, X870 | Chỉ hỗ trợ DDR5 |

---

## 2. Công Thức Tính Công Suất Nguồn (PSU)

Nguồn máy tính là linh kiện quan trọng nhất bảo vệ toàn bộ linh kiện khác. Không được chọn nguồn thiếu hụt hoặc nguồn không rõ nguồn gốc.

$$P_{\text{tổng}} = (TDP_{\text{CPU}} + TDP_{\text{GPU}} + 100\text{W [Mainboard + RAM + SSD + Quạt]}) \times 1.25$$

| Cấu Hình CPU + GPU | Mức tiêu thụ tối đa (Full load) | Khuyến nghị công suất nguồn tối thiểu | Chuẩn chất lượng |
| :--- | :--- | :--- | :--- |
| i5-13400F + GTX 1650 / Arc A380 | ~200W - 250W | **450W - 550W** | 80 Plus Bronze |
| i5-13500 + GTX 1650 / RX 6500 XT | ~260W - 300W | **550W - 650W** | 80 Plus Bronze |
| i5-13500 + RTX 3050 6GB/8GB | ~280W - 330W | **550W - 650W** | 80 Plus Bronze |
| i5-13500 / 14600K + RTX 4060 / 4060 Ti | ~350W - 420W | **650W - 750W** | 80 Plus Bronze / Gold |
