---
name: pc-rules
description: Quy chuẩn bắt buộc về khảo sát nhu cầu, tỷ trọng ngân sách và an toàn kỹ thuật phần cứng.
trigger: model_decision
---

# PC Builder Rules & Hardware Standards

Mọi Agent tư vấn cấu hình PC BẮT BUỘC tuân thủ các quy tắc sau:

1. **Quy Tắc Chốt Chặn Khảo Sát (Intake Gate - Bắt buộc)**:
   - **Tuyệt đối KHÔNG tự ý giả định** ngân sách hay tác vụ nếu người dùng chưa cung cấp.
   - Khi nhận yêu cầu chung chung (vd: *"build pc cho mình"*), Agent **BẮT BUỘC HỎI LÀM RÕ 4 YẾU TỐ**:
     1. Ngân sách dự tính (triệu VNĐ)?
     2. Nhu cầu/tác vụ chính (Gaming, Code/Docker/Data, Local AI, Đồ họa, hay Văn phòng)?
     3. Phạm vi (Chỉ case hay gồm cả màn hình & phím chuột)?
     4. Sở thích phần cứng (Intel/AMD, NVIDIA/Radeon, kích thước case, đèn LED)?
   - **Chỉ khi người dùng nói**: *"build mặc định"* hoặc *"tùy bạn chọn"* thì mới áp dụng cấu hình baseline tầm trung.

2. **Quy Tắc Phân Bổ Ngân Sách Linh Hoạt**:
   - Gaming: VGA chiếm ~50% ngân sách.
   - Data Science / Docker (Cloud AI): Dồn ~40% ngân sách cho CPU nhiều nhân luồng và ~20% cho RAM (tối thiểu 32GB, 4 khe nâng cấp), hạ tối đa GPU.
   - Local AI / Deep Learning: Ưu tiên tối thượng là VRAM GPU (tối thiểu 12GB–16GB VRAM NVIDIA).
   - Văn phòng: Dùng iGPU tích hợp, không lắp card rời.

3. **Quy Tắc An Toàn Nguồn Điện (PSU Safety)**:
   - Công suất nguồn tối thiểu = $(\text{TDP}_{\text{CPU}} + \text{TDP}_{\text{GPU}} + 100\text{W}) \times 1.25$.
   - Bắt buộc nguồn có chứng nhận tối thiểu **80 Plus Bronze** từ các hãng uy tín.

4. **Quy Tắc Kiểm Tra Tương Thích Kỹ Thuật**:
   - Check socket CPU vs Mainboard (LGA1700 vs AM5).
   - Check chuẩn RAM (DDR4 vs DDR5).
   - Check kích thước tản nhiệt & case nếu CPU có TDP > 120W lúc load nặng.
