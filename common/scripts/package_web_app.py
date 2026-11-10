#!/usr/bin/env python3
r"""
package_web_app.py - Universal Web App Packager & Key Locker
Đóng gói bất kỳ dự án web nào (Translate, Dental, Next.js, Django, FastAPI)
thành 1 tệp CMD cài đặt độc lập (Zero-Dependency) đưa cho người dùng test:
  1. Không yêu cầu cài Docker, Git, hay Python lên máy User.
  2. Tự động tải Python Portable (Embed) và giải nén GitHub Zip nếu máy trắng.
  3. Cơ chế Lock Key kép (Dual-Slot AES-256-CBC) bảo vệ API Key / Secrets.
  4. Tự động tạo Shortcut Desktop, map Domain Local (.local) và chạy ẩn ngầm.
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def encrypt_dual_slot_powershell(in_env_file: Path, out_enc_file: Path, master_pass: str, user_pass: str) -> bool:
    """Mã hóa payload .env bằng PowerShell built-in chuẩn GEMINI_DUAL_V1 (Không cần cài thư viện ngoài)."""
    ps_script = f"""
$ErrorActionPreference = 'Stop'
$plain = [System.IO.File]::ReadAllBytes('{str(in_env_file)}')

$rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
$dataKey = New-Object byte[](32); $rng.GetBytes($dataKey)
$dataIV = New-Object byte[](16); $rng.GetBytes($dataIV)

$aesData = [System.Security.Cryptography.Aes]::Create()
$aesData.KeySize = 256; $aesData.BlockSize = 128
$aesData.Mode = [System.Security.Cryptography.CipherMode]::CBC
$aesData.Padding = [System.Security.Cryptography.PaddingMode]::PKCS7
$aesData.Key = $dataKey; $aesData.IV = $dataIV
$cipherPayload = $aesData.CreateEncryptor().TransformFinalBlock($plain, 0, $plain.Length)

# Master Slot
$saltM = New-Object byte[](16); $rng.GetBytes($saltM)
$kdfM = New-Object System.Security.Cryptography.Rfc2898DeriveBytes('{master_pass}', $saltM, 50000, [System.Security.Cryptography.HashAlgorithmName]::SHA256)
$aesM = [System.Security.Cryptography.Aes]::Create()
$aesM.Key = $kdfM.GetBytes(32); $aesM.IV = $kdfM.GetBytes(16)
$cipherKeyM = $aesM.CreateEncryptor().TransformFinalBlock($dataKey, 0, $dataKey.Length)

# User Slot
$saltU = New-Object byte[](16); $rng.GetBytes($saltU)
$kdfU = New-Object System.Security.Cryptography.Rfc2898DeriveBytes('{user_pass}', $saltU, 50000, [System.Security.Cryptography.HashAlgorithmName]::SHA256)
$aesU = [System.Security.Cryptography.Aes]::Create()
$aesU.Key = $kdfU.GetBytes(32); $aesU.IV = $kdfU.GetBytes(16)
$cipherKeyU = $aesU.CreateEncryptor().TransformFinalBlock($dataKey, 0, $dataKey.Length)

# File Pack
$magic = [System.Text.Encoding]::ASCII.GetBytes('GEMINI_DUAL_V1')
$fs = [System.IO.File]::Create('{str(out_enc_file)}')
$fs.Write($magic, 0, $magic.Length)
$fs.Write($saltM, 0, $saltM.Length)
$fs.Write($cipherKeyM, 0, $cipherKeyM.Length)
$fs.Write($saltU, 0, $saltU.Length)
$fs.Write($cipherKeyU, 0, $cipherKeyU.Length)
$fs.Write($dataIV, 0, $dataIV.Length)
$fs.Write($cipherPayload, 0, $cipherPayload.Length)
$fs.Close()
Write-Output 'DUAL_ENCRYPTION_OK'
"""
    try:
        res = subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
            capture_output=True,
            text=True,
            timeout=10,
        )
        return "DUAL_ENCRYPTION_OK" in res.stdout
    except Exception as e:
        print(f"[!] Lỗi khi mã hóa qua PowerShell: {e}")
        return False


def generate_cmd_launcher(
    app_title: str,
    repo_url: str,
    repo_zip_url: str,
    zip_subfolder: str,
    run_command_powershell: str,
    port: int,
    domain: str,
    use_portproxy: bool = True,
) -> str:
    """Sinh nội dung file .cmd cài đặt & khởi chạy độc lập (Zero-Dependency)."""

    domain_check = ""
    domain_cleanup = ""
    if domain:
        domain_check = f"""findstr /C:"{domain}" "%HOSTS_FILE%" >nul 2>&1
