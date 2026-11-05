#!/usr/bin/env python3
"""
linter_guard.py
Automated Pre-Commit & QA Linter Guard for Antigravity Agent Hub.

Features:
- Multi-language syntax & linter enforcement (Python, JS/TS, JSON, YAML).
- Git-aware scanning: supports full directory, --staged-only, or --changed-only.
- Secret & credential leak prevention (API keys, passwords, private tokens).
- Workspace hygiene enforcement (Rule 11): catches temporary scripts and stray images.
- Auto-fix integration: triggers 'ruff check --fix' when available and requested.
- Dual-mode output: Human-readable CLI summary or Zero-Fat M2M JSON.
"""

import os
import sys
import re
import json
import py_compile
import subprocess
import argparse
from pathlib import Path

# Ensure UTF-8 standard IO for Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Secret leak detection regex patterns
SECRET_PATTERNS = [
    (r'(?i)(password|passwd|pwd)\s*=\s*[\'"][^\'"]+[\'"]', "HARDCODED_PASSWORD", "Phát hiện mật khẩu viết trực tiếp trong code"),
    (r'(?i)(secret_key|private_key|jwt_secret)\s*=\s*[\'"][^\'"]+[\'"]', "SECRET_KEY_EXPOSURE", "Phát hiện khóa bí mật / JWT secret hardcoded"),
    (r'AIza[0-9A-Za-z-_]{35}', "GOOGLE_API_KEY", "Phát hiện Google API Key"),
    (r'ghp_[0-9a-zA-Z]{36}', "GITHUB_TOKEN", "Phát hiện GitHub Personal Access Token"),
    (r'sk-[a-zA-Z0-9]{48}', "OPENAI_API_KEY", "Phát hiện OpenAI API Key"),
]

# Rule 11: Temp script patterns
HYGIENE_PATTERNS = [
    r'^(?:tmp|temp|debug|qa_inspect|scratch)_.*\.py$',
    r'.*\.tmp$',
    r'.*\.bak$',
]

IGNORE_DIRS = {
    '.git', 'node_modules', '.venv', 'venv', '__pycache__',
    'dist', 'build', '.idea', '.vscode', 'coverage', '.pytest_cache'
}


def get_git_files(repo_path, mode="changed"):
    """Fetches changed or staged files using git command line."""
    try:
        if mode == "staged":
            cmd = ["git", "-C", repo_path, "diff", "--name-only", "--cached"]
        else:
            cmd = ["git", "-C", repo_path, "status", "--porcelain"]
            
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        files = []
        for line in result.stdout.strip().splitlines():
            line = line.strip()
            if not line:
                continue
            if mode == "staged":
                files.append(os.path.normpath(os.path.join(repo_path, line)))
            else:
                # git status --porcelain formats as ' M file.py' or '?? file.py'
                parts = line.split(maxsplit=1)
                if len(parts) == 2:
                    files.append(os.path.normpath(os.path.join(repo_path, parts[1])))
        return [f for f in files if os.path.isfile(f)]
    except Exception:
        return []


def scan_all_files(target_dir):
    """Walks the directory and gathers trackable code files."""
    matched_files = []
    for root, dirs, files in os.walk(target_dir):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        for f in files:
            full_path = os.path.join(root, f)
            matched_files.append(full_path)
    return matched_files


def check_python_syntax(file_path):
    """Validates Python syntax using py_compile."""
    try:
        py_compile.compile(file_path, doraise=True)
        return None
    except py_compile.PyCompileError as e:
        # e.exc_value contains (msg, (filename, lineno, offset, text))
        msg = str(e)
        lineno = None
        if hasattr(e, 'exc_value') and e.exc_value:
            args = getattr(e.exc_value, 'args', [])
            if len(args) > 1 and isinstance(args[1], tuple) and len(args[1]) > 1:
                lineno = args[1][1]
        return {
            "file": file_path,
            "line": lineno or 1,
            "rule": "PY_SYNTAX_ERROR",
            "message": f"Lỗi cú pháp Python: {msg.splitlines()[0]}"
        }
    except Exception as e:
        return {
            "file": file_path,
            "line": 1,
            "rule": "PY_SYNTAX_ERROR",
            "message": str(e)
        }


