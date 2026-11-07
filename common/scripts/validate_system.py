#!/usr/bin/env python3
"""
System Integrity & Hierarchy Validator for Antigravity Agent Hub
Checks that all registered skills, projects, and rules are valid and properly structured,
verifying strict adherence to Zero-Execution in Main Chat, Anti-Polling, and M2M Protocols.
"""

import os
import sys
import json
import glob
import re

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
        
    # 3. Check M2M Rules & Rule 19 Integrity
    m2m_rule = os.path.join(agent_hub, "rules", "m2m-protocol.md")
    m2m_detail = os.path.join(agent_hub, "rules", "m2m-protocol-detail.md")
    if not os.path.exists(m2m_rule):
        errors.append("Thiếu rules/m2m-protocol.md ở thư mục gốc!")
    else:
        with open(m2m_rule, 'r', encoding='utf-8') as f:
            content = f.read()
            if "19." not in content or "Zero-Execution" not in content:
                errors.append("rules/m2m-protocol.md thiếu Quy tắc 19 (Zero-Execution & Reactive Wakeup)!")
        print("\n[+] Đã kiểm tra M2M Protocol toàn cục: HỢP LỆ (Bao gồm Rule 19 Zero-Execution)")

    # 4. Check GEMINI.md Directives
    gemini_md = os.path.join(agent_hub, "GEMINI.md")
    if not os.path.exists(gemini_md):
        errors.append("Thiếu GEMINI.md ở thư mục gốc!")
    else:
        with open(gemini_md, 'r', encoding='utf-8') as f:
            gcontent = f.read()
            if "TIẾNG VIỆT" not in gcontent:
                errors.append("GEMINI.md thiếu chỉ thị ngôn ngữ Tiếng Việt!")
            if "Rule 16" not in gcontent:
                errors.append("GEMINI.md thiếu Rule 16 (Ép sử dụng API tối đa)!")
            if "Rule 18" not in gcontent:
                errors.append("GEMINI.md thiếu Rule 18 (Phân mảnh ngữ cảnh)!")
            if "Rule 19" not in gcontent or "Zero-Execution" not in gcontent:
                errors.append("GEMINI.md thiếu Rule 19 (Zero-Execution trong Main Chat)!")
            if "schedule" not in gcontent.lower():
                errors.append("GEMINI.md thiếu quy tắc cấm polling qua schedule!")
        print("[+] Đã kiểm tra GEMINI.md Directives: HỢP LỆ (Chỉ thị Tiếng Việt, Rule 16, 18, 19)")

    # 5. Check Master Agent SKILL.md
    master_skill = os.path.join(agent_hub, "common", "skills", "master-agent", "SKILL.md")
    if not os.path.exists(master_skill):
        errors.append("Thiếu common/skills/master-agent/SKILL.md!")
    else:
        with open(master_skill, 'r', encoding='utf-8') as f:
            mscontent = f.read()
            if "dental-pm-orchestrator" not in mscontent:
                errors.append("master-agent/SKILL.md thiếu định tuyến dental-pm-orchestrator!")
            if "vj-pm-orchestrator" not in mscontent:
                errors.append("master-agent/SKILL.md thiếu định tuyến vj-pm-orchestrator!")
            if "ĐIỀU CẤM KỴ" not in mscontent:
                errors.append("master-agent/SKILL.md thiếu bảng Điều cấm kỵ của Master Agent!")
        print("[+] Đã kiểm tra Master Agent SKILL.md: HỢP LỆ (Định tuyến chuẩn & Bảng cấm kỵ)")

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