if !errorlevel! neq 0 set "NEED_HOSTS=1"
"""
        domain_cleanup = f"""powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process cmd -ArgumentList '/c (powershell -Command \"\"(Get-Content -Path $env:windir\\System32\\drivers\\etc\\hosts) | Where-Object {{ $_ -notmatch ''{domain}'' }} | Set-Content -Path $env:windir\\System32\\drivers\\etc\\hosts\"\" ) & (netsh interface portproxy delete v4tov4 listenport=80 listenaddress=127.0.0.1 >nul 2>&1)' -Verb RunAs -Wait" >nul 2>&1
"""

    proxy_check = ""
    proxy_cmd = ""
    if use_portproxy and domain:
        proxy_check = f"""netsh interface portproxy show v4tov4 | findstr "80" | findstr "{port}" >nul 2>&1
if !errorlevel! neq 0 set "NEED_PROXY=1"
"""
        proxy_cmd = f"& (netsh interface portproxy add v4tov4 listenport=80 listenaddress=127.0.0.1 connectport={port} connectaddress=127.0.0.1 >nul 2>&1)"

    url_to_open = f"http://{domain}" if domain else f"http://localhost:{port}"

    cmd_template = f"""@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
title {app_title}

set "CURRENT_DIR=%~dp0"
if "%CURRENT_DIR:~-1%"=="\\" set "CURRENT_DIR=%CURRENT_DIR:~0,-1%"
set "CONFIG_PATH_FILE=%CURRENT_DIR%\\.install_path"

set "APP_DIR="
if exist "%CONFIG_PATH_FILE%" (
    set /p "APP_DIR="<"%CONFIG_PATH_FILE%"
)
if "!APP_DIR!"=="" (
    if exist "%CURRENT_DIR%\\app.py" (
        set "APP_DIR=%CURRENT_DIR%"
    ) else if exist "%CURRENT_DIR%\\manage.py" (
        set "APP_DIR=%CURRENT_DIR%"
    ) else if exist "%USERPROFILE%\\{app_title}\\app.py" (
        set "APP_DIR=%USERPROFILE%\\{app_title}"
    ) else if exist "%USERPROFILE%\\{app_title}\\manage.py" (
        set "APP_DIR=%USERPROFILE%\\{app_title}"
    ) else (
        set "APP_DIR=%CURRENT_DIR%"
    )
)

set "REPO_URL={repo_url}"
set "REPO_ZIP_URL={repo_zip_url}"
set "ZIP_SUBFOLDER={zip_subfolder}"
set "PY_EMBED_URL=https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-amd64.zip"
set "GET_PIP_URL=https://bootstrap.pypa.io/get-pip.py"
set "HOSTS_FILE=%windir%\\System32\\drivers\\etc\\hosts"
set "APP_PORT={port}"
set "APP_URL={url_to_open}"

if not "%~1"=="" (
    set "choice=%~1"
    goto DISPATCH
)

:MENU
set "choice="
cls
call :CHECK_STATUS_INTERNAL
if "!IS_RUNNING!"=="1" (set "SERVER_STATUS=ĐANG CHẠY") else (set "SERVER_STATUS=ĐÃ TẮT")

echo =====================================================================
echo     {app_title.upper()}
echo     Trạng thái: [!SERVER_STATUS!]
echo =====================================================================
echo   [1] Bật ứng dụng (Start Web)
echo   [2] Tắt ứng dụng (Stop Web)
echo   [3] Cài đặt / Khởi tạo môi trường (Install)
echo   [4] Cập nhật mã nguồn mới nhất (Update)
echo   [5] Xóa cài đặt hoàn toàn (Uninstall)
echo   [0] Thoát
echo =====================================================================
set /p "choice=Nhập lựa chọn (0-5): "

