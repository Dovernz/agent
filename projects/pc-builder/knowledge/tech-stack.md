# Dynamic PC Hardware Sizing & Budget Allocation Matrix

Tài liệu hướng dẫn phân bổ tỷ trọng phần cứng một cách linh hoạt, không cố định cấu hình hay phân khúc giá.

---

## 1. Các Phân Khúc Ngân Sách Phổ Biến

| Phân Khúc | Mức Giá Tham Khảo | Định Hướng Cốt Lõi |
| :--- | :--- | :--- |
| **Tiết kiệm / Học sinh - Sinh viên** | 8 – 12 triệu VNĐ | Tối ưu chi phí, dùng CPU tích hợp đồ họa (i3, Ryzen 5 5600G) hoặc card xuất hình cơ bản (GTX 1650 cũ/mới). 16GB RAM, 500GB SSD. |
| **Phổ thông / Gaming eSports** | 13 – 18 triệu VNĐ | CPU 6C/12T (i5-12400F, Ryzen 5 5600) + VGA RTX 3050 / RX 6600. Đủ chiến mượt LOL, Valorant, CS2, FO4 ở độ phân giải Full HD. |
| **Tầm trung / Data Science & Dev** | 18 – 28 triệu VNĐ | CPU nhiều nhân/luồng (i5-13500, i5-14600K, Ryzen 7 7700), 32GB–64GB RAM, 1TB Gen 4 SSD, nguồn 650W. Card đồ họa tùy thuộc vào việc có train model cục bộ hay chạy cloud. |
| **Cao cấp / AAA 2K & Đồ họa 3D** | 30 – 45 triệu VNĐ | CPU i7 / Ryzen 7 + VGA RTX 4070 Super / RX 7800 XT, RAM DDR5 32GB bus cao, tản nhiệt nước AIO 240/360mm. |
| **High-End / Workstation & Local LLM** | > 50 triệu VNĐ | CPU i9 / Ryzen 9 / Threadripper + VGA RTX 4080 Super / RTX 4090 (24GB VRAM để chạy model AI 70B Quantized hoặc 32B FP16). |

---

## 2. Ma Trận Phân Bổ Tỷ Trọng Ngân Sách Theo Nhu Cầu

Khi người dùng cung cấp mức ngân sách tổng ($B$), phân bổ linh kiện theo tỷ lệ:

### A. Gaming AAA / Đồ Họa Nặng
- **VGA (Card đồ họa)**: 45% – 55% ngân sách (ưu tiên số 1, quyết định trực tiếp FPS).
- **CPU**: 20% – 25% ngân sách (đủ mạnh để không nghẽn VGA).
- **RAM**: 10% – 12% (16GB – 32GB).
- **SSD + Mainboard + Nguồn + Vỏ**: 20% – 25%.

### B. Data Analyst / Data Science / Docker Containers (AI chạy Cloud/API)
- **CPU**: 35% – 45% ngân sách (ưu tiên nhiều nhân/luồng thực sự để gánh container).
- **RAM**: 20% – 25% ngân sách (tối thiểu 32GB, bắt buộc mainboard 4 khe để nâng cấp 64GB).
- **SSD**: 12% – 15% (NVMe Gen 4 đọc dữ liệu lớn >5000MB/s).
- **VGA**: 10% – 15% (hạ xuống card phổ thông xuất hình mượt hoặc eSports nhẹ).
- **Nguồn + Vỏ + Tản**: 12% – 15%.

### C. Local Deep Learning / Offline LLM / Stable Diffusion
- **VGA**: 55% – 65% ngân sách (bắt buộc NVIDIA có VRAM từ 12GB trở lên).
- **CPU**: 15% – 20% ngân sách.
- **RAM**: 15% – 20% (32GB – 64GB).
- **Lưu trữ + Nguồn + Vỏ**: 15% – 20% (nguồn tối thiểu 750W–850W Gold).

### D. Văn Phòng / Kế Toán / Học Tập Cơ Bản
- **CPU**: 40% – 50% ngân sách (chọn mã có đồ họa tích hợp iGPU: i3-12100, i5-12400).
- **VGA**: 0% (không lắp card rời).
- **RAM**: 15% – 20% (16GB Dual-Channel).
- **SSD + Mainboard + Nguồn + Vỏ**: 35% – 40%.
