#!/usr/bin/env python3
"""
sync_rules.py - Antigravity Rule Sync Engine
Tự động đồng bộ GEMINI.md master vào tất cả workspace root của các project Antigravity.
Chạy khi: commit lên Agent repo, thêm project mới, hoặc gọi `hub sync`.

Usage:
    hub sync              - Đồng bộ GEMINI.md vào tất cả workspace
    hub sync --check      - Chỉ kiểm tra, không ghi
    hub sync --force      - Ghi đè tất cả, kể cả file đã có
    hub sync --list       - Liệt kê trạng thái GEMINI.md trên toàn bộ workspace
"""

import sys
import os
import json
import shutil
import glob
from pathlib import Path
from urllib.parse import unquote

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

AGENT_HUB = Path(os.environ.get("AGENT_HUB", r"D:\Thành\Agent"))
SOURCE_GEMINI = AGENT_HUB / "GEMINI.md"
PROJECTS_CONFIG_DIR = Path(r"C:\Users\thanhcaotien\.gemini\config\projects")

SKIP_FOLDERS = {".venv", "venv", "node_modules", ".git", "__pycache__"}


def resolve_uri(uri: str) -> Path | None:
    """Chuyển file:/// URI thành đường dẫn thực."""
    if not uri:
        return None
    decoded = unquote(uri.replace("file:///", "").replace("file://", ""))
    p = Path(decoded.replace("/", os.sep))
    return p if p.exists() else None


def collect_workspaces() -> list[tuple[str, Path]]:
    """Đọc tất cả project configs và trả về [(project_name, workspace_path)]."""
    workspaces = []
    for config_file in PROJECTS_CONFIG_DIR.glob("*.json"):
        if config_file.name == "outside-of-project.json":
            continue
        try:
            with open(config_file, encoding="utf-8") as f:
                d = json.load(f)
        except Exception:
            continue
        name = d.get("name", config_file.stem)
        resources = d.get("projectResources", {}).get("resources", [])
        for r in resources:
            uri = r.get("gitFolder", {}).get("folderUri", "") or r.get("folderUri", "")
            path = resolve_uri(uri)
            if path:
                workspaces.append((name, path))
    return workspaces


def sync(check_only: bool = False, force: bool = False) -> int:
    """Thực hiện đồng bộ. Trả về số file thực sự được deploy."""

    if not SOURCE_GEMINI.exists():
        print(f"[ERROR] Source không tồn tại: {SOURCE_GEMINI}")
        return 0

    workspaces = collect_workspaces()
    if not workspaces:
        print("[WARN] Không tìm thấy project config nào.")
        return 0

    deployed = 0
    skipped_exists = 0
    errors = 0

    print(f"{'[DRY-RUN] ' if check_only else ''}Đồng bộ {SOURCE_GEMINI.name} → {len(workspaces)} workspace(s)...\n")

    seen_paths = set()
    source_resolved = SOURCE_GEMINI.resolve()

    for project_name, ws_path in sorted(workspaces, key=lambda x: str(x[1])):
        resolved_ws = ws_path.resolve()
        if str(resolved_ws) in seen_paths:
            continue
        seen_paths.add(str(resolved_ws))

        dest = resolved_ws / "GEMINI.md"
        label = f"{project_name}: {ws_path}"

        # Bỏ qua nếu đích đến chính là file nguồn
        if dest.resolve() == source_resolved:
            print(f"  [SOURCE] {label} (File nguồn Master)")
            continue

        if dest.exists() and not force:
            src_stat = SOURCE_GEMINI.stat()
            dst_stat = dest.stat()
            if src_stat.st_size == dst_stat.st_size and src_stat.st_mtime <= dst_stat.st_mtime:
                print(f"  [OK]     {label}")
            else:
                print(f"  [STALE]  {label} -> Cũ hơn source! Dùng --force để cập nhật.")
            skipped_exists += 1
        else:
            if not check_only:
                try:
                    shutil.copy2(SOURCE_GEMINI, dest)
                    print(f"  [DEPLOY] {label}")
                    deployed += 1
                except Exception as e:
                    print(f"  [ERROR]  {label}: {e}")
                    errors += 1
            else:
                print(f"  [WOULD]  {label} -> GEMINI.md sẽ được tạo/cập nhật")
                deployed += 1

    print(f"\n{'=' * 60}")
    print(f"Tổng kết: {deployed} deploy | {skipped_exists} đã có | {errors} lỗi")
    if check_only:
        print("(Dry-run - không có file nào bị ghi thực sự)")
    return deployed


def install_git_hook():
    r"""Cài Git post-commit hook vào D:\Thành\Agent để tự động sync khi commit."""
    hook_dir = AGENT_HUB / ".git" / "hooks"
    hook_path = hook_dir / "post-commit"

    hook_script = f"""#!/bin/sh
# Auto-sync GEMINI.md vào tất cả workspace khi commit vào Agent repo
if git diff --name-only HEAD~1 HEAD 2>/dev/null | grep -q "GEMINI.md"; then
    echo "[hook] GEMINI.md đã thay đổi. Đang đồng bộ rules sang tất cả workspace..."
    uv run python "{AGENT_HUB / 'common' / 'scripts' / 'sync_rules.py'}" --force 2>&1
    echo "[hook] Đồng bộ hoàn tất."
fi
"""
    try:
        with open(hook_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(hook_script)
        print(f"[GIT HOOK] Đã cài post-commit hook tại: {hook_path}")
        return True
    except Exception as e:
        print(f"[ERROR] Không cài được hook: {e}")
        return False


def main():
    args = sys.argv[1:]
    check_only = "--check" in args
    force = "--force" in args
    install_hook = "--install-hook" in args
    report_only = "--list" in args

    if install_hook:
        install_git_hook()
        return

    if report_only:
        workspaces = collect_workspaces()
        source_resolved = SOURCE_GEMINI.resolve()
        print(f"{'PROJECT':<22} {'WORKSPACE':<52} {'GEMINI.md'}")
        print("-" * 90)
        seen = set()
        for name, ws in sorted(workspaces, key=lambda x: str(x[1])):
            r_ws = ws.resolve()
            if str(r_ws) in seen:
                continue
            seen.add(str(r_ws))
            dest = r_ws / "GEMINI.md"
            if dest.resolve() == source_resolved:
                status = "SOURCE (Master)"
            elif not dest.exists():
                status = "MISSING"
            else:
                dst = dest.stat()
                src = SOURCE_GEMINI.stat()
                stale = src.st_size != dst.st_size or src.st_mtime > dst.st_mtime
                status = "STALE" if stale else "OK"
            print(f"  {name:<20} {str(ws):<52} {status}")
        return

    sync(check_only=check_only, force=force)


if __name__ == "__main__":
    main()
