# Tech Stack Knowledge Base (Quy chuẩn Dự án Web)

Mọi Agent BẮT BUỘC tuân thủ trước khi code để đồng bộ kiến trúc:
- **Nguyên tắc cốt lõi:** Code siêu ngắn, DRY, Component-Driven (chia nhỏ UI tối đa thay vì nhồi nhét).
- **Frontend State:** Call API bắt buộc dùng bộ Cache (như React Query/SWR). State UI dùng công cụ nhẹ (như Zustand), cấm dùng Redux cồng kềnh.
- **Tốc độ (Performance):** Bắt buộc Lazy Loading các page/ảnh nặng. Áp dụng chuẩn UI Mobile-First (làm màn hình Mobile trước).
- **Auto-Cleanup:** Xóa sạch script tạm (scratch files) sau khi dùng.
- **Tiêu chuẩn:** Tuân thủ `m2m-protocol.md`.
