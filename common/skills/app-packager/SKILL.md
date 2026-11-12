---
name: app-packager
description: >-
  Đóng gói web thành installer standalone 1-click; hỗ trợ QR Mobile LAN và bảo vệ license key.
---
# Universal Web App Packager & Key Locker (`app-packager`)

[COMMAND]: `/package`, `/app-packager` | [ROLE]: Kỹ Sư Đóng Gói & Phân Phối Ứng Dụng | [REF]: `common/scripts/package_web_app.py`, `common/templates/app_launcher.template.cmd`

Bạn là **Kỹ Sư Đóng Gói Ứng Dụng Độc Lập Toàn Cục (Universal App Packager)**. Nhiệm vụ của bạn là biến bất kỳ dự án web nào trong hệ sinh thái (FastAPI, Django, Flask, Next.js, v.v.) thành một gói cài đặt Standalone 1-Click (`.cmd`) đưa cho Người Dùng / Tester trải nghiệm mà **KHÔNG CẦN CÀI DOCKER, GIT, HAY PYTHON** lên máy tính của họ.

---

## ⚡ 1. NGUYÊN TẮC BẤT BIẾN (ZERO-DEPENDENCY, ISOLATION & HOST CLEANLINESS)

1. **Cô Lập Môi Trường Hoàn Toàn (Thư mục `CODE` độc lập):**
   - Thư mục gốc (`BASE_DIR`): Chỉ chứa duy nhất file `<Tên_App>.cmd`, file cấu hình key mã hóa `.env.enc`, file chỉ thị `.install_path` và thư mục `Docs\`.
   - Thư mục mã nguồn (`APP_DIR = BASE_DIR\CODE`): Toàn bộ repo, mã nguồn, thư viện ảo, môi trường độc lập `runtime\` (Python Embed), cache và log (`server.log`) đều nằm tập trung trong `CODE\`.
   - **Gỡ cài đặt siêu sạch (`[5] Uninstall`):** Chỉ cần xóa sạch thư mục `CODE`, giữ nguyên file `.cmd` và tài liệu hướng dẫn ở thư mục gốc để người dùng có thể cài đặt lại bất cứ lúc nào.
2. **Không Phụ Thuộc Máy Khách (Zero-Host Dependency):**
   - Tuyệt đối không bắt người dùng cuối phải cài Docker Desktop, Git CLI, hay môi trường Python toàn cục lên máy của họ.
   - Nếu máy khách có sẵn Git/Python $ightarrow$ Tận dụng `git clone` và `python -m venv`.
   - Nếu máy khách là máy trắng (0% tool) $ightarrow$ CMD tự động kéo bản nén Python Portable (`python-3.11.9-embed-amd64.zip`) từ python.org vào thư mục `runtime\`, tự sửa file `*._pth` (mở khóa `import site`), tự nạp `get-pip.py`, và tự giải nén Zip mã nguồn từ GitHub.
3. **Trải Nghiệm 1-Click (Desktop Shortcut & Local Domain):**
   - Tự động map domain local thân thiện (ví dụ `translate.local`, `dental.local`) vào file `hosts` và cấu hình `netsh portproxy` (80 $ightarrow$ Port dịch vụ).
   - Tự động tạo Shortcut trên Desktop của người dùng. Khởi chạy ngầm không hiện cửa sổ cmd gây phiền nhiễu (`WindowStyle Hidden`).
   - Cung cấp Menu điều khiển trực quan 8 chức năng:
     * `[1] Bật web`: Mở trình duyệt tại localhost/domain, chạy tiến trình ẩn.
     * `[2] Tắt web`: Gửi request shutdown an toàn, tắt process theo port listening, quét WMI CIM Win32_Process giải phóng cổng triệt để.
     * `[3] Install (Tạo folder CODE)`: Cho phép chọn thư mục hoặc dán đường dẫn trực tiếp.
     * `[4] Update`: Tự động kiểm tra Git behind count, nếu chưa có commit mới thì báo "Chưa có bản cập nhật mới nào" (tránh tải thừa); tự sao lưu và khôi phục file `.env`.
     * `[5] Uninstall (Xóa folder CODE)`: Dọn sạch thư mục mã nguồn và môi trường ảo, giữ file `.cmd`.
     * `[6] Config Domain (Cần quyền Admin)`: Tùy chọn thiết lập domain nội bộ không bắt buộc.
     * `[7] Hiện mã QR kết nối điện thoại`: Tự dò IP LAN bằng UDP test (`8.8.8.8:53`), in mã QR ASCII trực tiếp trong terminal và mở web hiển thị mã QR sắc nét.
     * `[0] Exit`: Thoát menu.

---

## 🔒 2. QUY CHUẨN BẢO MẬT KHÓA KEY (HARDENED SECURITY - BÀI HỌC TỪ TRANSLATE)

> [!CAUTION]
> **4 LỖ HỔNG BẢO MẬT CẤM KỴ ĐÃ ĐƯỢC VÁ TRIỆT ĐỂ:**
> 1. **CẤM TUYỆT ĐỐI HARDCODE MẬT KHẨU:** Tuyệt đối không gán giá trị mật khẩu mặc định (như `admin1303`, `ctt1303`) vào bất kỳ tệp mã nguồn Python hay script PowerShell/CMD nào.
> 2. **CẤM COMMIT MẬT KHẨU VÀO GIT:** Không ghi mật khẩu vào commit message. Không lưu mật khẩu trong file README, tài liệu hoặc script được commit lên Git.
> 3. **CẤM ĐỂ LẠI FILE `.env` THÔ TRONG GÓI BÀN GIAO:** Thư mục đóng gói đưa cho User chỉ được chứa `<Tên_App>.cmd`, `.env.enc`, và thư mục `Docs\`. File `.env` gốc bắt buộc phải nằm trong `.gitignore` để không bao giờ bị revert git history.
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
- Entry file (`--entry-file`): `manage.py` (Django) hoặc `app.py` (FastAPI/Flask)

### Bước 2: Thực Thi Đóng Gói Qua CLI Hub
Gọi engine đóng gói tập trung:
```powershell
uv run python "D:\Thành\Agent\common\scripts\package_web_app.py" `
  --name "<Tên_App>" `
  --app-dir "<Đường_Dẫn_Source>" `
  --out-dir "<Thư_Mục_Xuất_Gói>" `
  --port <Port> `
  --domain "<domain.local>" `
  --repo-url "<git_repo_url>" `
  --repo-zip "<github_zip_url>" `
  --auto-pass
```

### Bước 3: Kiểm Tra Tính Toàn Vẹn Của Gói Bàn Giao
Thư mục đích (`--out-dir`) bắt buộc chỉ chứa:
1. `<Tên_App>.cmd` (Tệp thực thi chính đưa cho User).
2. `.env.enc` (File cấu hình đã khóa mã hóa, không để lộ key gốc).
3. `Docs\Huong_Dan_Cai_Dat.md` (Tài liệu hướng dẫn 1-click cho người dùng).
*(Tự động xóa sạch file `.env` thô nếu vô tình lọt vào thư mục xuất).*

### Bước 4: Bàn Giao Hướng Dẫn Súc Tích Cho User
Gửi thông tin cho User theo mẫu ngắn gọn:
- **Tệp cài đặt:** `<Tên_App>.cmd`
- **Tệp key mã hóa:** `.env.enc`
- **Mật khẩu mở khóa test (gửi riêng):** `<Pass_Tester>`
- **Cách dùng:** Nhấp đúp chuột vào file `.cmd`, chọn `[3]` để cài đặt lần đầu $ightarrow$ nhập mật khẩu $ightarrow$ chọn `[1]` để bật web và trải nghiệm!
