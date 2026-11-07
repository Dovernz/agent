#!/usr/bin/env python3
"""
hub_cleaner.py
Automated Workspace Janitor & Clutter Cleanup Engine for Antigravity Agent Hub
Scans codebases and agent projects to purge one-off scratch scripts, debug scripts,
and stray screenshot images (*.png, *.jpg) generated during Playwright/E2E test runs.
"""

import os
import sys
import glob
import argparse
from pathlib import Path

# Ensure UTF-8 standard IO for Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

TEMP_SCRIPT_PATTERNS = [
    "tmp_*.py", "temp_*.py", "scratch_*.py", "debug_*.py",
    "qa_inspect*.py", "test_temp_*.py", "test_scratch_*.py",
    "quick_*.py", "inspect_*.py"
]

TEMP_IMAGE_EXTENSIONS = [".png", ".jpg", ".jpeg", ".webp"]
TEMP_CACHE_PATTERNS = ["*.log", ".coverage", "dump.rdb"]

def is_protected_file(file_path):
    """Check if file should never be deleted."""
    p_norm = os.path.normpath(file_path).lower()
    # Protect assets in brain, documentation, templates, or skills
    if "brain" in p_norm: return True
    if any(k in p_norm for k in ["docs", "assets", "static", "public", "images", "img", "media"]): return True
    if "template" in p_norm: return True
    if ".git" in p_norm or "node_modules" in p_norm or ".venv" in p_norm: return True
    if "test_suite.py" in p_norm or "baseline_test.py" in p_norm: return True
    return False

def scan_clutter(target_dir):
    target_dir = os.path.abspath(target_dir)
    trash_items = []
    
    for root, dirs, files in os.walk(target_dir):
        # Skip protected / large dirs
        dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', '.venv', 'venv', 'docs', 'assets', 'static', 'public', 'images', 'media']]
        
        for file in files:
            file_path = os.path.join(root, file)
            if is_protected_file(file_path):
                continue
                
            f_lower = file.lower()
            
            # 1. Scratch scripts
            for pattern in TEMP_SCRIPT_PATTERNS:
                if glob.fnmatch.fnmatch(f_lower, pattern):
                    trash_items.append((file_path, "One-off Scratch/Debug Script"))
                    break
                    
            # 2. Stray screenshots in code or test dirs
            if any(f_lower.endswith(ext) for ext in TEMP_IMAGE_EXTENSIONS):
                trash_items.append((file_path, "Stray Screenshot (Playwright/QA)"))
                
            # 3. Temp logs & cache files
            for pattern in TEMP_CACHE_PATTERNS:
                if glob.fnmatch.fnmatch(f_lower, pattern):
                    trash_items.append((file_path, "Temporary Log/Cache"))
                    break
                    
    return trash_items

def main():
    parser = argparse.ArgumentParser(description="Clean one-off scratch scripts and stray screenshots")
    parser.add_argument("target_path", nargs="?", default=".", help="Đường dẫn thư mục cần dọn dẹp")
    parser.add_argument("--dry-run", action="store_true", help="Chỉ liệt kê tệp rác, không xóa thực tế")
    parser.add_argument("--clean", action="store_true", help="Xác nhận xóa triệt để các tệp rác")
    
    args = parser.parse_args()
    target_abs = os.path.abspath(args.target_path)
    
    print(f"[*] Đang quét dọn tệp rác & ảnh chụp màn hình tại: {target_abs}")
    trash = scan_clutter(target_abs)
    
    if not trash:
        print("[✓] THƯ MỤC SẠCH SẼ HOÀN TOÀN! Không phát hiện script tạm hay ảnh chụp màn hình vương vãi.")
        sys.exit(0)
        
    print(f"\n[!] Phát hiện {len(trash)} tệp rác/ảnh tạm cần dọn dẹp:")
    for path, reason in trash:
        rel_p = os.path.relpath(path, target_abs)
        print(f"  🗑️  [{reason}] {rel_p}")
        
    if args.clean:
        deleted_count = 0
        for path, _ in trash:
            try:
                os.remove(path)
                deleted_count += 1
            except Exception as e:
                print(f"[-] Không thể xóa {path}: {e}")
        print(f"\n[✓] ĐÃ DỌN SẠCH {deleted_count}/{len(trash)} TỆP RÁC VÀ ẢNH TẠM!")
    else:
        print("\n💡 GỢI Ý: Chạy lại lệnh với cờ `--clean` để xóa sạch toàn bộ các tệp trên:")
        print(f"   uv run python \"D:\\Thành\\Agent\\common\\scripts\\hub_cleaner.py\" \"{target_abs}\" --clean")

if __name__ == "__main__":
    main()
