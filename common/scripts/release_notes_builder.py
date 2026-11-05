#!/usr/bin/env python3
"""
release_notes_builder.py
Automated Changelog & Release Notes Generator for Antigravity Agent Hub.

Features:
- Parses Git commit history and classifies Conventional Commits (feat, fix, perf, refactor, docs, chore).
- Formats structured Markdown Release Notes and auto-updates CHANGELOG.md.
- Identifies commit hashes, scopes, authors, and dates.
- Zero-Fat M2M JSON output (--json) or Markdown preview (--preview).
- SSoT compliant: reads directly from the live Git repository.
"""

import os
import sys
import re
import json
import argparse
import subprocess
from datetime import datetime
from pathlib import Path

# Ensure UTF-8 standard IO for Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

CONVENTIONAL_PATTERN = re.compile(
    r'^(?P<type>feat|fix|perf|refactor|docs|chore|test|style|build|ci)(?:\((?P<scope>[^)]+)\))?!?: (?P<desc>.+)$',
    re.IGNORECASE
)

SECTION_MAPPING = {
    "feat": ("🚀 Tính Năng Mới (Features)", 1),
    "fix": ("🐛 Sửa Lỗi (Bug Fixes)", 2),
    "perf": ("⚡ Tối Ưu Hiệu Năng & Token (Performance)", 3),
    "refactor": ("🔨 Tái Cấu Trúc Mã Nguồn (Refactoring)", 4),
    "docs": ("📚 Tài Liệu & Hướng Dẫn (Documentation)", 5),
    "chore": ("⚙️ Bảo Trì & Hạ Tầng (Maintenance)", 6),
    "other": ("📦 Thay Đổi Khác (Other Changes)", 7)
}


def get_git_commits(repo_path, since_ref=None, max_count=30):
    """Fetches formatted commit entries from git log."""
    repo_path = os.path.abspath(repo_path)
    cmd = ["git", "-C", repo_path, "log", f"--max-count={max_count}", "--pretty=format:%h|||%an|||%ad|||%s", "--date=short"]
    
    if since_ref:
        cmd.insert(4, f"{since_ref}..HEAD")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        lines = result.stdout.strip().splitlines()
        commits = []
        for line in lines:
            if not line.strip():
                continue
            parts = line.split("|||")
            if len(parts) == 4:
                commits.append({
                    "hash": parts[0],
                    "author": parts[1],
                    "date": parts[2],
                    "subject": parts[3]
                })
        return commits
    except Exception as e:
        return []


def categorize_commits(commits):
    """Categorizes commits according to Conventional Commits standard."""
    categorized = {k: [] for k in SECTION_MAPPING}
    
    for c in commits:
        sub = c["subject"].strip()
        m = CONVENTIONAL_PATTERN.match(sub)
        if m:
            c_type = m.group("type").lower()
            scope = m.group("scope")
            desc = m.group("desc")
            target_key = c_type if c_type in categorized else "other"
            categorized[target_key].append({
                "hash": c["hash"],
                "scope": scope or "",
                "desc": desc,
                "author": c["author"],
                "date": c["date"],
                "raw": sub
            })
        else:
            categorized["other"].append({
                "hash": c["hash"],
                "scope": "",
                "desc": sub,
                "author": c["author"],
                "date": c["date"],
                "raw": sub
            })
            
    return categorized


def generate_markdown(categorized, version_tag="Latest Release", repo_name="Agent Hub"):
    """Generates structured Markdown release notes."""
    today = datetime.now().strftime("%Y-%m-%d")
    md_lines = [
        f"## 릴리즈 [{version_tag}] - {today}",
        f"> **Kho mã nguồn:** `{repo_name}` | Tự động tạo bởi `release_notes_builder.py`\n"
    ]

    has_content = False
    sorted_sections = sorted(SECTION_MAPPING.items(), key=lambda x: x[1][1])

    for key, (title, _) in sorted_sections:
        items = categorized.get(key, [])
        if not items:
            continue
        has_content = True
        md_lines.append(f"### {title}")
        for item in items:
            scope_prefix = f"**{item['scope']}:** " if item['scope'] else ""
            md_lines.append(f"- {scope_prefix}{item['desc']} (`{item['hash']}` bởi {item['author']})")
        md_lines.append("")

    if not has_content:
        md_lines.append("- Không có thay đổi nào đáng kể kể từ phiên bản trước.\n")

    return "\n".join(md_lines).strip() + "\n"


def update_changelog_file(output_path, new_content):
    """Prepends new release notes to an existing CHANGELOG.md or creates a new one."""
    existing_content = ""
    if os.path.exists(output_path):
        try:
            with open(output_path, "r", encoding="utf-8") as f:
                existing_content = f.read()
        except Exception:
            pass

    header = "# 📝 Nhật Ký Thay Đổi (Changelog)\n\nToàn bộ các cập nhật và tính năng mới được ghi nhận tại đây.\n\n---\n\n"
    
    if existing_content.startswith("# 📝 Nhật Ký Thay Đổi"):
        # Remove old header to prepend cleanly
        body = existing_content.split("---\n\n", 1)[-1]
        final_content = header + new_content + "\n---\n\n" + body
    else:
        final_content = header + new_content + ("\n---\n\n" + existing_content if existing_content else "")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(final_content)


def main():
    parser = argparse.ArgumentParser(description="Automated Changelog & Release Notes Generator for Antigravity Agent Hub")
    parser.add_argument("repo", nargs="?", default=".", help="Đường dẫn kho mã nguồn Git")
    parser.add_argument("--since", help="Git ref hoặc tag mốc bắt đầu (ví dụ: v1.0.0 hoặc HEAD~15)")
    parser.add_argument("--tag", default="vNext", help="Tên phiên bản release (mặc định: vNext)")
    parser.add_argument("--output", help="Đường dẫn file ghi changelog (ví dụ: CHANGELOG.md)")
    parser.add_argument("--preview", action="store_true", help="In bản Markdown xem trước ra màn hình")
    parser.add_argument("--json", action="store_true", help="Xuất kết quả dưới định dạng JSON M2M")
    args = parser.parse_args()

    commits = get_git_commits(args.repo, since_ref=args.since)
    categorized = categorize_commits(commits)
    repo_name = os.path.basename(os.path.abspath(args.repo))
    md_notes = generate_markdown(categorized, version_tag=args.tag, repo_name=repo_name)

    if args.json:
        result = {
            "version": args.tag,
            "repo": repo_name,
            "commits_analyzed": len(commits),
            "categorized": categorized
        }
        print(json.dumps(result, indent=2, ensure_ascii=False))
        sys.exit(0)

    if args.output:
        update_changelog_file(args.output, md_notes)
        print(f"[+] Đã ghi nhận bản ghi release vào: {args.output}")

    if args.preview or not args.output:
        print("\n" + "=" * 65)
        print("📝 BẢN XEM TRƯỚC NHẬT KÝ THAY ĐỔI (RELEASE NOTES PREVIEW)")
        print("=" * 65 + "\n")
        print(md_notes)
        print("=" * 65 + "\n")


if __name__ == "__main__":
    main()
