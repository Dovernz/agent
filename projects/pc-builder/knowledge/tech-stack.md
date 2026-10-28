# PC Hardware Knowledge & Workload Sizing

## 1. Trọng Số Linh Kiện Theo Tác Vụ

### A. Data Analyst / Data Science & Docker Multi-Agent (AI chạy Cloud/API)
- **CPU**: Ưu tiên cao nhất. Tối thiểu 10C/16T (i5-13400F) hoặc tối ưu 14C/20T (i5-13500, i5-14500). Docker và Multi-Agent spawn nhiều worker đồng thời.
- **RAM**: Tối thiểu 32GB (2x16GB) Bus 3200MHz DDR4 hoặc 5600MHz DDR5. Bắt buộc bo mạch chủ có 4 khe RAM để nâng cấp lên 64GB.
- **SSD**: Chuẩn NVMe PCIe Gen 4x4 (Kingston NV3, WD Blue SN5000, tốc độ đọc >5000MB/s).
- **GPU**: Hạ cấu hình xuống GTX 1650 4GB hoặc Radeon RX 6500 XT 4GB để dồn ngân sách cho CPU & RAM.

### B. Local Deep Learning / LLM
- **GPU**: Yếu tố cốt lõi. Tối thiểu 12GB - 16GB VRAM (RTX 3060 12GB, RTX 4060 Ti 16GB, RTX 4070 Ti Super).
- **RAM**: 32GB - 64GB DDR5.
- **Nguồn**: 650W - 850W Gold.

### C. Gaming Phổ Thông & AAA
- **CPU**: 6C/12T (i5-12400F, Ryzen 5 5600, Ryzen 5 7600).
- **GPU**: RTX 4060 8GB / RX 6600 8GB trở lên.
