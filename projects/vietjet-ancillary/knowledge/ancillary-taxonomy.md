# Quy chuẩn Danh mục Sản phẩm Ancillary & Chính sách Hoa hồng Sân bay

Tài liệu này lưu trữ toàn bộ từ điển 9 nhóm sản phẩm Ancillary quy chuẩn của Vietjet và ma trận chính sách tính hoa hồng hành lý theo Tờ trình KPI Sân bay.

---

## 1. Bảng 9 Nhóm Sản phẩm Ancillary Quy chuẩn

| STT | Tên nhóm (Product Group) | Mã nhận diện chính | Nguồn Master Data | Mô tả & Sản phẩm đại diện |
| :---: | :--- | :--- | :--- | :--- |
| **1** | **Baggage & Cabin Baggage** | `BA`, `CB`, `QR` | Surcharge & SSR | Hành lý ký gửi mua trước (15kg-100kg), hành lý mua tại quầy check-in sân bay, hành lý tính phí tại cửa khởi hành (Gate), hành lý quá cước lẻ theo cân, hành lý xách tay 2kg/7kg. |
| **2** | **Seat Assignment** | `SA` | Surcharge & SSR | Dịch vụ chọn chỗ ngồi trước chuyến bay: Ghế đầu hàng (Hot Seat), Ghế để chân rộng (Front Seat), Ghế tiêu chuẩn (Normal Seat), Ghế trống liền kề (Empty Seat). |
| **3** | **Meals & Beverages** | `SR` (Category `Meal`) | PSS SSR | Suất ăn nóng và đồ uống đặt trước: Cơm chiên, Phở bò, Bánh mì kẹp, Món chay, Cà ri Ấn Độ, Mì xào, Nước giải khát. |
| **4** | **Priority & Airport Convenience** | `SR` (Category `Priority Checkin`), `SP`, `CS`, `QT` | Surcharge & SSR | Thủ tục ưu tiên tại quầy riêng (Priority Check-in), gói dịch vụ phòng chờ cao cấp SkyBoss Plus (`SP`), hỗ trợ nối chuyến (`CS`), xuất vé nhanh (`QT`). |
| **5** | **Special Services** | `SV`, `IF`, `NL` | Surcharge & SSR | Thú cưng trên cabin (`PETC`), Trẻ em đi một mình (`UM` / `YPTA`), Dịch vụ đón tiễn Meet & Greet, Phí phục vụ em bé (`IF`), Phí không được phép nhập cảnh (`NL`). |
| **6** | **Travel Insurance** | `IN`, `IT`, `MC` (HDI) | PSS Surcharge | Bảo hiểm du lịch trọn gói, thuế bảo hiểm du lịch, bảo hiểm thất lạc hành lý đối tác HDI (Nội địa & Quốc tế). |
| **7** | **Inflight Merchandise & Duty Free** | `MC` | PSS Surcharge | Hàng lưu niệm trên tàu bay, dịch vụ quấn bọc hành lý tại sân bay (Luggage Wrapping). |
| **8** | **Flight Modification, Penalty & Admin Fees** | `CX`, `MD`, `XX`, `UF`, `NR`, `PD`, `LT` | PSS Surcharge | Phí đổi vé (`MD`), Phí hủy vé (`CX`), Phí bỏ chuyến No-show (`XX`), Nâng hạng vé (`UF`), Phí giờ cao điểm (`PD`), Phí xử lý muộn (`LT`). |
| **9** | **Other System & Legacy Charges** | `HA`, `PM`, `AM`, `MF`, `JL`, `BR`, `CR`, `BL`, `FC` | PSS Surcharge | Phí tiện ích thanh toán (`PM`), Phí quản trị hệ thống (`HA`, `AM`, `MF`), Hợp tác liên danh đối tác (`JL`, `BR`, `CR`), Bù trừ tài chính (`BL`, `WO`, `FC`). |

---

## 2. Danh mục Loại trừ (Non-Ancillary Charges)
Khi phân tích danh mục Ancillary từ hệ thống cũ (`Ancillary Type.xlsx`), BẮT BUỘC loại bỏ 10 mã sau vì thuộc nhóm **Giá vé thuần (Fare)** hoặc **Thuế/Phí sân bay & an ninh soi chiếu nhà nước**:
- `AI`: Airport Improvement Fund (Phí sân bay).
- `SG`: Passenger service charge (Thuế dịch vụ sân bay Singapore).
- `OO`: Passenger Security Service charges (Phí an ninh Singapore).
- `OP`: Aviation levy.
- `AS`: Airport Security Scan.
- `APPS`: Advance Passenger Processing System.
- `BKK E8`: Bangkok airport charge.
- `SF`: Security Fee (Phí an ninh soi chiếu).
- `MO`: Non-ancillary regulatory fee.
- `FA`: Fare (Giá vé thuần túy).

---

## 3. Ma trận Đơn giá Hoa hồng Hành lý Sân bay (KPI SÂN BAY)

Áp dụng cho view `gold_dev.com.ancillary_commission_baggage_detail`:

| Vị trí thu (Category) | Loại hành lý (Type) | Đường bay Nội địa (VND) | Đường bay Quốc tế (VND) | Công thức tính tiền |
| :--- | :--- | :---: | :---: | :--- |
| **Counter (Quầy Check-in)** | **Kiện/Gói tiêu chuẩn (G)** | 8,000 | 12,000 | Đơn giá cố định / giao dịch |
| **Counter (Quầy Check-in)** | **Quá cước lẻ theo kg (L)** | 3,000 | 5,000 | `baggage_kg * Đơn giá` |
| **Gate (Cửa Khởi hành)** | **Kiện/Gói tính phí (G)** | 5,000 | 10,000 | Đơn giá cố định / giao dịch |
| **Gate (Cửa Khởi hành)** | **Quá cước lẻ theo kg (L)** | 2,000 | 4,000 | `baggage_kg * Đơn giá` |
| **Cả Quầy & Cửa Gate** | **Quá khổ (O - Oversize)** | 30,000 | 60,000 | Đơn giá cố định / giao dịch |
