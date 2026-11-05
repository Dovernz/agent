#!/usr/bin/env python3
"""
git_safe_snapshot.py
Git Safe-Checkpoint & Auto-Rollback Engine for Antigravity Agent Hub
Provides non-destructive workspace snapshots before complex dev tasks,
enabling 1-command safe rollback if a QA loop fails or code breaks.
"""

import os
import sys
import json
import argparse
import subprocess
from pathlib import Path

# Ensure UTF-8 standard IO for Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def run_git(repo_path, args):
    res = subprocess.run(["git", "-C", repo_path] + args, capture_output=True, text=True, timeout=10)
    return res

def create_snapshot(repo_path, task_id):
    repo_path = os.path.abspath(repo_path)
    if not os.path.exists(os.path.join(repo_path, ".git")):
        print(f"[-] Thư mục không phải là git repo: {repo_path}", file=sys.stderr)
        sys.exit(1)
        
    head_res = run_git(repo_path, ["rev-parse", "HEAD"])
    branch_res = run_git(repo_path, ["rev-parse", "--abbrev-ref", "HEAD"])
    
    commit_sha = head_res.stdout.strip()
    branch = branch_res.stdout.strip()
    
    # Check if there are modified files
    status_res = run_git(repo_path, ["status", "--porcelain"])
    has_dirty_files = bool(status_res.stdout.strip())
    
    stash_ref = None
    if has_dirty_files:
        # Create a stash commit without modifying working tree
        stash_res = run_git(repo_path, ["stash", "create", f"snapshot_{task_id}"])
        stash_ref = stash_res.stdout.strip()
        
    snapshot_data = {
        "task_id": task_id,
        "repo_path": repo_path,
        "branch": branch,
        "commit_sha": commit_sha,
        "stash_ref": stash_ref,
        "has_dirty_files": has_dirty_files
    }
    
    # Save snapshot metadata
    snap_dir = os.path.join(repo_path, ".agent_snapshots")
    os.makedirs(snap_dir, exist_ok=True)
    snap_file = os.path.join(snap_dir, f"{task_id}.json")
    with open(snap_file, 'w', encoding='utf-8') as f:
        json.dump(snapshot_data, f, indent=2, ensure_ascii=False)
        
    print(f"[✓] Đã tạo Safe-Snapshot cho task [{task_id}] tại commit {commit_sha[:8]}")
    if stash_ref:
        print(f"    - Ghi nhận trạng thái dirty files tại stash ref: {stash_ref[:8]}")
    return snapshot_data

def rollback_snapshot(repo_path, task_id):
    repo_path = os.path.abspath(repo_path)
    snap_file = os.path.join(repo_path, ".agent_snapshots", f"{task_id}.json")
    if not os.path.exists(snap_file):
        print(f"[-] Không tìm thấy snapshot của task [{task_id}] tại {snap_file}", file=sys.stderr)
        sys.exit(1)
        
    with open(snap_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    print(f"[*] Đang thực hiện rollback về snapshot ban đầu của task [{task_id}]...")
    
    # 1. Reset all current uncommitted changes
    run_git(repo_path, ["reset", "--hard", data["commit_sha"]])
    run_git(repo_path, ["clean", "-fd"])
    
    # 2. If had dirty files at snapshot time, restore them
    if data.get("stash_ref"):
        run_git(repo_path, ["stash", "apply", "--quiet", data["stash_ref"]])
        print(f"[+] Đã khôi phục trạng thái tệp làm việc dở dang ban đầu.")
        
    print(f"[✓] HOÀN NGUYÊN AN TOÀN THÀNH CÔNG! Mã nguồn đã trở về trạng thái trước khi thực thi task {task_id}.")

def clear_snapshot(repo_path, task_id):
    repo_path = os.path.abspath(repo_path)
    snap_file = os.path.join(repo_path, ".agent_snapshots", f"{task_id}.json")
    if os.path.exists(snap_file):
        os.remove(snap_file)
        print(f"[+] Đã dọn dẹp snapshot task [{task_id}] sau khi hoàn tất thành công.")

def main():
    parser = argparse.ArgumentParser(description="Git Safe Snapshot & Auto-Rollback Engine")
    parser.add_argument("action", choices=["create", "rollback", "clear"], help="Thao tác snapshot")
    parser.add_argument("--repo", "-r", required=True, help="Đường dẫn repository")
    parser.add_argument("--task", "-t", required=True, help="ID của tác vụ (ví dụ: TASK-101)")
    
    args = parser.parse_args()
    
    if args.action == "create":
        create_snapshot(args.repo, args.task)
    elif args.action == "rollback":
        rollback_snapshot(args.repo, args.task)
    elif args.action == "clear":
        clear_snapshot(args.repo, args.task)

if __name__ == "__main__":
    main()
