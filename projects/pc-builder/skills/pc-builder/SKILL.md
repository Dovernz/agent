---
name: pc-builder
description: >-
  Adaptive PC hardware architect and live configuration generator. Dynamically collects
  user budget and workload requirements, verifies hardware compatibility, compares
  real-time prices across Vietnamese retailers (GearVN, An Phat, HACOM, KCCShop,
  Nguyen Cong PC, MemoryZone), and automates web building. NEVER assumes fixed budgets
  or static workloads without user confirmation.
---

# Adaptive PC Builder & Hardware Architect Skill

Kỹ năng chuyên gia tư vấn phần cứng máy tính **hoàn toàn thích ứng theo nhu cầu người dùng**. Kỹ năng này không áp đặt bất kỳ ngân sách hay tác vụ cố định nào; mọi cấu hình đều được thiết kế cá nhân hóa dựa trên khảo sát thực tế hoặc câu hỏi làm rõ.

> [!IMPORTANT]
> **NGUYÊN TẮC CỐT LÕI (Core Rules):**
> 1. **KHÔNG CỐ ĐỊNH NGÂN SÁCH & TÁC VỤ**: Không tự ý gán người dùng vào ngân sách 15tr, 20tr hay CPU/GPU cụ thể nếu người dùng chưa nói rõ.
> 2. **GATE KHẢO SÁT & HỎI LẠI TRƯỚC KHI BUILD**: Nếu người dùng chưa cung cấp đủ ngân sách hoặc mục đích sử dụng, Agent **BẮT BUỘC HỎI LÀM RÕ** trước khi search hoặc build thử trên web.
> 3. **CHẾ ĐỘ MẶC ĐỊNH (Baseline Fallback)**: Chỉ sử dụng cấu hình mẫu khi người dùng nói rõ: *"tùy bạn chọn"*, *"build theo mặc định"*, hoặc *"lấy cấu hình tối ưu tầm trung"*.

---

## 1. Quy Trình Khảo Sát Nhu Cầu Người Dùng (Requirement Intake Gate)

Khi nhận được yêu cầu build PC, Agent kiểm tra 4 thông số:

| Tiêu Chí | Câu Hỏi Cần Làm Rõ | Ví Dụ Các Lựa Chọn |
| :--- | :--- | :--- |
| **1. Ngân sách (Budget)** | *"Bạn dự tính đầu tư khoảng bao nhiêu triệu?"* | 8–12tr (tiết kiệm), 15–20tr (tầm trung), 25–40tr (cao cấp), >50tr (hi-end). |
| **2. Nhu cầu chính (Workload)** | *"Máy dùng cho tác vụ nào là chủ yếu?"* | • Gaming (Esports / AAA 2K-4K)<br>• Data Science / Docker / Multi-Agent AI (Cloud/API)<br>• Local Deep Learning / LLM (chạy AI offline trên card)<br>• Đồ họa 2D / 3D / Render / Edit Video<br>• Văn phòng / Lập trình cơ bản |
| **3. Phạm vi mua sắm (Scope)** | *"Ngân sách trên chỉ cho thùng case hay bao gồm cả màn hình & phím chuột?"* | Chỉ thân máy (Case only) / Trọn bộ kèm màn hình & phụ kiện. |
| **4. Sở thích cá nhân (Preferences)** | *"Bạn có ưu tiên thương hiệu hay kiểu dáng nào không?"* | Intel vs AMD, NVIDIA vs Radeon, vỏ bể cá LED RGB hay đen tĩnh lặng, kích thước ITX nhỏ gọn hay ATX thoáng khí. |

> [!TIP]
> Sử dụng công cụ `ask_question` hoặc đặt câu hỏi ngắn gọn trực tiếp trong chat nếu người dùng chỉ nói chung chung như: *"Build cho tôi một bộ PC"* hoặc *"Tư vấn PC để làm việc"*.

---

## 2. Ma Trận Phân Bổ Ngân Sách Động Theo Tác Vụ (Dynamic Allocation Engine)

Sau khi có ngân sách và tác vụ từ người dùng, Agent áp dụng ma trận tỷ trọng:

