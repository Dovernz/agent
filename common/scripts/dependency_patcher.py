#!/usr/bin/env python3
"""
dependency_patcher.py
Automated Security & Outdated Dependency Patcher for Antigravity Agent Hub
Scans requirements.txt and package.json to identify vulnerable or outdated libraries,
proposing and applying safe version bumps (patch/minor) directly.
"""

import os
import sys
import json
import re
import argparse
from pathlib import Path

# Ensure UTF-8 standard IO for Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Known minimum recommended safe versions for common vulnerable packages
KNOWN_SAFE_VERSIONS = {
    # Python
    "urllib3": ">=2.2.2",
    "requests": ">=2.32.0",
    "jinja2": ">=3.1.4",
    "django": ">=4.2.16",
    "cryptography": ">=43.0.1",
    "tornado": ">=6.4.1",
    "gunicorn": ">=22.0.0",
    "aiohttp": ">=3.10.2",
    "werkzeug": ">=3.0.3",
    "sqlparse": ">=0.5.0",
    "pillow": ">=10.3.0",
    # Node
    "axios": ">=1.7.4",
    "express": ">=4.20.0",
    "jsonwebtoken": ">=9.0.0",
    "tar": ">=6.2.1",
    "semver": ">=7.5.4",
    "micromatch": ">=4.0.8",
    "ws": ">=8.17.1",
    "braces": ">=3.0.3"
}

def scan_python_requirements(req_path, apply_patch=False):
    updates = []
    if not os.path.exists(req_path):
        return updates
        
    try:
        with open(req_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        new_lines = []
        for line in lines:
            stripped = line.strip()
            if not stripped or stripped.startswith('#'):
                new_lines.append(line)
                continue
                
            match = re.match(r'^([a-zA-Z0-9_\-]+)\s*([=><~^!]+.*)?$', stripped)
            if match:
                pkg = match.group(1).lower()
                current_ver = match.group(2) or "unpinned"
                
                if pkg in KNOWN_SAFE_VERSIONS:
                    safe_spec = KNOWN_SAFE_VERSIONS[pkg]
                    # Check if currently lower than safe spec
                    clean_safe = safe_spec.replace('>=', '').strip()
                    if current_ver != "unpinned" and any(op in current_ver for op in ['==', '<=']):
                        curr_num = re.sub(r'[^0-9.]', '', current_ver)
                        if curr_num and curr_num < clean_safe:
                            updates.append({
                                "package": pkg,
                                "current": current_ver,
                                "recommended": f">={clean_safe}",
                                "file": req_path
                            })
                            if apply_patch:
                                new_lines.append(f"{match.group(1)}>={clean_safe}\n")
                                continue
            new_lines.append(line)
            
        if apply_patch and updates:
            with open(req_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
    except Exception as e:
        print(f"[!] Lỗi phân tích {req_path}: {e}", file=sys.stderr)
        
    return updates

def scan_node_package_json(pkg_path, apply_patch=False):
    updates = []
    if not os.path.exists(pkg_path):
        return updates
        
    try:
        with open(pkg_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        changed = False
        for dep_type in ["dependencies", "devDependencies"]:
            deps = data.get(dep_type, {})
            for pkg, ver in list(deps.items()):
                pkg_lower = pkg.lower()
                if pkg_lower in KNOWN_SAFE_VERSIONS:
                    safe_spec = KNOWN_SAFE_VERSIONS[pkg_lower]
                    clean_safe = safe_spec.replace('>=', '').strip()
                    ver_num = re.sub(r'[^0-9.]', '', ver)
                    if ver_num and ver_num < clean_safe:
                        updates.append({
                            "package": pkg,
                            "current": ver,
                            "recommended": f"^{clean_safe}",
                            "file": pkg_path
                        })
                        if apply_patch:
                            deps[pkg] = f"^{clean_safe}"
                            changed = True
                            
        if apply_patch and changed:
            with open(pkg_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"[!] Lỗi phân tích {pkg_path}: {e}", file=sys.stderr)
        
    return updates

def scan_directory(target_dir, apply_patch=False):
    target_dir = os.path.abspath(target_dir)
    print(f"[*] Đang quét lỗ hổng & phiên bản phụ thuộc tại: {target_dir}")
    all_updates = []
    
    for root, dirs, files in os.walk(target_dir):
        dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', '.venv', 'venv', '__pycache__']]
        for file in files:
            full_p = os.path.join(root, file)
            if file == "requirements.txt":
                all_updates.extend(scan_python_requirements(full_p, apply_patch))
            elif file == "package.json":
                all_updates.extend(scan_node_package_json(full_p, apply_patch))
                
    return all_updates

def main():
    parser = argparse.ArgumentParser(description="Scan and safely patch vulnerable/outdated dependencies")
    parser.add_argument("target_path", nargs="?", default=".", help="Đường dẫn thư mục dự án cần quét")
    parser.add_argument("--patch", action="store_true", help="Tự động vá (nâng cấp) phiên bản an toàn vào tệp cấu hình")
    args = parser.parse_args()
    
    updates = scan_directory(args.target_path, apply_patch=args.patch)
    
    print("\n" + "="*60)
    print("🛡️ BÁO CÁO KIỂM TRA PHỤ THUỘC (DEPENDENCY PATCHER)")
    print("="*60)
    
    if not updates:
        print("[✓] TOÀN BỘ PHỤ THUỘC ĐÃ Ở PHIÊN BẢN AN TOÀN! Không phát hiện thư viện cần vá khẩn cấp.")
        sys.exit(0)
        
    print(f"[!] Phát hiện {len(updates)} thư viện cần nâng cấp phiên bản an toàn:")
    for u in updates:
        rel_f = os.path.relpath(u["file"], args.target_path)
        print(f"  📦 {u['package']:<15}: {u['current']} ➡️  {u['recommended']} (tại `{rel_f}`)")
        
    if args.patch:
        print(f"\n[✓] ĐÃ TỰ ĐỘNG VÁ THÀNH CÔNG {len(updates)} THƯ VIỆN VÀO TỆP CẤU HÌNH!")
    else:
        print("\n💡 GỢI Ý: Chạy lại lệnh với cờ `--patch` để tự động nâng cấp phiên bản an toàn:")
        print(f"   uv run python \"D:\\Thành\\Agent\\common\\scripts\\dependency_patcher.py\" \"{args.target_path}\" --patch")

if __name__ == "__main__":
    main()
