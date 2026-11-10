#!/usr/bin/env python3
r"""
sync_rules.py - Antigravity Global Rule Sync Engine
Đồng bộ duy nhất 1 chiều từ Master (D:\Thành\Agent\GEMINI.md)
sang Global Plugin Runtime (C:\Users\thanhcaotien\.gemini\config\plugins\agent-core\rules\).
Tuyệt đối KHÔNG nhân bản file rác vào các thư mục dự án con.

Usage:
    hub sync              - Đồng bộ master sang global plugin
    hub sync --check      - Kiểm tra tính nhất quán
"""

import sys
import os
import shutil
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

AGENT_HUB = Path(os.environ.get("AGENT_HUB", r"D:\Thành\Agent"))
SOURCE_GEMINI = AGENT_HUB / "GEMINI.md"
GLOBAL_PLUGIN_RULES = Path(r"C:\Users\thanhcaotien\.gemini\config\plugins\agent-core\rules")


def sync(check_only: bool = False) -> bool:
    if not SOURCE_GEMINI.exists():
        print(f"[ERROR] Source không tồn tại: {SOURCE_GEMINI}")
        return False

    if not GLOBAL_PLUGIN_RULES.exists():
        if not check_only:
            GLOBAL_PLUGIN_RULES.mkdir(parents=True, exist_ok=True)
        else:
            print(f"[MISSING] Thư mục plugin toàn cầu chưa tồn tại: {GLOBAL_PLUGIN_RULES}")
            return False

    dest_gemini = GLOBAL_PLUGIN_RULES / "GEMINI.md"
    dest_agents = GLOBAL_PLUGIN_RULES / "AGENTS.md"

    # Kiểm tra trạng thái
    up_to_date = True
    src_stat = SOURCE_GEMINI.stat()

    for dest in [dest_gemini, dest_agents]:
        if not dest.exists():
            up_to_date = False
            break
        dst_stat = dest.stat()
        if src_stat.st_size != dst_stat.st_size or src_stat.st_mtime > dst_stat.st_mtime:
            up_to_date = False
            break

    if check_only:
        status = "ĐỒNG BỘ 100%" if up_to_date else "CẦN CẬP NHẬT (STALE)"
        print(f"Trạng thái Global Plugin Rules: [{status}]")
        return up_to_date

    try:
        shutil.copy2(SOURCE_GEMINI, dest_gemini)
        shutil.copy2(SOURCE_GEMINI, dest_agents)
        print(f"[SUCCESS] Đã đồng bộ Master GEMINI.md -> Global Plugin Rules:")
        print(f"  • {dest_gemini}")
        print(f"  • {dest_agents}")
        return True
    except Exception as e:
        print(f"[ERROR] Thất bại khi đồng bộ: {e}")
        return False


def main():
    args = sys.argv[1:]
    check_only = "--check" in args or "--list" in args
    sync(check_only=check_only)


if __name__ == "__main__":
    main()
