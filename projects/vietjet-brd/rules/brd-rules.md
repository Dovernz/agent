# Nguyên Tắc Tạo BRD Chuẩn Vietjet (BRD Rules)

Bộ quy tắc bắt buộc mà Agent soạn thảo BRD (`vietjet-brd-architect`) phải tuân thủ nghiêm ngặt trong mọi tình huống.

---

## 🔒 1. Quy Tắc Bất Di Bất Dịch Về Format (Immutable Structure)
- **Kiểu phông chữ & Ma trận cỡ chữ chuẩn theo từng phần**:
  * Phông chữ bắt buộc: **100% `Times New Roman`** trên toàn bộ tài liệu.
  * Cỡ chữ chuẩn cho từng phần (trích xuất từ 100% BRD gốc):
    + Tiêu đề trang bìa: **24.0 pt**, In đậm.
    + Tiêu đề Mục lục: **16.0 pt**, In đậm.
    + **Heading 1** (Mục A-F, I, II, III): **13.0 pt**, In đậm, Màu đỏ Vietjet `#EE0000`.
    + **Heading 2** (Mục con 1.1, 1.2, 2.1...): **13.0 pt**, In đậm, Màu đen `#000000`.
    + **Nội dung văn bản & gạch đầu dòng**: **12.0 pt**, Thường (`Regular`).
    + **Tiêu đề cột bảng (Table Header)**: **12.0 pt**, In đậm, Nền xám `#D7D7D7`.
    + **Ô dữ liệu bảng (Table Data Cell)**: **12.0 pt**, Thường (`Regular`).
    + **Bảng kiểm soát tài liệu (Table 0)**: **12.0 pt**.
    + **Running Header**: **9.0 pt**.
- **Cấm sửa đổi cấu trúc trang đầu**:
  * Trang bìa (Cover Page) phải giữ nguyên Logo Vietjet, layout tiêu đề, khung metadata tài liệu (Table 0), địa chỉ trụ sở Vietjet.
  * Các bảng thủ tục hành chính bắt buộc:
    - **A.** Danh sách phân phối / List of distribution (Table 1)
    - **B.** Danh sách sửa đổi / Record of Revision (Table 2)
    - **C.** Danh mục trang có hiệu lực / List of effective pages (Table 3)
    - **D.** Căn cứ vào tài liệu / References (Table 4)
    - **E.** Kiểm tra và phê duyệt / Check and Approval (Table 5 kèm khung Header IT Dept)
    - **F.** Xác nhận đơn vị tham gia rà soát / Check and Approval (Table 6)
    - **G.** Danh sách phân phối / List of distribution (Table 7)
- **Cấm làm mất Header / Footer**:
  * Running Header ở Section 1 bắt buộc có Logo Vietjet, Tên báo cáo (cột giữa) và Ngày tạo / Phiên bản (cột phải).
  * Chữ ký người phê duyệt mặc định:
    - Lê Hải Bình (ICT Director)
    - Hà Năng Việt (Director of Commercial Division) - hoặc Trưởng đơn vị nghiệp vụ liên quan.
    - Trần Phước Duy (Data Manager).

---

## 🔄 2. Quy Tắc Cập Nhật Động (Dynamic Updates)
Khi tạo BRD cho một báo cáo mới, Agent **CHỈ ĐƯỢC PHÉP THAY ĐỔI**:
1. **Tên báo cáo**:
   * Tiếng Việt in hoa chuẩn (VD: `BÁO CÁO CÁC DỊCH VỤ BÁN THÊM CỦA ĐỐI TÁC`).
   * Cập nhật đồng bộ tại: Trang bìa (P1/P2), Khung Running Header (Section 1), và Tiêu đề Mục II (P56).
2. **Ngày tạo**:
   * Định dạng `DD-MM-YYYY` trên trang bìa (VD: `29-10-2026`) và `DD/MM/YYYY` trên Header table.
   * Mặc định lấy theo ngày hiện tại của hệ thống hoặc ngày do người gửi chỉ dẫn.
3. **Mục I (Mục tiêu & Phạm vi)**:
   * Viết ngắn gọn, súc tích, phản ánh đúng bài toán kinh doanh.
   * Cập nhật Bảng đối tượng sử dụng (Khối, Phòng ban).
4. **Mục II (Chi tiết báo cáo)**:
   * 2.1 Tổng quan báo cáo.
   * 2.2 Bảng định nghĩa nghiệp vụ (nếu có công thức hoặc thuật ngữ mới).
   * 2.3 Bảng Tham số đầu vào (Input Parameters): STT, Tên cột, Định nghĩa, Ví dụ, Notes.
   * 2.4 Bảng dữ liệu chi tiết (Detailed Schema): STT, Tên cột, Định nghĩa, Ví dụ, Notes / Công thức.
5. **Mục III (Dashboard báo cáo)**:
   * 3.1 Tổng quan KPI cards và bộ lọc.
   * 3.2 Báo cáo tổng hợp cấp mạng bay / đường bay.
   * 3.3 Báo cáo chi tiết cấp chuyến bay.
   * Layout mockup giao diện.

---

## 📊 3. Quy Tắc Xử Lý Dữ Liệu Đầu Vào (Excel & User Prompt)
- Nếu người dùng cung cấp file Excel (ví dụ `20260108_REPORT REQUEST TO IT.xlsx`):
  * Tự động trích xuất mục tiêu, bộ lọc và các cột dữ liệu theo đúng dòng/sheet yêu cầu.
  * Nếu một số cột thiếu mô tả hoặc ví dụ, Agent chủ động điền giá trị mẫu thực tế theo chuẩn hàng không Vietjet (mã sân bay IATA, số hiệu chuyến bay `VJxxx`, PNR 6 ký tự...).
- Nếu người dùng mô tả bằng lời:
  * Phân tích rõ: Input filters gồm những gì? Schema chi tiết gồm những trường nào? Mục đích sử dụng là gì?
  * Tạo bảng tham số và bảng dữ liệu đầy đủ, chuyên nghiệp.

---

## ⚙️ 4. Quy Chuẩn Kỹ Thuật Sinh File (Code Engine)
- Mọi file Word `.docx` sinh ra bắt buộc phải được thực thi qua engine `D:\Thành\Agent\projects\vietjet-brd\scripts\brd_builder.py`.
- Engine này nạp từ file template gốc `template_vietjet_brd.docx`, đảm bảo:
  * Không làm hỏng quan hệ XML giữa các part và hình ảnh logo.
  * Mọi dòng mới trong bảng đều kế thừa viền (border), màu nền xám (`#D7D7D7`), đệm lề (cell margins), và font Times New Roman.
  * File kết quả xuất ra trực tiếp tại thư mục được yêu cầu (ví dụ: `D:\Vietjet\2026\COM - Sale Reports\BRD\`).
