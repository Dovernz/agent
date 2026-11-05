#!/usr/bin/env python3
"""
create_project.py
Automated 1-Click Project Onboarding Engine for Antigravity Agent Hub
Initializes a new project squad, auto-scans tech stack, sets up PM orchestrator,
creates checkpoint, and registers skills in both local and global configs.
"""

import os
import sys
import json
import re
import shutil
import argparse
from pathlib import Path

# Ensure UTF-8 standard IO for Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Import scan_repo_techstack if in same scripts directory
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPTS_DIR not in sys.path:
    sys.path.append(SCRIPTS_DIR)

try:
    from scan_repo_techstack import scan_repository, generate_tech_stack_markdown
except ImportError:
    scan_repository = None
    generate_tech_stack_markdown = None

def slugify_name(name):
    slug = re.sub(r'[^a-zA-Z0-9_-]', '-', name).strip('-').lower()
    return slug

def update_skills_json(file_path, new_entry):
    if not os.path.exists(file_path):
        return False
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        entries = data.get("entries", [])
        
        # Check if already present
        exists = any(os.path.normpath(e.get("path", "")).lower() == os.path.normpath(new_entry.get("path", "")).lower() for e in entries)
        if not exists:
            entries.append(new_entry)
            data["entries"] = entries
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        return False
    except Exception as e:
        print(f"[!] Warning updating {file_path}: {e}", file=sys.stderr)
        return False