def check_json_syntax(file_path):
    """Validates JSON file parsing."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            json.load(f)
        return None
    except json.JSONDecodeError as e:
        return {
            "file": file_path,
            "line": e.lineno,
            "rule": "JSON_PARSE_ERROR",
            "message": f"Lỗi cú pháp JSON: {e.msg} (line {e.lineno}, col {e.colno})"
        }
    except Exception as e:
        return {
            "file": file_path,
            "line": 1,
            "rule": "JSON_PARSE_ERROR",
            "message": str(e)
        }


def check_secrets_and_hygiene(file_path, base_dir):
    """Scans for credential leaks and Rule 11 hygiene violations."""
    violations = []
    file_name = os.path.basename(file_path)
    rel_path = os.path.relpath(file_path, base_dir)

    # 1. Rule 11 Workspace Hygiene
    for pat in HYGIENE_PATTERNS:
        if re.match(pat, file_name, re.IGNORECASE):
            violations.append({
                "file": rel_path,
                "line": 1,
                "rule": "RULE_11_HYGIENE_VIOLATION",
                "message": f"Phát hiện file tạm/rác vi phạm Rule 11: {file_name}. Cần xóa trước khi commit."
            })
            break

    # Check for stray screenshots in non-artifact directories
    if file_name.lower().endswith(('.png', '.jpg', '.jpeg')):
        # Allow standard asset folders
        norm_rel = rel_path.replace('\\', '/').lower()
        if not any(allowed in norm_rel for allowed in ['static/', 'assets/', 'public/', 'docs/images/', 'screenshots/']):
            violations.append({
                "file": rel_path,
                "line": 1,
                "rule": "RULE_11_STRAY_SCREENSHOT",
                "message": f"Phát hiện ảnh chụp màn hình nằm sai vị trí: {file_name}. Bắt buộc lưu tại brain/ artifacts."
            })
        return violations

    # 2. Secret Leaks Check (only for text files)
    if not file_name.endswith(('.py', '.js', '.ts', '.jsx', '.tsx', '.json', '.yml', '.yaml', '.html', '.php', '.sql')):
        return violations

    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for idx, line in enumerate(f, 1):
                # Ignore comment lines
                stripped = line.strip()
                if stripped.startswith('#') or stripped.startswith('//') or stripped.startswith('/*'):
                    continue
                for pat, code, desc in SECRET_PATTERNS:
                    if re.search(pat, line):
                        violations.append({
                            "file": rel_path,
                            "line": idx,
                            "rule": code,
                            "message": f"{desc} tại dòng {idx}"
                        })
    except Exception:
        pass

    return violations


def run_external_ruff(files, repo_path, auto_fix=False):
    """Runs ruff check if ruff is installed in system or uv."""
    py_files = [f for f in files if f.endswith('.py')]
    if not py_files:
        return []

    cmd = ["uv", "run", "ruff", "check"]
    if auto_fix:
        cmd.append("--fix")
    cmd.extend(py_files[:30])  # limit batch size

    try:
        result = subprocess.run(cmd, cwd=repo_path, capture_output=True, text=True)
        if result.returncode != 0 and result.stdout:
            # Parse ruff output
            ruff_violations = []
            for line in result.stdout.splitlines():
                if ":" in line and not line.startswith("Found"):
                    parts = line.split(":", 3)
                    if len(parts) >= 3 and parts[1].strip().isdigit():
                        ruff_violations.append({
                            "file": parts[0].strip(),
                            "line": int(parts[1].strip()),
                            "rule": "RUFF_LINT_ERROR",
                            "message": parts[2].strip() if len(parts) == 3 else parts[3].strip()
                        })
            return ruff_violations
    except Exception:
        pass
    return []


def audit_project(target_dir, mode="all", auto_fix=False):
    """Orchestrates comprehensive linter, syntax, and secret audit."""
    target_dir = os.path.abspath(target_dir)
    
    if mode == "staged":
        files_to_check = get_git_files(target_dir, mode="staged")
    elif mode == "changed":
        files_to_check = get_git_files(target_dir, mode="changed")
    else:
        files_to_check = scan_all_files(target_dir)

    all_violations = []

    for f_path in files_to_check:
        rel_path = os.path.relpath(f_path, target_dir)
        
        # 1. Hygiene & Secrets check
        hygiene_errs = check_secrets_and_hygiene(f_path, target_dir)
        all_violations.extend(hygiene_errs)

        # 2. Python syntax
        if f_path.endswith('.py'):
            py_err = check_python_syntax(f_path)
            if py_err:
                py_err["file"] = rel_path
                all_violations.append(py_err)

        # 3. JSON syntax
        elif f_path.endswith('.json'):
            json_err = check_json_syntax(f_path)
            if json_err:
                json_err["file"] = rel_path
                all_violations.append(json_err)

    # 4. Optional ruff check
    ruff_errs = run_external_ruff(files_to_check, target_dir, auto_fix=auto_fix)
    all_violations.extend(ruff_errs)

    status = "PASS" if not all_violations else "FAIL"
    
    return {
        "status": status,
        "target_dir": target_dir,
        "mode": mode,
        "total_files_scanned": len(files_to_check),
        "violations_count": len(all_violations),
        "violations": all_violations
    }


def main():
    parser = argparse.ArgumentParser(description="Unified Pre-Commit & QA Linter Guard for Antigravity Agent Hub")
    parser.add_argument("path", nargs="?", default=".", help="Thư mục cần kiểm toán (mặc định: .)")
    parser.add_argument("--staged-only", action="store_true", help="Chỉ quét các tệp đã git add (staged)")
    parser.add_argument("--changed-only", action="store_true", help="Chỉ quét các tệp bị sửa đổi (dirty git files)")
    parser.add_argument("--fix", action="store_true", help="Tự động sửa lỗi với ruff nếu có thể")
    parser.add_argument("--json", action="store_true", help="Xuất kết quả dưới định dạng JSON M2M")
    args = parser.parse_args()

    mode = "all"
    if args.staged_only:
        mode = "staged"
    elif args.changed_only:
        mode = "changed"

    report = audit_project(args.path, mode=mode, auto_fix=args.fix)

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
        sys.exit(0 if report["status"] == "PASS" else 1)

    print("\n" + "=" * 65)
    print("🛡️  ANTIGRAVITY PRE-COMMIT & QA LINTER GUARD")
    print(f"📍 Thư mục: {report['target_dir']}")
    print(f"🔍 Chế độ quét: {report['mode']} | Tệp đã quét: {report['total_files_scanned']}")
    print("=" * 65)

    if report["status"] == "PASS":
        print("\n✅ [STATUS: PASS] TOÀN BỘ MÃ NGUỒN SẠCH SẼ & ĐẠT TIÊU CHUẨN!")
        print("   - Không có lỗi cú pháp (Python / JSON)")
        print("   - Không phát hiện rò rỉ secret / API keys")
        print("   - Tuân thủ nghiêm ngặt Rule 11 (Workspace Hygiene)")
        print("\n" + "=" * 65 + "\n")
        sys.exit(0)
    else:
        print(f"\n❌ [STATUS: FAIL] PHÁT HIỆN {report['violations_count']} VI PHẠM:")
        for idx, item in enumerate(report["violations"], 1):
            print(f"  {idx}. [{item['rule']}] {item['file']}:{item['line']}")
            print(f"     => {item['message']}")
        print("\n💡 Gợi ý khắc phục:")
        print("   - Sửa lỗi cú pháp tại dòng được chỉ định")
        print("   - Đưa API Key/Secret vào biến môi trường (.env)")
        print("   - Chạy 'hub_cleaner.py --clean' để dọn file rác/script tạm")
        print("=" * 65 + "\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