```
┌────────────────────────────────────────────────────────────────────────┐
│                      TỶ TRỌNG NGÂN SÁCH THEO TÁC VỤ                    │
├────────────────────────┬─────────┬─────────┬─────────┬────────┬────────┤
│ Tác vụ                 │   GPU   │   CPU   │   RAM   │  SSD   │ Nguồn/Vỏ│
├────────────────────────┼─────────┼─────────┼─────────┼────────┼────────┤
│ 1. Gaming AAA / 2K-4K  │ 45–55%  │ 20–25%  │ 10–12%  │ 8–10%  │ 12–15% │
│ 2. Data / Docker / Dev │ 10–15%  │ 35–45%  │ 20–25%  │ 12–15% │ 12–15% │
│ 3. Local AI / DeepLearn│ 55–65%  │ 15–20%  │ 15–20%  │ 8–10%  │ 10–12% │
│ 4. 3D Render / Video   │ 35–40%  │ 30–35%  │ 15–20%  │ 10–12% │ 12–15% │
│ 5. Văn phòng / Học tập │ 0% (iGPU│ 40–50%  │ 15–20%  │ 15–20% │ 20–25% │
└────────────────────────┴─────────┴─────────┴─────────┴────────┴────────┘
```

### Chi tiết logic từng nhóm:
1. **Gaming AAA / Đồ họa nặng**:
   - GPU là linh kiện quyết định FPS. Dồn tối đa tiền cho VGA (RTX 4060, 4070 Super, RX 6700 XT...). CPU chỉ cần 6C/12T (i5-12400F, Ryzen 5 7600) là đủ không nghẽn.
2. **Data Science / Docker Containers / Multi-Agent (AI chạy Cloud/API)**:
   - CPU nhiều nhân thực sự (>10C/16T hoặc 14C/20T như i5-13500) để gánh đồng thời nhiều worker Docker.
   - RAM tối thiểu 32GB (chọn mainboard 4 khe RAM để nâng cấp 64GB).
   - SSD NVMe PCIe Gen 4 (>5000MB/s).
   - Hạ GPU xuống mức tối thiểu (GTX 1650, RX 6500 XT, Arc A380) vì không train AI trên máy.
3. **Local AI / Deep Learning (Offline LLM / Stable Diffusion)**:
   - **VRAM của GPU là tối thượng**: Tối thiểu 12GB - 16GB VRAM NVIDIA (RTX 3060 12GB, RTX 4060 Ti 16GB, RTX 4070 Ti Super 16GB, RTX 3090/4090 24GB).
4. **Văn phòng / Học sinh sinh viên**:
   - Sử dụng CPU có đồ họa tích hợp (Intel Core non-F hoặc AMD Ryzen dòng G) để cắt hẳn chi phí card rời.

---

## 3. Kiểm Tra Tính Tương Thích Kỹ Thuật

Mọi cấu hình phải vượt qua các chốt chặn kiểm tra:
1. **Socket CPU & Chipset**:
   - Intel Gen 12/13/14 $\rightarrow$ `LGA1700` (H610, B760, Z790).
   - AMD Ryzen 7000/9000 $\rightarrow$ `AM5` (A620, B650, X670).
2. **Chuẩn RAM**:
   - Đối chiếu Mainboard hỗ trợ DDR4 hay DDR5 để chọn đúng loại RAM.
3. **Tính Công Suất Nguồn Thực Tế**:
   - Sử dụng script: `python ./scripts/calc_wattage.py --cpu "<mã_cpu>" --gpu "<mã_gpu>"`
   - Bắt buộc nguồn có chứng nhận tối thiểu **80 Plus Bronze**.
4. **Kích thước Tản nhiệt & Vỏ Case**:
   - CPU TDP > 120W (i5-13500 full-load, dòng K, Ryzen 7/9) phải dùng tản tháp 4-6 ống đồng hoặc tản nước AIO, không dùng tản stock.

---

## 4. Tra Cứu Giá Real-time & Báo Giá (BOM)

Sử dụng công cụ `web_search` và `fetch_web_page` của tầng Global để quét giá thị trường tại các đại lý lớn:
* `web_search("giá <tên_linh_kiện> anphatpc OR gearvn OR hacom OR kccshop OR nguyencongpc")`

Báo cáo gửi người dùng luôn có:
1. Bảng linh kiện chi tiết (CPU, Main, RAM, SSD, VGA, Nguồn, Tản, Vỏ) kèm giá và lý do chọn.
2. Tổng chi phí dự tính & khoản tiết kiệm khi mua theo combo.
3. Khả năng nâng cấp trong 2-3 năm tới.

---

## 5. Tự Động Build Thử Trên Web Bán Lẻ (Khi Người Dùng Yêu Cầu)

Khi người dùng muốn xem cấu hình trực tiếp trên web bán lẻ:
```bash
uv run --with playwright python ./scripts/auto_builder_hacom.py --cpu "<cpu>" --ram "<ram>" --ssd "<ssd>" --vga "<vga>" --psu "<psu>"
```
* Nếu người dùng muốn bật cửa sổ Chrome để xem trực tiếp, thêm cờ `--headed`.
* Script sẽ tự động chọn linh kiện, chụp ảnh màn hình bảng tổng hợp và trích xuất tổng tiền trả về cho người dùng.