:DISPATCH
if "%choice%"=="1" goto START_APP
if "%choice%"=="2" goto STOP_APP
if "%choice%"=="3" goto INSTALL_APP
if "%choice%"=="4" goto UPDATE_APP
if "%choice%"=="5" goto UNINSTALL_APP
if "%choice%"=="0" exit /b 0
goto MENU

:ENSURE_NETWORK_CONFIG
set "NEED_HOSTS=0"
set "NEED_PROXY=0"
{domain_check}
{proxy_check}

set "DO_ELEVATE=0"
if "!NEED_HOSTS!"=="1" set "DO_ELEVATE=1"
if "!NEED_PROXY!"=="1" set "DO_ELEVATE=1"

if "!DO_ELEVATE!"=="1" (
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process cmd -ArgumentList '/c (findstr /C:\"{domain}\" \"%HOSTS_FILE%\" >nul 2>&1 || echo 127.0.0.1 {domain} >> \"%HOSTS_FILE%\") {proxy_cmd}' -Verb RunAs -Wait"
    ping -n 2 127.0.0.1 >nul
)
exit /b 0

:FIND_PYTHON
set "PY_RUN="
if exist "!APP_DIR!\\runtime\\python.exe" (
    set "PY_RUN=!APP_DIR!\\runtime\\python.exe"
    exit /b 0
)
if exist "!APP_DIR!\\venv\\Scripts\\python.exe" (
    set "PY_RUN=!APP_DIR!\\venv\\Scripts\\python.exe"
    exit /b 0
)
if exist "!APP_DIR!\\.venv\\Scripts\\python.exe" (
    set "PY_RUN=!APP_DIR!\\.venv\\Scripts\\python.exe"
    exit /b 0
)
where python >nul 2>&1
if !errorlevel! equ 0 (
    set "PY_RUN=python"
    exit /b 0
)
exit /b 0

:START_APP
call :CHECK_STATUS_INTERNAL
if "!IS_RUNNING!"=="1" (
    start "" !APP_URL!
    if not "%~1"=="" exit /b 0
    goto MENU
)

call :ENSURE_NETWORK_CONFIG

if not exist "!APP_DIR!" (
    echo Chưa tìm thấy thư mục ứng dụng. Vui lòng chọn [3] để cài đặt.
    pause
    goto MENU
)

cd /d "!APP_DIR!"

if exist "docker-compose.yml" (
    docker --version >nul 2>&1
    if !errorlevel! equ 0 (
        docker compose up -d
        goto WAIT_READY
    )
)

call :FIND_PYTHON
if "!PY_RUN!"=="" (
    echo Không tìm thấy Python. Vui lòng chọn [3] để tự động thiết lập Python Portable.
    pause
    goto MENU
)

start /b "" powershell -NoProfile -WindowStyle Hidden -Command "{run_command_powershell}"

:WAIT_READY
for /l %%i in (1,1,12) do (
    netstat -ano | findstr /R ":!APP_PORT! .*LISTENING" >nul 2>&1
    if !errorlevel! equ 0 (
        start "" !APP_URL!
        if not "%~1"=="" exit /b 0
        goto MENU
    )
    ping -n 2 127.0.0.1 >nul
)

start "" !APP_URL!
if not "%~1"=="" exit /b 0
goto MENU

:STOP_APP
cd /d "!APP_DIR!" 2>nul
if exist "docker-compose.yml" (
    docker compose stop >nul 2>&1
)

for /f "tokens=5" %%a in ('netstat -ano ^| findstr /R ":!APP_PORT! .*LISTENING"') do (
    taskkill /f /pid %%a >nul 2>&1
)

ping -n 2 127.0.0.1 >nul
echo Đã tắt dịch vụ thành công.
if not "%~1"=="" exit /b 0
ping -n 2 127.0.0.1 >nul
goto MENU

