#!/usr/bin/env python3
"""
hub_status.py
Portfolio Overview & Live Status Dashboard for Antigravity Agent Hub
Scans all project checkpoints, detects Git branches and uncommitted changes,
and produces a consolidated Markdown table in milliseconds.
"""

import os
import sys
import re
import subprocess
from pathlib import Path

# Ensure UTF-8 standard IO for Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def get_git_info(repo_path):
    if not repo_path or not os.path.exists(repo_path):
        return {"branch": "N/A", "clean": True, "uncommitted_count": 0}
    try:
        branch_cmd = subprocess.run(
            ["git", "-C", repo_path, "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True, text=True, timeout=3
        )
        branch = branch_cmd.stdout.strip() if branch_cmd.returncode == 0 else "N/A"
        
        status_cmd = subprocess.run(
            ["git", "-C", repo_path, "status", "--porcelain"],
            capture_output=True, text=True, timeout=3
        )
        lines = [l for l in status_cmd.stdout.splitlines() if l.strip()]
        return {
            "branch": branch,
            "clean": len(lines) == 0,
            "uncommitted_count": len(lines)
        }
    except Exception:
        return {"branch": "N/A", "clean": True, "uncommitted_count": 0}

def parse_checkpoint(checkpoint_path):
    info = {
        "last_updated": "Chưa có",
        "status": "Chưa có checkpoint",
        "in_progress": "Không có",
        "next_steps": []
    }
    if not os.path.exists(checkpoint_path):
        return info
        
    try:
        with open(checkpoint_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
        # Extract last_updated
        m_time = re.search(r'\*\*Cập nhật lần cuối:\*\*\s*(.*)', content)
        if m_time:
            info["last_updated"] = m_time.group(1).strip()
            
        # Extract status
        m_status = re.search(r'\*\*Trạng thái hiện tại:\*\*\s*([\s\S]*?)(?=\n-\s*\*\*|$)', content)
        if m_status:
            clean_status = m_status.group(1).strip().replace('\n', ' ')
            clean_status = re.sub(r'\s+', ' ', clean_status)
            info["status"] = clean_status[:120] + ("..." if len(clean_status) > 120 else "")
            
        # Extract in_progress
        m_prog = re.search(r'\*\*Hạng mục đang xử lý dở dang:\*\*\s*([\s\S]*?)(?=\n-\s*\*\*|$)', content)
        if m_prog:
            info["in_progress"] = m_prog.group(1).strip().replace('\n', ' ')[:100]
            
        # Extract next steps
        m_next = re.search(r'\*\*Hành động tiếp theo cần thực hiện:\*\*\s*([\s\S]*?)(?=\n#|$)', content)
        if m_next:
            steps = [s.strip() for s in m_next.group(1).splitlines() if s.strip()]
            info["next_steps"] = steps[:3]
    except Exception as e:
        info["status"] = f"Lỗi đọc checkpoint: {e}"
        
    return info

def extract_repo_path(tech_stack_path):
    if not os.path.exists(tech_stack_path):
        return None
    try:
        with open(tech_stack_path, 'r', encoding='utf-8', errors='ignore') as f:
            text = f.read()
        m = re.search(r'Đường dẫn (?:mã nguồn|dự án)[^:]*:\s*(?:\*\*)?\s*`([^`\r\n]+)`', text)
        if m:
            path_str = m.group(1).strip()
            if os.path.exists(path_str):
                return path_str
    except Exception:
        pass
    return None

def main():
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    projects_dir = os.path.join(root_dir, "projects")
    
    if not os.path.exists(projects_dir):
        print(f"[-] Không tìm thấy thư mục projects tại: {projects_dir}")
        sys.exit(1)
        
    projects = [p for p in os.listdir(projects_dir) if os.path.isdir(os.path.join(projects_dir, p)) and p != "_template"]
    projects.sort()
    
    print("# 📊 Bảng Điều Khiển Trạng Thái Toàn Cục (Agent Hub Portfolio)")
    print(f"> Tổng số dự án đang quản lý: **{len(projects)} dự án**  \n")
    print("| Dự Án | Branch Git | Trạng Thái Working Tree | Cập Nhật Lần Cuối | Trọng Tâm Hiện Tại |")
    print("| :--- | :--- | :--- | :--- | :--- |")
    
    details = []
    
    for p_name in projects:
        p_dir = os.path.join(projects_dir, p_name)
        cp_path = os.path.join(p_dir, "knowledge", "checkpoint.md")
        ts_path = os.path.join(p_dir, "knowledge", "tech-stack.md")
        
        repo_path = extract_repo_path(ts_path)
        git_info = get_git_info(repo_path)
        cp_info = parse_checkpoint(cp_path)
        
        branch_badge = f"`{git_info['branch']}`" if git_info['branch'] != "N/A" else "Local Hub"
        tree_badge = "🟢 Sạch" if git_info['clean'] else f"🟡 {git_info['uncommitted_count']} tệp sửa"
        
        print(f"| **{p_name}** | {branch_badge} | {tree_badge} | `{cp_info['last_updated']}` | {cp_info['status']} |")
        
        details.append({
            "name": p_name,
            "git": git_info,
            "cp": cp_info,
            "repo": repo_path
        })
        
    print("\n---")
    print("## 📌 Kế Hoạch Tiếp Theo Từng Dự Án\n")
    for d in details:
        print(f"### 🔹 {d['name']}")
        if d['repo']:
            print(f"- **Mã nguồn:** `{d['repo']}` (Branch: `{d['git']['branch']}`)")
        if d['cp']['in_progress'] and d['cp']['in_progress'] != "Không có":
            print(f"- **Dở dang:** {d['cp']['in_progress']}")
        if d['cp']['next_steps']:
            print("- **Hành động ưu tiên:**")
            for step in d['cp']['next_steps']:
                print(f"  {step}")
        else:
            print("- **Hành động ưu tiên:** Sẵn sàng nhận chỉ thị mới.")
        print()

if __name__ == "__main__":
    main()
