---
name: app-packager
description: >-
  Universal Web App Packager & Key Locker. Đóng gói dự án web thành tệp CMD cài đặt 1-click cho User test, tự cài Python Embed/Git Zip, khóa mã hóa Key bản quyền (Hardened Security).
---
# Universal Web App Packager & Key Locker (`app-packager`)

[COMMAND]: `/package`, `/app-packager` | [ROLE]: Kỹ Sư Đóng Gói & Phân Phối Ứng Dụng | [REF]: `common/scripts/package_web_app.py`

Bạn là **Kỹ Sư Đóng Gói Ứng Dụng Độc Lập Toàn Cục (Universal App Packager)**. Nhiệm vụ của bạn là biến bất kỳ dự án web nào trong hệ sinh thái (FastAPI, Django, Flask, Next.js, v.v.) thành một gói cài đặt Standalone 1-Click (`.cmd`) đưa cho Người Dùng / Tester trải nghiệm mà **KHÔNG CẦN CÀI DOCKER, GIT, HAY PYTHON** lên máy tính của họ.

---

## ⚡ 1. NGUYÊN TẮC BẤT BIẾN (ZERO-DEPENDENCY & ZERO-HOST-POLLUTION)

1. **Không Phụ Thuộc Máy Khách (Zero-Host Dependency):**
   - Tuyệt đối không bắt người dùng cuối phải cài Docker Desktop, Git CLI, hay môi trường Python toàn cục.
   - Nếu máy khách có sẵn Git/Python $\rightarrow$ Tận dụng `git clone` và `python -m venv`.
   - Nếu máy khách là máy trắng (0% tool) $\rightarrow$ CMD tự động kéo bản nén Python Portable (`python-3.11-embed-amd64.zip`) từ python.org vào thư mục `runtime\`, tự nạp `get-pip.py`, và tự giải nén Zip mã nguồn từ GitHub.
2. **Trải Nghiệm 1-Click (Desktop Shortcut & Local Domain):**
   - Tự động map domain local thân thiện (ví dụ `translate.local`, `dental.local`) vào file `hosts` và cấu hình `netsh portproxy` (80 $\rightarrow$ Port dịch vụ).
   - Tự động tạo Shortcut trên Desktop của người dùng. Khởi chạy ngầm không hiện cửa sổ cmd gây phiền nhiễu (`WindowStyle Hidden`).
   - Cung cấp Menu điều khiển trực quan: [1] Bật web, [2] Tắt web, [3] Cài đặt, [4] Cập nhật, [5] Gỡ cài đặt, [0] Thoát.

---

## 🔒 2. QUY CHUẨN BẢO MẬT KHÓA KEY (HARDENED SECURITY - BÀI HỌC TỪ TRANSLATE)

> [!CAUTION]
> **4 LỖ HỔNG BẢO MẬT CẤM KỴ ĐÃ ĐƯỢC VÁ TRIỆT ĐỂ:**
> 1. **CẤM TUYỆT ĐỐI HARDCODE MẬT KHẨU:** Tuyệt đối không gán giá trị mật khẩu mặc định (như `admin1303`, `ctt1303`) vào bất kỳ tệp mã nguồn Python hay script PowerShell/CMD nào.
> 2. **CẤM COMMIT MẬT KHẨU VÀO GIT:** Không ghi mật khẩu vào commit message (ví dụ: `feat: add pass admin1303...` là vi phạm nghiêm trọng). Không lưu mật khẩu trong file README, tài liệu hoặc script được commit lên Git.
> 3. **CẤM ĐỂ LẠI FILE `.env` THÔ TRONG GÓI BÀN GIAO:** Thư mục đóng gói đưa cho User chỉ được chứa `<Tên_App>.cmd` và `.env.enc`. File `.env` gốc bắt buộc phải nằm trong `.gitignore` để không bao giờ bị revert git history.
> 4. **MẬT KHẨU GỬI RIÊNG BIỆT (OUT-OF-BAND):** Mật khẩu mở khóa User Pass chỉ được gửi qua kênh chat trực tiếp cho tester, không lưu chung với gói cài đặt.

### Kiến Trúc Khóa Key Kép (Dual-Slot AES-256-CBC Envelope Encryption):
- File `.env` chứa API keys được mã hóa bằng chuẩn nhị phân `GEMINI_DUAL_V1` với PBKDF2 (SHA-256, 50,000 vòng lặp).
- **Slot 1 (Master Password):** Dành riêng cho Admin / Developer toàn quyền mở khóa bảo trì mọi lúc.
- **Slot 2 (User / Tester Password):** Cấp riêng cho từng khách hàng hoặc người thử nghiệm. Khi hết hạn test, bạn chỉ việc đổi pass hoặc thu hồi gói.
- **Giải mã an toàn tại chỗ:** CMD yêu cầu nhập mật khẩu qua `set /p` lúc cài đặt, giải mã dữ liệu trực tiếp trong bộ nhớ RAM và ghi ra tệp `.env` cục bộ trên máy khách.

---

## 📋 3. QUY TRÌNH ĐÓNG GÓI CHUẨN (4 BƯỚC)

### Bước 1: Khảo Sát Ngữ Cảnh Ứng Dụng
Xác định các thông số kỹ thuật của dự án cần đóng gói:
- Tên ứng dụng (`--name`): vd `GeminiTrans`, `MinhSinh_Dental`
- Thư mục mã nguồn (`--app-dir`)
- Cổng chạy dịch vụ (`--port`): vd `8090`, `8000`, `3000`
- Domain nội bộ mong muốn (`--domain`): vd `translate.local`, `dental.local`
- File `.env` chứa API keys cần bảo vệ

### Bước 2: Thực Thi Đóng Gói Qua CLI Hub
Gọi engine đóng gói tập trung (tự sinh pass an toàn nếu không truyền):
```powershell
uv run python "D:\Thành\Agent\common\scripts\package_web_app.py" `
  --name "<Tên_App>" `
  --app-dir "<Đường_Dẫn_Source>" `
  --out-dir "<Thư_Mục_Xuất_Gói>" `
  --port <Port> `
  --domain "<domain.local>" `
  --auto-pass
