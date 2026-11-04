#!/usr/bin/env python3
"""
System Integrity & Hierarchy Validator for Antigravity Agent Hub
Checks that all registered skills, projects, and rules are valid and properly structured.
"""

import os
import sys
import json
import glob

# Ensure UTF-8 standard IO for Windows
if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def main():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    agent_hub = os.path.dirname(root_dir)
    skills_json_path = os.path.join(agent_hub, "skills.json")
    
    print(f"[*] Đang kiểm tra tính toàn vẹn hệ thống tại: {agent_hub}")
    errors = []
    warnings = []
    
    # 1. Check skills.json
    if not os.path.exists(skills_json_path):
        errors.append("Không tìm thấy skills.json ở thư mục gốc!")
        return
        
    with open(skills_json_path, 'r', encoding='utf-8') as f:
        skills_cfg = json.load(f)
        
    entries = skills_cfg.get("entries", [])
    print(f"[+] Tìm thấy {len(entries)} đường dẫn kỹ năng được khai báo trong skills.json:")
    
    total_skills = 0
    for entry in entries:
        rel_path = entry.get("path")
        abs_path = os.path.normpath(os.path.join(agent_hub, rel_path))
        if not os.path.exists(abs_path):
            errors.append(f"Đường dẫn không tồn tại: {rel_path}")
            continue
            
        skill_files = glob.glob(os.path.join(abs_path, "*", "SKILL.md")) + glob.glob(os.path.join(abs_path, "SKILL.md"))
        for sf in skill_files:
            total_skills += 1
            # Check frontmatter
            with open(sf, 'r', encoding='utf-8', errors='ignore') as sff:
                content = sff.read()
                if not content.startswith("---") or "name:" not in content:
                    warnings.append(f"Tệp SKILL.md thiếu frontmatter hợp lệ: {sf}")
                    
        print(f"  - {rel_path}: {len(skill_files)} skill(s)")
        
    # 2. Check Project Structure
    projects_dir = os.path.join(agent_hub, "projects")
    project_names = [p for p in os.listdir(projects_dir) if os.path.isdir(os.path.join(projects_dir, p))]
    print(f"\n[+] Kiểm tra {len(project_names)} nhóm dự án:")
    for pname in project_names:
        pdir = os.path.join(projects_dir, pname)
        has_readme = os.path.exists(os.path.join(pdir, "README.md"))
        has_knowledge = os.path.exists(os.path.join(pdir, "knowledge"))
        has_skills = os.path.exists(os.path.join(pdir, "skills"))
        
        status = "OK" if (has_readme and has_skills) else "THIẾU TỆP"
        print(f"  - [{status}] {pname}")
        if not has_readme: warnings.append(f"Dự án {pname} thiếu README.md")
        if not has_skills: errors.append(f"Dự án {pname} thiếu thư mục skills/")
        
    # 3. Check M2M Rules
    m2m_rule = os.path.join(agent_hub, "rules", "m2m-protocol.md")
    if not os.path.exists(m2m_rule):
        errors.append("Thiếu rules/m2m-protocol.md ở thư mục gốc!")
    else:
        print("\n[+] Đã kiểm tra M2M Protocol toàn cục: HỢP LỆ")
        
    # Summary
    print("\n" + "="*50)
    print(f"TỔNG KẾT: {total_skills} Skills | {len(project_names)} Dự án | {len(errors)} Lỗi | {len(warnings)} Cảnh báo")
    if errors:
        print("[-] CÁC LỖI CẦN XỬ LÝ:")
        for e in errors: print(f"  * {e}")
        sys.exit(1)
    else:
        print("[✓] TOÀN BỘ HỆ THỐNG AGENT ĐÃ ĐƯỢC PHÂN CẤP HOÀN CHỈNH VÀ ĐẠT CHUẨN 100%!")
        sys.exit(0)

if __name__ == "__main__":
    main()