def main():
    parser = argparse.ArgumentParser(description="1-Click Project Onboarding for Antigravity Agent Hub")
    parser.add_argument("--name", "-n", required=True, help="Tên định danh dự án (ví dụ: ecommerce, crm-sales)")
    parser.add_argument("--repo", "-r", default=None, help="Đường dẫn thư mục mã nguồn thực tế của dự án")
    parser.add_argument("--desc", "-d", default=None, help="Mô tả ngắn gọn về nghiệp vụ của dự án")
    parser.add_argument("--force", "-f", action="store_true", help="Ghi đè nếu thư mục dự án đã tồn tại")
    
    args = parser.parse_args()
    
    project_slug = slugify_name(args.name)
    if not project_slug:
        print("[-] Tên dự án không hợp lệ!", file=sys.stderr)
        sys.exit(1)
        
    hub_dir = os.path.dirname(os.path.dirname(SCRIPTS_DIR))
    projects_dir = os.path.join(hub_dir, "projects")
    template_dir = os.path.join(projects_dir, "_template")
    target_project_dir = os.path.join(projects_dir, project_slug)
    
    print(f"[*] Khởi tạo dự án mới: [{project_slug}] tại: {target_project_dir}")
    
    if os.path.exists(target_project_dir):
        if not args.force:
            print(f"[-] Thư mục dự án '{project_slug}' đã tồn tại! Sử dụng cờ --force nếu muốn tạo lại.", file=sys.stderr)
            sys.exit(1)
        else:
            print(f"[!] Ghi đè thư mục dự án hiện có...")
            shutil.rmtree(target_project_dir)
            
    # 1. Copy template
    if not os.path.exists(template_dir):
        print(f"[-] Không tìm thấy thư mục template tại: {template_dir}", file=sys.stderr)
        sys.exit(1)
        
    shutil.copytree(template_dir, target_project_dir)
    print(f"[+] Đã nhân bản cấu trúc từ projects/_template")
    
    # 2. Update README.md
    readme_path = os.path.join(target_project_dir, "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            readme_text = f.read()
        readme_text = readme_text.replace("[PROJECT_NAME]", project_slug)
        if args.desc:
            readme_text += f"\n\n**Mô tả:** {args.desc}\n"
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_text)
            
    # 3. Update skills/pm-orchestrator/SKILL.md
    pm_skill_path = os.path.join(target_project_dir, "skills", "pm-orchestrator", "SKILL.md")
    if os.path.exists(pm_skill_path):
        with open(pm_skill_path, 'r', encoding='utf-8') as f:
            pm_skill_text = f.read()
        pm_skill_text = pm_skill_text.replace("[PROJECT_NAME]", project_slug)
        if args.desc:
            pm_skill_text = pm_skill_text.replace("Dự án [PROJECT_NAME]", f"Dự án {project_slug} ({args.desc})")
        with open(pm_skill_path, 'w', encoding='utf-8') as f:
            f.write(pm_skill_text)
        print(f"[+] Đã cấu hình PM Orchestrator: `{project_slug}-pm-orchestrator`")
        
    # 4. Create initial knowledge/checkpoint.md
    knowledge_dir = os.path.join(target_project_dir, "knowledge")
    os.makedirs(knowledge_dir, exist_ok=True)
    checkpoint_path = os.path.join(knowledge_dir, "checkpoint.md")
    initial_checkpoint = f"""# Project Checkpoint: {project_slug}

- **Cập nhật lần cuối:** Khởi tạo dự án
- **Trạng thái hiện tại:** Dự án vừa được khởi tạo thành công qua `create_project.py`.
- **Hạng mục đang xử lý dở dang:** Chưa có tác vụ nào đang chạy.
- **Hành động tiếp theo cần thực hiện:**
  1. Xác nhận Tech Stack trong `knowledge/tech-stack.md`.
  2. Bổ sung các quy tắc dự án đặc thù vào `rules/`.
  3. Giao task đầu tiên cho `{project_slug}-pm-orchestrator`.
"""
    with open(checkpoint_path, 'w', encoding='utf-8') as f:
        f.write(initial_checkpoint)
    print(f"[+] Đã tạo tệp ghi nhớ ngữ cảnh xuyên phiên: `knowledge/checkpoint.md`")
    
    # 5. Scan codebase if repo provided
    tech_stack_path = os.path.join(knowledge_dir, "tech-stack.md")
    if args.repo:
        repo_abs = os.path.abspath(args.repo)
        if os.path.exists(repo_abs):
            print(f"[*] Đang tự động quét mã nguồn tại: {repo_abs}")
            if scan_repository and generate_tech_stack_markdown:
                try:
                    discovery = scan_repository(repo_abs)
                    md_stack = generate_tech_stack_markdown(discovery)
                    with open(tech_stack_path, 'w', encoding='utf-8') as f:
                        f.write(md_stack)
                    print(f"[+] Đã tự động sinh hồ sơ Tech Stack thành công từ codebase thực tế!")
                    
                    # 5b. Scaffold baseline tests for Lead QA
                    tests_dir = os.path.join(target_project_dir, "tests")
                    os.makedirs(tests_dir, exist_ok=True)
                    baseline_test_path = os.path.join(tests_dir, "baseline_test.py")
                    
                    test_lines = [
                        '#!/usr/bin/env python3',
                        f'"""Baseline test suite for {project_slug} generated by Lead QA & create_project.py."""',
                        'import urllib.request',
                        'import pytest',
                        '',
                        'def ping_url(url, timeout=3):',
                        '    try:',
                        '        req = urllib.request.Request(url, headers={"User-Agent": "AgentHub-QA/1.0"})',
                        '        with urllib.request.urlopen(req, timeout=timeout) as res:',
                        '            return res.status',
                        '    except urllib.error.HTTPError as e:',
                        '        return e.code',
                        '    except Exception:',
                        '        return None',
                        ''
                    ]
                    
                    ports = discovery.get("ports", [])
                    if ports:
                        for p_str in ports:
                            p_clean = p_str.split(":")[0].strip()
                            if p_clean.isdigit():
                                test_lines.append(f'def test_port_{p_clean}_connectivity():')
                                test_lines.append(f'    code = ping_url("http://localhost:{p_clean}")')
                                test_lines.append(f'    assert code is not None and code < 500, f"Port {p_clean} not responsive"')
                                test_lines.append('')
                    else:
                        test_lines.append('def test_baseline_placeholder():')
                        test_lines.append('    assert True')
                        test_lines.append('')
                        
                    with open(baseline_test_path, 'w', encoding='utf-8') as tf:
                        tf.write("\n".join(test_lines))
                    print(f"[+] Đã khởi tạo bộ kiểm thử tự động Shift-Left: `tests/baseline_test.py`")
                except Exception as ex:
                    print(f"[!] Lỗi khi quét repo: {ex}")
            else:
                print("[!] Module scan_repo_techstack không tải được, giữ tech-stack.md mặc định.")
        else:
            print(f"[!] Đường dẫn repo '{args.repo}' không tồn tại trên máy.")
            
    # 6. Register in skills.json (Local Hub & Global Gemini Config)
    local_skills_json = os.path.join(hub_dir, "skills.json")
    local_added = update_skills_json(local_skills_json, {"path": f"projects/{project_slug}/skills"})
    if local_added:
        print(f"[+] Đã đăng ký vào: {local_skills_json}")
        
    global_skills_json = os.path.expanduser(r"~/.gemini/config/skills.json")
    global_path = os.path.normpath(os.path.join(hub_dir, "projects", project_slug, "skills"))
    global_added = update_skills_json(global_skills_json, {"path": global_path})
    if global_added:
        print(f"[+] Đã đăng ký vào cấu hình toàn cục Antigravity: {global_skills_json}")
        
    print("\n" + "="*60)
    print(f"[✓] HOÀN TẤT KHỞI TẠO DỰ ÁN: {project_slug}")
    print(f"  - PM Orchestrator: `{project_slug}-pm-orchestrator`")
    print(f"  - Thư mục dự án: `projects/{project_slug}`")
    print(f"  - Ngữ cảnh & Checkpoint: `projects/{project_slug}/knowledge/checkpoint.md`")
    print("="*60)

if __name__ == "__main__":
    main()
