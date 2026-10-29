---
name: pc-builder
description: >-
  Specialized PC hardware architect and build generator. Leverages the global
  'web-search-interactive' skill and MCP tools to search real-time component prices
  across Vietnamese retailers (GearVN, An Phat, HACOM, KCCShop, Nguyen Cong PC, MemoryZone),
  validate hardware compatibility, calculate wattage, and generate direct configuration links.
---

# Specialized PC Builder Skill

Kỹ năng chuyên biệt dành riêng cho việc tư vấn cấu hình, tối ưu hóa phần cứng theo ngân sách, kiểm tra tương thích kỹ thuật và so sánh giá linh kiện thời gian thực.

> [!NOTE]
> Kỹ năng này **kế thừa và sử dụng công cụ của Global Skill/MCP `web-search-interactive`** (`web_search`, `fetch_web_page`) để tương tác với web bán lẻ trong thời gian thực.

---

## 1. Quy Trình Xử Lý Yêu Cầu Build PC

### Bước 1: Phân tích Trọng số Phần cứng theo Tác vụ
1. **Data Science / Docker / Multi-Agent (AI chạy Cloud/API)**:
   - **Ưu tiên số 1: CPU nhiều nhân, nhiều luồng** (Tối thiểu 10C/16T như i5-13400F hoặc tối ưu 14C/20T như i5-13500) để phục vụ Docker và các agent chạy tiến trình song song.
   - **Ưu tiên số 2: RAM 32GB (Dual-Channel)**. Bắt buộc chọn Mainboard có **4 khe RAM** (ví dụ: B760M-P, B760M Pro RS) để sẵn sàng cắm thêm 2 thanh lên 64GB.
   - **Ưu tiên số 3: SSD NVMe PCIe Gen 4** (>5000MB/s) như Kingston NV3, WD Blue SN5000 để load dataset nhanh.
   - **Hạ GPU**: Do AI chạy Cloud/API, chỉ cần GPU phổ thông xuất hình mượt và giải trí nhẹ (GTX 1650 4GB, RX 6500 XT, Arc A380 6GB) để tiết kiệm 2–3 triệu dồn cho CPU và RAM.

### Bước 2: Kiểm tra Tương thích & Tính Công Suất Nguồn
1. Kiểm tra Socket CPU vs Bo mạch chủ:
   - Intel Gen 12/13/14 $\rightarrow$ `LGA1700` (H610, B760, Z790).
   - AMD Ryzen 7000/9000 $\rightarrow$ `AM5` (B650).
2. Kiểm tra chuẩn RAM:
   - Tránh nhầm lẫn giữa Mainboard DDR4 và DDR5.
3. Tính công suất nguồn (PSU) bằng script:
   - Chạy: `python ./scripts/calc_wattage.py --cpu 13500 --gpu "gtx 1650"`
   - Chọn nguồn đạt tối thiểu **80 Plus Bronze** từ các thương hiệu uy tín (MSI, DeepCool, Cooler Master).

### Bước 3: Sử dụng Global Web Tools để Tìm Giá Thời Gian Thực
Sử dụng công cụ `web_search` của Global MCP với cú pháp:
* `web_search("giá i5 13500 tray anphatpc gearvn kccshop")`
* `web_search("giá ram 32gb ddr4 2x16gb 3200 memoryzone")`
* `web_search("giá vga gtx 1650 4gb anphatpc")`

Khi cần xem thông số kỹ thuật chi tiết hoặc chương trình khuyến mãi của một đại lý cụ thể:
* Sử dụng `fetch_web_page(url="https://www.anphatpc.com.vn/...")` để lấy giá bán niêm yết mới nhất và kiểm tra tình trạng còn hàng.

### Bước 4: Tự Động Build Thử Cấu Hình Trên Web Bán Lẻ (Live Auto-Builder)
Khi người dùng yêu cầu vào trực tiếp các trang như HACOM hay Phong Vũ để build thử:
1. Chạy công cụ tự động hóa trình duyệt:
   ```bash
   uv run --with playwright python ./scripts/auto_builder_hacom.py --cpu "i5 13500" --ram "32GB 3200" --ssd "Kingston 1TB" --vga "GTX 1650" --psu "550W"
   ```
2. Script sẽ:
   - Tự động mở Google Chrome thật kết nối tới `https://hacom.vn/buildpc`.
   - Lần lượt bấm nút `Chọn` từng hạng mục, tìm kiếm mã linh kiện và bấm `Thêm` vào cấu hình.
   - Chụp ảnh màn hình lưu lại bảng cấu hình hoàn chỉnh với tổng chi phí thực tế.
3. Nếu người dùng muốn tận mắt nhìn thấy trình duyệt thao tác hoặc cần hỗ trợ thao tác thêm, truyền cờ `--headed`.

### Bước 5: Tạo Link Cấu Hình & Báo Cáo
1. Sử dụng helper script để sinh nhanh link trang Xây dựng cấu hình PC:
   - `python ./scripts/pc_builder_links.py i5 13500 gtx 1650 32gb`
2. Xuất bảng Báo giá Linh kiện (BOM) hoàn chỉnh gửi người dùng kèm ảnh chụp cấu hình thực tế.