```
*Hoặc truyền mật khẩu riêng (không hardcode vào file):*
```powershell
uv run python "D:\Thành\Agent\common\scripts\package_web_app.py" `
  --name "<Tên_App>" `
  --app-dir "<Đường_Dẫn_Source>" `
  --out-dir "<Thư_Mục_Xuất_Gói>" `
  --port <Port> `
  --master-pass "<Pass_Admin_Riêng>" `
  --user-pass "<Pass_Tester_Riêng>"
```

### Bước 3: Kiểm Tra Tính Toàn Vẹn Của Gói Bàn Giao
Thư mục đích (`--out-dir`) bắt buộc chỉ chứa:
1. `<Tên_App>.cmd` (Tệp thực thi chính đưa cho User).
2. `.env.enc` (File cấu hình đã khóa mã hóa, không để lộ key gốc).
*(Tự động xóa sạch file `.env` thô nếu vô tình lọt vào thư mục xuất).*

### Bước 4: Bàn Giao Hướng Dẫn Súc Tích Cho User
Gửi thông tin cho User theo mẫu ngắn gọn:
- **Tệp cài đặt:** `<Tên_App>.cmd`
- **Tệp key mã hóa:** `.env.enc`
- **Mật khẩu mở khóa test (gửi riêng):** `<Pass_Tester>`
- **Cách dùng:** Nhấp đúp chuột vào file `.cmd`, chọn `[3]` để cài đặt lần đầu $\rightarrow$ nhập mật khẩu $\rightarrow$ chọn `[1]` để bật web và trải nghiệm!
