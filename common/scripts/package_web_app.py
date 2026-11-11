#!/usr/bin/env python3
r"""
Universal Web App Packager & Key Locker (Hardened Security V3 - Code Isolation & Zero-Host Dependency)
==================================================================================================
Tác vụ:
1. Đóng gói bất kỳ ứng dụng web nào (FastAPI, Django, Flask, Streamlit) thành 1-Click .cmd độc lập.
2. Cách ly hoàn toàn mã nguồn vào thư mục 'CODE', thư mục gốc chỉ chứa file .cmd và Docs.
3. Hỗ trợ 100% Zero-Host Dependency: 0 Docker, 0 Git, 0 Python cài lên máy User.
   - Tự động tải Python 3.11 Embed từ python.org vào runtime\ khi máy trắng.
   - Tự mở khóa import site trong *._pth, tải get-pip.py và pip install -r requirements.txt ngầm.
4. Tích hợp Mạng LAN & QR Code truy cập điện thoại di động ([7] Hiện mã QR kết nối điện thoại).
5. Tích hợp Cấu hình Custom Domain ([6] Config Domain).
6. Tích hợp Cập nhật thông minh ([4] Update): Kiểm tra git behind count, không tải thừa nếu đã mới nhất.
7. Tích hợp Gỡ cài đặt an toàn ([5] Uninstall): Chỉ xóa đúng thư mục CODE, giữ nguyên file .cmd.
8. Mã hóa Key nhạy cảm bằng chuẩn kép Dual-Slot AES-256-CBC (GEMINI_DUAL_V1) qua PowerShell .NET.
"""

import os
import sys
import re
import secrets
import getpass
import argparse
import subprocess
from pathlib import Path

# Force UTF-8 for console output on Windows
try:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass


def encrypt_dual_slot_powershell(in_env_file: Path, out_enc_file: Path, master_pass: str, user_pass: str) -> bool:
    """Mã hóa payload .env bằng PowerShell built-in chuẩn GEMINI_DUAL_V1 (Không lưu mật khẩu vào file)."""
    p_master = master_pass.replace("'", "''")
    p_user = user_pass.replace("'", "''")
    f_in = str(in_env_file.resolve()).replace("'", "''")
    f_out = str(out_enc_file.resolve()).replace("'", "''")

    ps_code = f"""
$ErrorActionPreference = 'Stop'
$fIn = '{f_in}'
$fOut = '{f_out}'
$pMaster = '{p_master}'
$pUser = '{p_user}'

$data = [System.IO.File]::ReadAllBytes($fIn)

# 1. Sinh Data Key ngẫu nhiên (32 bytes AES-256) và Data IV (16 bytes)
$rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
$dataKey = New-Object byte[](32)
$rng.GetBytes($dataKey)
$dataIV = New-Object byte[](16)
$rng.GetBytes($dataIV)

# 2. Sinh Salt cho Master và User (mỗi salt 16 bytes)
$saltMaster = New-Object byte[](16)
$rng.GetBytes($saltMaster)
$saltUser = New-Object byte[](16)
$rng.GetBytes($saltUser)

# 3. Derive Key & Mã hóa Data Key cho Master Slot (PBKDF2 SHA256 50000 vòng)
$kdfM = New-Object System.Security.Cryptography.Rfc2898DeriveBytes($pMaster, $saltMaster, 50000, [System.Security.Cryptography.HashAlgorithmName]::SHA256)
$keyM = $kdfM.GetBytes(32)
$ivM = $kdfM.GetBytes(16)
$aesM = [System.Security.Cryptography.Aes]::Create()
$aesM.Key = $keyM
$aesM.IV = $ivM
$encKeyMaster = $aesM.CreateEncryptor().TransformFinalBlock($dataKey, 0, 32)

# 4. Derive Key & Mã hóa Data Key cho User Slot (PBKDF2 SHA256 50000 vòng)
$kdfU = New-Object System.Security.Cryptography.Rfc2898DeriveBytes($pUser, $saltUser, 50000, [System.Security.Cryptography.HashAlgorithmName]::SHA256)
$keyU = $kdfU.GetBytes(32)
$ivU = $kdfU.GetBytes(16)
$aesU = [System.Security.Cryptography.Aes]::Create()
$aesU.Key = $keyU
$aesU.IV = $ivU
$encKeyUser = $aesU.CreateEncryptor().TransformFinalBlock($dataKey, 0, 32)

# 5. Mã hóa Payload chính (.env) bằng Data Key
$aesD = [System.Security.Cryptography.Aes]::Create()
$aesD.Key = $dataKey
$aesD.IV = $dataIV
$encPayload = $aesD.CreateEncryptor().TransformFinalBlock($data, 0, $data.Length)

# 6. Ghi định dạng GEMINI_DUAL_V1 nhị phân hoàn chỉnh
$fs = [System.IO.File]::Create($fOut)
$magic = [System.Text.Encoding]::ASCII.GetBytes('GEMINI_DUAL_V1')
$fs.Write($magic, 0, 14)
$fs.Write($saltMaster, 0, 16)
$fs.Write($encKeyMaster, 0, 48)
$fs.Write($saltUser, 0, 16)
$fs.Write($encKeyUser, 0, 48)
$fs.Write($dataIV, 0, 16)
$fs.Write($encPayload, 0, $encPayload.Length)
$fs.Close()
"""
    try:
        cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_code]
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"[!] PowerShell Encryption Error: {e.stderr}", file=sys.stderr)
        return False