:INSTALL_APP
cls
echo =====================================================================
echo                     CÀI ĐẶT {app_title.upper()}
echo =====================================================================
echo Chọn thư mục cài đặt:
echo   [1] Thư mục hiện tại: !CURRENT_DIR!
echo   [2] Nhập đường dẫn tùy chọn (dán path)
echo =====================================================================
set "DIR_CHOICE=1"
set /p "DIR_CHOICE=Nhập lựa chọn (1/2, Mặc định 1): "

if "!DIR_CHOICE!"=="2" (
    set /p "CUSTOM_DIR=Nhập đường dẫn thư mục muốn lưu: "
    set "CUSTOM_DIR=!CUSTOM_DIR:"=!"
    if not "!CUSTOM_DIR!"=="" (
        set "APP_DIR=!CUSTOM_DIR!"
    )
) else (
    set "APP_DIR=!CURRENT_DIR!"
)

echo !APP_DIR!>"%CONFIG_PATH_FILE%"
echo Thư mục cài đặt: !APP_DIR!
echo.

if not exist "!APP_DIR!" mkdir "!APP_DIR!"
cd /d "!APP_DIR!"

set "USE_GIT=0"
where git >nul 2>&1
if !errorlevel! equ 0 set "USE_GIT=1"

if "!USE_GIT!"=="1" (
    if not exist ".git" (
        if not "!REPO_URL!"=="" (
            echo Đang tải mã nguồn từ GitHub...
            git clone "!REPO_URL!" .
        )
    )
) else (
    if not "!REPO_ZIP_URL!"=="" (
        echo Đang tải mã nguồn gói Zip từ máy chủ...
        set "TEMP_ZIP=%TEMP%\\app_pkg_%RANDOM%.zip"
        set "TEMP_EXTRACT=%TEMP%\\app_ext_%RANDOM%"
        powershell -NoProfile -ExecutionPolicy Bypass -Command "[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.SecurityProtocolType]::Tls12; (New-Object System.Net.WebClient).DownloadFile('!REPO_ZIP_URL!', '!TEMP_ZIP!'); Expand-Archive -Path '!TEMP_ZIP!' -DestinationPath '!TEMP_EXTRACT!' -Force; Copy-Item -Path '!TEMP_EXTRACT!\\!ZIP_SUBFOLDER!\\*' -Destination '!APP_DIR!' -Recurse -Force; Remove-Item -Path '!TEMP_EXTRACT!' -Recurse -Force; Remove-Item -Path '!TEMP_ZIP!' -Force"
    )
)

set "SYSTEM_PYTHON=0"
where python >nul 2>&1
if !errorlevel! equ 0 set "SYSTEM_PYTHON=1"

if "!SYSTEM_PYTHON!"=="1" (
    echo Đang khởi tạo môi trường Python Virtual Environment...
    if not exist "venv\\Scripts\\python.exe" (
        python -m venv venv
    )
    call venv\\Scripts\\activate.bat
    python -m pip install --upgrade pip >nul 2>&1
    if exist "requirements.txt" (
        echo Đang cài đặt thư viện phụ thuộc...
        python -m pip install -r requirements.txt
    )
    set "PY_RUN=!APP_DIR!\\venv\\Scripts\\python.exe"
) else (
    echo Đang cài đặt môi trường Python Portable (Standalone, 0% rác hệ thống)...
    if not exist "!APP_DIR!\\runtime" mkdir "!APP_DIR!\\runtime"
    if not exist "!APP_DIR!\\runtime\\python.exe" (
        set "PY_ZIP=%TEMP%\\py_embed_%RANDOM%.zip"
        powershell -NoProfile -ExecutionPolicy Bypass -Command "[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.SecurityProtocolType]::Tls12; (New-Object System.Net.WebClient).DownloadFile('!PY_EMBED_URL!', '!PY_ZIP!'); Expand-Archive -Path '!PY_ZIP!' -DestinationPath '!APP_DIR!\\runtime' -Force; Remove-Item -Path '!PY_ZIP!' -Force"
        powershell -NoProfile -ExecutionPolicy Bypass -Command "Get-ChildItem -Path '!APP_DIR!\\runtime' -Filter '*._pth' | ForEach-Object {{ $c = Get-Content $_.FullName; $c = $c -replace '#import site', 'import site'; Set-Content -Path $_.FullName -Value $c }}"
        set "GET_PIP_FILE=!APP_DIR!\\runtime\\get-pip.py"
        powershell -NoProfile -ExecutionPolicy Bypass -Command "[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.SecurityProtocolType]::Tls12; (New-Object System.Net.WebClient).DownloadFile('!GET_PIP_URL!', '!GET_PIP_FILE!')"
        "!APP_DIR!\\runtime\\python.exe" "!GET_PIP_FILE!" --no-warn-script-location >nul 2>&1
        del /f /q "!GET_PIP_FILE!" >nul 2>&1
    )
    echo Đang cài đặt thư viện phụ thuộc...
    "!APP_DIR!\\runtime\\python.exe" -m pip install --upgrade pip >nul 2>&1
    if exist "requirements.txt" "!APP_DIR!\\runtime\\python.exe" -m pip install -r requirements.txt
    set "PY_RUN=!APP_DIR!\\runtime\\python.exe"
)

