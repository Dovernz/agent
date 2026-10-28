---
name: pc-rules
description: Quy chuẩn kỹ thuật bắt buộc khi tư vấn và build cấu hình máy tính.
trigger: model_decision
---

# PC Builder Rules & Hardware Standards

Mọi Agent tư vấn cấu hình PC BẮT BUỘC tuân thủ các quy tắc phần cứng sau:

1. **Không nghẽn cổ chai (No Bottleneck)**: Tuyệt đối không phối CPU quá yếu với GPU cao cấp (vd: i3-10100 với RTX 4070) hoặc CPU quá nóng với tản nhiệt stock.
2. **Quy chuẩn bo mạch chủ 4 khe RAM**: Với các tác vụ Data Science, Docker, AI và lập trình, khuyến nghị ưu tiên mainboard có **4 khe RAM** để đảm bảo khả năng nâng cấp về sau.
3. **An toàn nguồn điện (PSU Safety)**:
   - Công suất nguồn tối thiểu = $(\text{TDP}_{\text{CPU}} + \text{TDP}_{\text{GPU}} + 100\text{W}) \times 1.25$.
   - Bắt buộc đạt chứng chỉ **80 Plus Bronze** trở lên. Cấm tư vấn nguồn noname/công suất ảo.
4. **Tách biệt Workload**:
   - AI chạy Cloud/API $\rightarrow$ Hạ GPU xuống mức cơ bản, dồn ngân sách tối đa cho CPU đa nhân và RAM.
   - AI chạy Local (LLM/Stable Diffusion) $\rightarrow$ Ưu tiên card NVIDIA RTX có VRAM tối thiểu 12GB - 16GB.
