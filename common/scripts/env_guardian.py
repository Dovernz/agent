#!/usr/bin/env python3
"""
env_guardian.py
Automated Environment & Secret Guardian for Antigravity Agent Hub
Audits .env vs .env.example parity, identifies missing or undeclared keys,
and prevents real secrets and passwords from leaking into Git commits.
"""

import os
import sys
import re
import argparse
from pathlib import Path

# Ensure UTF-8 standard IO for Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

SUSPICIOUS_SECRET_PATTERNS = [
    (r'(?i)(password|passwd|pwd)\s*=\s*[\'"][^\'"]+[\'"]', "Plaintext password"),
    (r'(?i)(secret_key|private_key|jwt_secret)\s*=\s*[\'"][^\'"]+[\'"]', "Hardcoded Secret Key"),
    (r'AIza[0-9A-Za-z-_]{35}', "Google API Key"),
    (r'ghp_[0-9a-zA-Z]{36}', "GitHub Personal Access Token"),
    (r'sk-[a-zA-Z0-9]{48}', "OpenAI API Key"),
]

def parse_env_file(file_path):
    keys = {}
    if not os.path.exists(file_path):
        return keys
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' in line:
                    key, val = line.split('=', 1)
                    keys[key.strip()] = val.strip()
    except Exception as e:
        print(f"[!] Lỗi đọc tệp {file_path}: {e}", file=sys.stderr)
    return keys

def audit_directory(dir_path):
    dir_path = os.path.abspath(dir_path)
    print(f"[*] Đang kiểm toán biến môi trường & bảo mật tại: {dir_path}")
    
    findings = {
        "dir": dir_path,
        "env_example_found": False,
        "env_found": False,
        "missing_keys": [],
        "extra_keys": [],
        "secret_leaks": []
    }
    
    # 1. Look for env files
    example_path = None
    for cand in [".env.example", ".env.sample", "env.example"]:
        p = os.path.join(dir_path, cand)
        if os.path.exists(p):
            example_path = p
            findings["env_example_found"] = True
            break
            
    env_path = os.path.join(dir_path, ".env")
    if os.path.exists(env_path):
        findings["env_found"] = True
        
    example_keys = parse_env_file(example_path) if example_path else {}
    actual_keys = parse_env_file(env_path) if os.path.exists(env_path) else {}
    
    if example_keys and actual_keys:
        for k in example_keys:
            if k not in actual_keys:
                findings["missing_keys"].append(k)
        for k in actual_keys:
            if k not in example_keys:
                findings["extra_keys"].append(k)
                
    # 2. Check for secret leaks in trackable text files (avoid node_modules, .git)
    for root, dirs, files in os.walk(dir_path):
        dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', '.venv', 'venv', '__pycache__', 'dist', 'build']]
        for file in files:
            if file.endswith(('.py', '.js', '.ts', '.jsx', '.tsx', '.json', '.yml', '.yaml', '.md', '.env.example')):
                f_path = os.path.join(root, file)
                try:
                    with open(f_path, 'r', encoding='utf-8', errors='ignore') as f:
                        text = f.read()
                    for pattern, desc in SUSPICIOUS_SECRET_PATTERNS:
                        if re.search(pattern, text):
                            rel_f = os.path.relpath(f_path, dir_path)
                            findings["secret_leaks"].append(f"{rel_f}: {desc}")
                except Exception:
                    pass
                    
    return findings

def print_report(findings):
    print("\n" + "="*60)
    print("🛡️ KẾT QUẢ KIỂM TOÁN BIẾN MÔI TRƯỜNG & BẢO MẬT (ENV GUARDIAN)")
    print("="*60)
    
    print(f"- **Thư mục kiểm tra:** `{findings['dir']}`")
    print(f"- **Tệp .env.example:** {'[✓] Có' if findings['env_example_found'] else '[-] Không tìm thấy'}")
    print(f"- **Tệp .env thực tế:** {'[✓] Có' if findings['env_found'] else '[-] Không tìm thấy'}")
    
    if findings["missing_keys"]:
        print(f"\n[!] CẢNH BÁO: Phát hiện {len(findings['missing_keys'])} biến còn THIẾU trong .env so với .env.example:")
        for k in findings["missing_keys"]:
            print(f"  ❌ Thiếu biến: `{k}`")
    else:
        if findings["env_example_found"] and findings["env_found"]:
            print("\n[✓] Tất cả biến trong .env.example đều đã được cấu hình trong .env.")
            
    if findings["extra_keys"]:
        print(f"\n[i] Thông tin: Có {len(findings['extra_keys'])} biến chỉ có trong .env (chưa cập nhật vào .env.example):")
        for k in findings["extra_keys"][:5]:
            print(f"  ℹ️ Chưa sync: `{k}`")
            
    if findings["secret_leaks"]:
        print(f"\n🚨 NGUY HIỂM: Phát hiện {len(findings['secret_leaks'])} nguy cơ lọt lộ bí mật mã hóa:")
        for leak in findings["secret_leaks"][:10]:
            print(f"  ⚠️ {leak}")
    else:
        print("\n[✓] Không phát hiện API Key hoặc chuỗi bí mật hardcode trong mã nguồn.")
        
    print("="*60)

def main():
    parser = argparse.ArgumentParser(description="Audit environment variables and secret leaks")
    parser.add_argument("target_path", nargs="?", default=".", help="Đường dẫn thư mục dự án cần kiểm toán")
    args = parser.parse_args()
    
    findings = audit_directory(args.target_path)
    print_report(findings)
    
    if findings["secret_leaks"]:
        sys.exit(1)
    sys.exit(0)

if __name__ == "__main__":
    main()