call :ENSURE_ENV_CONFIG
call :ENSURE_NETWORK_CONFIG

echo Đang tạo phím tắt tiện lợi trên Desktop...
powershell -NoProfile -ExecutionPolicy Bypass -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut([System.IO.Path]::Combine([Environment]::GetFolderPath('Desktop'), '{app_title}.lnk')); $s.TargetPath = '%~f0'; $s.Arguments = '1'; $s.WorkingDirectory = '%~dp0'; $s.Save()" >nul 2>&1

echo =====================================================================
echo Cài đặt hoàn tất! Bạn có thể bật ứng dụng ngay bây giờ.
echo =====================================================================
pause
goto MENU

:ENSURE_ENV_CONFIG
if exist ".env" exit /b 0
if exist "%CURRENT_DIR%\\.env" (
    copy "%CURRENT_DIR%\\.env" .env >nul
    exit /b 0
)

if exist "!APP_DIR!\\.env.enc" (
    echo =====================================================================
    echo Ứng dụng đã được khóa key bảo mật. Vui lòng nhập mật khẩu được cấp:
    set /p "USER_PASS=Nhập mật khẩu: "
    powershell -NoProfile -ExecutionPolicy Bypass -Command "$p = '!USER_PASS!'; $f = '!APP_DIR!\\.env.enc'; $out = '!APP_DIR!\\.env'; try {{ $b = [System.IO.File]::ReadAllBytes($f); $m = [System.Text.Encoding]::ASCII.GetString($b, 0, 14); if ($m -eq 'GEMINI_DUAL_V1') {{ $sM = New-Object byte[](16); [System.Array]::Copy($b, 14, $sM, 0, 16); $ckM = New-Object byte[](48); [System.Array]::Copy($b, 30, $ckM, 0, 48); $sU = New-Object byte[](16); [System.Array]::Copy($b, 78, $sU, 0, 16); $ckU = New-Object byte[](48); [System.Array]::Copy($b, 94, $ckU, 0, 48); $dIV = New-Object byte[](16); [System.Array]::Copy($b, 142, $dIV, 0, 16); $pL = $b.Length - 158; $pD = New-Object byte[]($pL); [System.Array]::Copy($b, 158, $pD, 0, $pL); $dk = $null; try {{ $k = New-Object System.Security.Cryptography.Rfc2898DeriveBytes($p, $sM, 50000, [System.Security.Cryptography.HashAlgorithmName]::SHA256); $a = [System.Security.Cryptography.Aes]::Create(); $a.Key = $k.GetBytes(32); $a.IV = $k.GetBytes(16); $c = $a.CreateDecryptor().TransformFinalBlock($ckM, 0, 48); if ($c.Length -eq 32) {{ $dk = $c }} }} catch {{}}; if ($dk -eq $null) {{ try {{ $k = New-Object System.Security.Cryptography.Rfc2898DeriveBytes($p, $sU, 50000, [System.Security.Cryptography.HashAlgorithmName]::SHA256); $a = [System.Security.Cryptography.Aes]::Create(); $a.Key = $k.GetBytes(32); $a.IV = $k.GetBytes(16); $c = $a.CreateDecryptor().TransformFinalBlock($ckU, 0, 48); if ($c.Length -eq 32) {{ $dk = $c }} }} catch {{}} }}; if ($dk -eq $null) {{ throw 'Err' }}; $af = [System.Security.Cryptography.Aes]::Create(); $af.Key = $dk; $af.IV = $dIV; $dec = $af.CreateDecryptor().TransformFinalBlock($pD, 0, $pL); [System.IO.File]::WriteAllBytes($out, $dec); Write-Host 'Mở khóa thành công.' -ForegroundColor Green }} }} catch {{ Write-Host 'Mật khẩu mở khóa không chính xác.' -ForegroundColor Red }}"
)

