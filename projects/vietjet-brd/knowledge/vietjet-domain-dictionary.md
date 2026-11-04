# Từ Điển Nghiệp Vụ Hàng Không Vietjet (Aviation & Sales Domain)

Tài liệu tham khảo chuyên ngành phục vụ xây dựng báo cáo và giải thích thuật ngữ trong BRD.

---

## 1. Mạng Bay & Hãng Khai Thác
- **VJ**: Vietjet Air (Việt Nam).
- **VZ**: Thai Vietjet (Thái Lan).
- **Dep / Arr**: Sân bay khởi hành (Departure) / Sân bay đến (Arrival) theo chuẩn IATA 3 ký tự (SGN, HAN, DAD, CXR, PQC, BKK, DMK, ICN, NRT, PKX, PVG, DEL, BOM, MEL, SYD, ALA, NQZ...).
- **Sector / Route**: Đường bay / Chặng bay (Ví dụ: `SGN-HAN`, `SGN-ICN`, `HAN-BKK`).
- **Thị trường (Market)**:
  * 2 sân bay đều ở Việt Nam -> `Vietnam` (Nội địa).
  * 2 sân bay ở Thái Lan (khai thác bởi VZ) -> `Thailand` (Nội địa Thái).
  * 1 sân bay ở VN, 1 sân bay ở nước ngoài -> Tính theo quốc gia nước ngoài (`China`, `Korea`, `Thailand`, `India`, `Australia`, `Kazakhstan`, `Japan`...).
  * 2 sân bay đều ở nước ngoài ngoài VN và Thái Lan -> `Others`.

---

## 2. Kênh Bán & Đối Tác (Sales Channels & Agencies)
- **Direct Web / Mobile App**: Kênh bán trực tiếp của hành khách qua website vietjetair.com hoặc app Vietjet.
- **OTA (Online Travel Agent)**: Đại lý du lịch trực tuyến (Trip.com, Ctrip, Traveloka, Agoda...).
- **GDS (Global Distribution System)**: Hệ thống phân phối toàn cầu (Amadeus, Sabre, Travelport...).
- **Agency (PSA / Đại lý chỉ định / Đại lý truyền thống)**: Các đại lý bán vé có mã Agency ID (ví dụ: `34001038 - CTRIP.COM`, `34000017 - LETSFLY LIMITED`).
- **Charter**: Chuyến bay thuê chuyến nguyên chuyến hoặc bán block chỗ cho đối tác lữ hành.

---

## 3. Vé & Đặt Chỗ (Reservations & Fares)
- **PNR (Passenger Name Record)**: Mã đặt chỗ gồm 6 ký tự chữ và số (Ví dụ: `KG3NJ5`, `K2J2T9`).
- **ResNumber**: Mã định danh reservation hệ thống Amelia / PSS.
- **Hạng vé (Fare Class)**:
  * `Eco`: Hạng vé phổ thông cơ bản.
  * `Deluxe (DLX)`: Hạng vé phổ thông linh hoạt (kèm hành lý, suất ăn, đổi ngày).
  * `SkyBoss (SBOS)`: Hạng thương gia cao cấp (ưu tiên check-in, phòng chờ, suất ăn nóng, 30kg ký gửi).
  * `SkyBoss Business (SBSS)`: Hạng thương gia trên tàu bay thân rộng A330 (ghế nằm phẳng flatbed).
- **Phân loại nhóm (Pax Group Type)**:
  * `FIT (Free Independent Traveler)`: Khách lẻ (dưới 9 khách trong 1 booking).
  * `GIT (Group Inclusive Tour)`: Khách đoàn (từ 9 khách trở lên trong 1 booking).
- **Trạng thái đặt chỗ**:
  * `PAID`: Đã hoàn tất thanh toán.
  * `HOLD`: Đang giữ chỗ chờ thanh toán theo thời hạn Time-limit (TL).
  * `CXL / CANCELLED`: Đã hủy.
  * `BOARDED / BORD`: Hành khách đã lên tàu bay.
  * `NOSHOW / NOIN`: Hành khách đã đặt chỗ nhưng không thực hiện chuyến bay.

---

## 4. Dịch Vụ Bán Thêm (Ancillary / Add-ons)
- **Baggage (Hành lý)**: Gói hành lý ký gửi quá cước (BAG15, BAG20, BAG30, BAG40, Oversized bag...).
- **Hot Meals (Suất ăn nóng)**: Đặt trước món ăn trên chuyến bay (Cơm gà, Xôi khúc, Miến xào...).
- **Seat Assignment (Chọn chỗ ngồi)**: Ghế hàng đầu (Hot seats), ghế thoát hiểm (Extra legroom), ghế cửa sổ/lối đi.
- **Priority Services**: Priority Check-in (Ưu tiên làm thủ tục tại quầy riêng), Priority Boarding.
- **Lounge (Phòng chờ thương gia)**: Tiếp cận phòng khách bông sen / business lounge tại sân bay.
- **Travel Insurance**: Bảo hiểm du lịch Bảo Việt / HD Insurance.
- **E-Sim / Fast Track**: Tiện ích viễn thông và thủ tục an ninh nhanh.

---

## 5. Chỉ Số Hiệu Quả Khai Thác (Operational KPIs)
- **Capacity**: Tổng số ghế cung ứng trên chuyến bay (Ví dụ: A320 = 180 ghế, A321 = 230/240 ghế, A330 = 365/377 ghế).
- **Pax Confirm**: Số lượng khách đã đặt chỗ xác nhận.
- **Pax Flown / Boarded**: Số lượng khách thực tế bay.
- **Load Factor (LF)**: Hệ số lấp đầy ghế:
  $$\text{Load Factor} = \frac{\text{Pax Flown}}{\text{Capacity}} \times 100\%$$
- **Flight Revenue**: Doanh thu chuyến bay gồm Fare + Surcharges + Ancillary.