def generate_cmd_launcher(
    app_title: str,
    repo_url: str,
    repo_zip_url: str,
    zip_subfolder: str,
    start_process_args: str,
    port: int,
    domain: str,
    entry_file: str = "app.py",
) -> str:
    """Sinh nội dung file .cmd cài đặt & khởi chạy độc lập từ template chuẩn."""
    template_path = Path(__file__).parent.parent / "templates" / "app_launcher.template.cmd"
    if not template_path.exists():
        raise FileNotFoundError(f"Không tìm thấy file template tại: {template_path}")

    template = template_path.read_text(encoding="utf-8")
    slug = re.sub(r"[^a-zA-Z0-9_]", "_", app_title.lower())
    app_url = f"http://localhost:{port}"
    cmd_name = f"{app_title}.cmd"

    res = template
    res = res.replace("__APP_TITLE__", app_title)
    res = res.replace("__APP_TITLE_UPPER__", app_title.upper())
    res = res.replace("__APP_SLUG__", slug)
    res = res.replace("__CMD_NAME__", cmd_name)
    res = res.replace("__REPO_URL__", repo_url or "")
    res = res.replace("__REPO_ZIP_URL__", repo_zip_url or "")
    res = res.replace("__ZIP_SUBFOLDER__", zip_subfolder or f"{slug}-main")
    res = res.replace("__APP_PORT__", str(port))
    res = res.replace("__APP_URL__", app_url)
    res = res.replace("__DOMAIN__", domain or "")
    res = res.replace("__ENTRY_FILE__", entry_file)
    res = res.replace("__START_PROCESS_ARGS__", start_process_args)

    return res