if not exist ".env" (
    if exist ".env.example" copy .env.example .env >nul
)
exit /b 0

:UPDATE_APP
cls
echo =====================================================================
echo                      CẬP NHẬT MÃ NGUỒN
echo =====================================================================
cd /d "!APP_DIR!"

if exist ".env" copy /y ".env" "%TEMP%\\app_env_backup.env" >nul

set "USE_GIT=0"
where git >nul 2>&1
if !errorlevel! equ 0 (
    if exist ".git" set "USE_GIT=1"
)

if "!USE_GIT!"=="1" (
    echo Đang kéo bản cập nhật mới nhất từ Git...
    git pull origin main
) else (
    if not "!REPO_ZIP_URL!"=="" (
        echo Đang tải bản cập nhật mới nhất...
        set "TEMP_ZIP=%TEMP%\\app_upd_%RANDOM%.zip"
        set "TEMP_EXTRACT=%TEMP%\\app_ext_%RANDOM%"
        powershell -NoProfile -ExecutionPolicy Bypass -Command "[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.SecurityProtocolType]::Tls12; (New-Object System.Net.WebClient).DownloadFile('!REPO_ZIP_URL!', '!TEMP_ZIP!'); Expand-Archive -Path '!TEMP_ZIP!' -DestinationPath '!TEMP_EXTRACT!' -Force; Copy-Item -Path '!TEMP_EXTRACT!\\!ZIP_SUBFOLDER!\\*' -Destination '!APP_DIR!' -Recurse -Force; Remove-Item -Path '!TEMP_EXTRACT!' -Recurse -Force; Remove-Item -Path '!TEMP_ZIP!' -Force"
    )
)

if exist "%TEMP%\\app_env_backup.env" (
    copy /y "%TEMP%\\app_env_backup.env" ".env" >nul
    del /f /q "%TEMP%\\app_env_backup.env" >nul
)

call :FIND_PYTHON
if not "!PY_RUN!"=="" (
    if exist "requirements.txt" "!PY_RUN!" -m pip install -r requirements.txt
)

echo Cập nhật hoàn tất.
pause
goto MENU

:UNINSTALL_APP
cls
echo =====================================================================
echo                       GỠ BỎ CÀI ĐẶT
echo =====================================================================
echo Thao tác này sẽ xóa ứng dụng khỏi máy tính: !APP_DIR!
set /p "confirm=Xác nhận xóa? (Y/N): "
if /i not "!confirm!"=="Y" goto MENU

call :STOP_APP >nul 2>&1

if exist "!APP_DIR!" (
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Remove-Item -Path '!APP_DIR!' -Recurse -Force -ErrorAction SilentlyContinue" >nul 2>&1
)

if exist "%CONFIG_PATH_FILE%" del /f /q "%CONFIG_PATH_FILE%" >nul 2>&1
set "DESKTOP_LNK=%USERPROFILE%\\Desktop\\{app_title}.lnk"
if exist "!DESKTOP_LNK!" del /f /q "!DESKTOP_LNK!" >nul 2>&1
{domain_cleanup}

echo Đã gỡ bỏ ứng dụng thành công.
pause
goto MENU

:CHECK_STATUS_INTERNAL
netstat -ano | findstr /R ":!APP_PORT! .*LISTENING" >nul 2>&1
if !errorlevel! equ 0 (set "IS_RUNNING=1") else (set "IS_RUNNING=0")
exit /b 0
"""
    return cmd_template


def main():
    parser = argparse.ArgumentParser(
        description="Universal Web App Packager & Key Locker"
    )
    parser.add_argument("--name", required=True, help="Tên ứng dụng (vd: GeminiTrans, MinhSinhDental)")
    parser.add_argument("--app-dir", required=True, help="Thư mục mã nguồn của dự án")
    parser.add_argument("--out-dir", required=True, help="Thư mục xuất file cài đặt cho User")
    parser.add_argument("--port", type=int, default=8000, help="Cổng Web của ứng dụng (mặc định 8000)")
    parser.add_argument("--domain", default="", help="Tên miền cục bộ tùy chọn (vd: dental.local)")
    parser.add_argument("--repo-url", default="", help="Git repo clone URL")
    parser.add_argument("--repo-zip", default="", help="GitHub zip archive URL")
    parser.add_argument("--zip-folder", default="*-main", help="Tên thư mục sau khi giải nén zip")
    parser.add_argument("--run-cmd", default="", help="Lệnh PowerShell khởi chạy backend (mặc định tự dò uvicorn hoặc django)")
    parser.add_argument("--env-file", default="", help="Đường dẫn file .env chứa key cần khóa")
    parser.add_argument("--master-pass", default="admin1303", help="Mật khẩu Master/Admin")
    parser.add_argument("--user-pass", default="ctt1303", help="Mật khẩu cấp cho Tester/User")

    args = parser.parse_args()

    app_dir = Path(args.app_dir).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 65)
    print(f"📦 ĐÓNG GÓI ỨNG DỤNG CHO USER TEST: {args.name}")
    print("=" * 65)

    # 1. Tự động xác định Run Command nếu chưa chỉ định
    run_cmd = args.run_cmd
    if not run_cmd:
        if (app_dir / "app.py").exists():
            run_cmd = f"Set-Location '!APP_DIR!'; & '!PY_RUN!' -m uvicorn app:app --host 0.0.0.0 --port {args.port}"
        elif (app_dir / "manage.py").exists():
            run_cmd = f"Set-Location '!APP_DIR!'; & '!PY_RUN!' manage.py runserver 0.0.0.0:{args.port}"
        elif (app_dir / "main.py").exists():
            run_cmd = f"Set-Location '!APP_DIR!'; & '!PY_RUN!' main.py"
        else:
            run_cmd = f"Set-Location '!APP_DIR!'; & '!PY_RUN!' -m http.server {args.port}"

    # 2. Khóa Key (Dual-Slot Encryption) nếu có env file
    env_source = Path(args.env_file).resolve() if args.env_file else (app_dir / ".env")
    if env_source.exists():
        print(f"[+] Tìm thấy file cấu hình nhạy cảm: {env_source}")
        out_enc = out_dir / ".env.enc"
        ok = encrypt_dual_slot_powershell(env_source, out_enc, args.master_pass, args.user_pass)
        if ok:
            print(f"[✓] Đã khóa mã hóa Key thành công: {out_enc}")
            print(f"    • Master Password : {args.master_pass}")
            print(f"    • User Test Pass  : {args.user_pass}")
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
        run_command_powershell=run_cmd,
        port=args.port,
        domain=args.domain,
        use_portproxy=bool(args.domain),
    )

    cmd_file_name = f"{args.name}.cmd"
    out_cmd = out_dir / cmd_file_name
    with open(out_cmd, "w", encoding="utf-8") as cf:
        cf.write(cmd_content)

    print(f"[✓] Đã sinh file cài đặt Standalone 1-Click: {out_cmd}")
    print(f"\n🎯 HOÀN TẤT ĐÓNG GÓI! Bạn chỉ cần gửi thư mục hoặc file CMD cho User:")
    print(f"   👉 {out_cmd}")
    if (out_dir / ".env.enc").exists():
        print(f"   👉 {out_dir / '.env.enc'}")
        print(f"   🔑 Mật khẩu cấp cho tester: {args.user_pass}")
    print("=" * 65)


if __name__ == "__main__":
    main()