def main():
    parser = argparse.ArgumentParser(
        description="Universal Web App Packager & Key Locker (Hardened Security V3)"
    )
    parser.add_argument("--name", required=True, help="Tên ứng dụng (vd: GeminiTrans, MinhSinh_Dental)")
    parser.add_argument("--app-dir", required=True, help="Thư mục mã nguồn của dự án")
    parser.add_argument("--out-dir", required=True, help="Thư mục xuất file cài đặt cho User")
    parser.add_argument("--port", type=int, default=8000, help="Cổng Web của ứng dụng (mặc định 8000)")
    parser.add_argument("--domain", default="", help="Tên miền cục bộ tùy chọn (vd: dental.local)")
    parser.add_argument("--repo-url", default="", help="Git repo clone URL")
    parser.add_argument("--repo-zip", default="", help="GitHub zip archive URL")
    parser.add_argument("--zip-folder", default="", help="Tên thư mục sau khi giải nén zip")
    parser.add_argument("--entry-file", default="", help="Tệp khởi động chính (tự động nhận diện manage.py hoặc app.py)")
    parser.add_argument("--run-cmd", default="", help="Lệnh tham số khởi chạy tiến trình Python")
    parser.add_argument("--env-file", default="", help="Đường dẫn file .env chứa key cần khóa")

    # BẢO MẬT: KHÔNG CÓ DEFAULT HARDCODE PASSWORD!
    parser.add_argument("--master-pass", default=None, help="Mật khẩu Master/Admin (Nếu bỏ trống sẽ nhắc nhập hoặc tự sinh)")
    parser.add_argument("--user-pass", default=None, help="Mật khẩu cấp cho Tester/User (Nếu bỏ trống sẽ nhắc nhập hoặc tự sinh)")
    parser.add_argument("--auto-pass", action="store_true", help="Tự động sinh mật khẩu ngẫu nhiên an toàn nếu không chỉ định")

    args = parser.parse_args()

    app_dir = Path(args.app_dir).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 65)
    print(f"📦 ĐÓNG GÓI ỨNG DỤNG CHO USER TEST: {args.name}")
    print("=" * 65)

    # 1. Tự động xác định Entry File và Run Arguments
    entry_file = args.entry_file
    if not entry_file:
        if (app_dir / "manage.py").exists():
            entry_file = "manage.py"
        elif (app_dir / "app.py").exists():
            entry_file = "app.py"
        elif (app_dir / "main.py").exists():
            entry_file = "main.py"
        else:
            entry_file = "app.py"

    run_args = args.run_cmd
    if not run_args:
        if entry_file == "manage.py":
            run_args = f"manage.py runserver 0.0.0.0:!APP_PORT!"
        elif entry_file == "app.py":
            run_args = f"-m uvicorn app:app --host 0.0.0.0 --port !APP_PORT!"
        else:
            run_args = f"{entry_file}"

    # 2. Xử lý Mật khẩu Dual-Slot an toàn (Không hardcode!)
    env_source = Path(args.env_file).resolve() if args.env_file else (app_dir / ".env")
    master_pass = args.master_pass
    user_pass = args.user_pass

    if env_source.exists():
        print(f"[+] Tìm thấy file cấu hình nhạy cảm: {env_source}")
        if not master_pass:
            if args.auto_pass or not sys.stdin.isatty():
                master_pass = secrets.token_urlsafe(12)
                print(f"[+] Tự động sinh Master Password ngẫu nhiên")
            else:
                master_pass = getpass.getpass("Nhập Master Password (Admin): ")
                if not master_pass:
                    master_pass = secrets.token_urlsafe(12)

        if not user_pass:
            if args.auto_pass or not sys.stdin.isatty():
                user_pass = secrets.token_urlsafe(8)
                print(f"[+] Tự động sinh User Test Password ngẫu nhiên")
            else:
                user_pass = getpass.getpass("Nhập User Password (cấp cho Tester): ")
                if not user_pass:
                    user_pass = secrets.token_urlsafe(8)

        out_enc = out_dir / ".env.enc"
        ok = encrypt_dual_slot_powershell(env_source, out_enc, master_pass, user_pass)
        if ok:
            print(f"[✓] Đã khóa mã hóa Key thành công: {out_enc}")
            print(f"    🔑 Master Password : {master_pass}")
            print(f"    🔑 User Test Pass  : {user_pass}")
            print(f"    ⚠️  LƯU Ý AN TOÀN: Hãy gửi User Pass qua kênh chat riêng biệt cho Tester!")
            print(f"    ⚠️  TUYỆT ĐỐI KHÔNG commit mật khẩu này vào Git repo!")
        else:
            print(f"[!] Lỗi khi mã hóa {env_source}")
    else:
        print("[!] Không tìm thấy file .env để khóa key. Bỏ qua bước mã hóa.")

    # 3. Sinh file CMD cài đặt độc lập
    cmd_content = generate_cmd_launcher(
        app_title=args.name,
        repo_url=args.repo_url,
        repo_zip_url=args.repo_zip,
        zip_subfolder=args.zip_folder,
        start_process_args=run_args,
        port=args.port,
        domain=args.domain,
        entry_file=entry_file,
    )

    cmd_file_name = f"{args.name}.cmd"
    out_cmd = out_dir / cmd_file_name
    with open(out_cmd, "w", encoding="utf-8") as cf:
        cf.write(cmd_content)

    # 4. Tạo thư mục tài liệu Docs\Huong_Dan_Cai_Dat.md
    docs_dir = out_dir / "Docs"
    docs_dir.mkdir(parents=True, exist_ok=True)
    doc_file = docs_dir / "Huong_Dan_Cai_Dat.md"
    doc_content = f"""# Hướng Dẫn Cài Đặt & Sử Dụng {args.name}

## 1. Yêu cầu hệ thống
- Hệ điều hành: Windows 10 / 11 (64-bit).
- **Hoàn toàn KHÔNG CẦN CÀI ĐẶT:** Docker, Git, hay Python trước trên máy tính.

## 2. Cách khởi động nhanh (1-Click)
1. Nhấp đúp chuột vào tệp `{cmd_file_name}`.
2. Chọn `[3] Cài đặt` trong Menu lần đầu tiên để hệ thống tự động thiết lập môi trường.
   - Nếu hệ thống yêu cầu mật khẩu mở khóa, hãy nhập mật khẩu được cấp riêng cho bạn.
3. Chọn `[1] Bật web` để mở giao diện ứng dụng trên trình duyệt:
   - Địa chỉ cục bộ: `http://localhost:{args.port}`
   - Địa chỉ mạng LAN (kết nối qua điện thoại/máy tính bảng cùng Wi-Fi): xem hiển thị trên Menu.
4. Chọn `[2] Tắt web` khi sử dụng xong để giải phóng cổng {args.port}.
5. Chọn `[7] Hiện mã QR` để quét mã QR kết nối nhanh trên điện thoại.

## 3. Gỡ cài đặt hoàn toàn
- Chọn `[5] Uninstall` trong Menu: Hệ thống chỉ xóa sạch thư mục `CODE`, giữ nguyên tệp `{cmd_file_name}` để bạn có thể cài lại bất cứ lúc nào.
"""
    doc_file.write_text(doc_content, encoding="utf-8")

    # 5. Kiểm tra vệ sinh an toàn thư mục bàn giao
    # CẤM tuyệt đối để file .env thô trong out_dir
    unencrypted_env_in_out = out_dir / ".env"
    if unencrypted_env_in_out.exists():
        unencrypted_env_in_out.unlink()
        print(f"[SECURITY] Đã loại bỏ file .env thô khỏi thư mục bàn giao {out_dir}")

    print(f"[✓] Đã sinh file cài đặt Standalone 1-Click: {out_cmd}")
    print(f"[✓] Đã tạo tài liệu hướng dẫn: {doc_file}")
    print("\n" + f"🎯 HOÀN TẤT ĐÓNG GÓI! Bạn chỉ cần gửi thư mục hoặc file CMD cho User:")
    print(f"   👉 {out_cmd}")
    print(f"   👉 {doc_file}")
    if (out_dir / ".env.enc").exists():
        print(f"   👉 {out_dir / '.env.enc'}")
        if user_pass:
            print(f"   🔑 Mật khẩu gửi riêng cho tester: {user_pass}")
    print("=" * 65)


if __name__ == "__main__":
    main()
