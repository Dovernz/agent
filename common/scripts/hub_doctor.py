#!/usr/bin/env python3
"""
hub_doctor.py
Unified Health Check, Diagnostic & Pre-flight Inspection Engine
Checks Agent Hub git sync, skills integrity, Docker daemon, container health,
port bindings, and active token budget health in one unified pass.
"""

import os
import sys
import json
import glob
import socket
import subprocess
from pathlib import Path

# Ensure UTF-8 standard IO for Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def check_socket_port(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        result = s.connect_ex(('127.0.0.1', port))
        return result == 0

def check_git_hub(agent_hub_dir):
    res = {"status": "OK", "details": []}
    try:
        branch = subprocess.run(
            ["git", "-C", agent_hub_dir, "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True, text=True, timeout=3
        ).stdout.strip()
        
        diff = subprocess.run(
            ["git", "-C", agent_hub_dir, "status", "--porcelain"],
            capture_output=True, text=True, timeout=3
        ).stdout.strip()
        
        if diff:
            res["status"] = "WARN"
            res["details"].append(f"Hub có thay đổi chưa commit (Branch `{branch}`)")
        else:
            res["details"].append(f"Đồng bộ sạch sẽ trên nhánh `{branch}`")
    except Exception as e:
        res["status"] = "ERROR"
        res["details"].append(f"Lỗi kiểm tra Git: {e}")
    return res

def check_skills_integrity(agent_hub_dir):
    res = {"status": "OK", "skills_count": 0, "projects_count": 0, "errors": []}
    skills_json_path = os.path.join(agent_hub_dir, "skills.json")
    if not os.path.exists(skills_json_path):
        res["status"] = "ERROR"
        res["errors"].append("Không tìm thấy skills.json")
        return res
        
    try:
        with open(skills_json_path, 'r', encoding='utf-8') as f:
            cfg = json.load(f)
        for entry in cfg.get("entries", []):
            rel_p = entry.get("path")
            abs_p = os.path.normpath(os.path.join(agent_hub_dir, rel_p))
            if not os.path.exists(abs_p):
                res["status"] = "ERROR"
                res["errors"].append(f"Đường dẫn skill không tồn tại: {rel_p}")
                continue
            sf = glob.glob(os.path.join(abs_p, "*", "SKILL.md")) + glob.glob(os.path.join(abs_p, "SKILL.md"))
            res["skills_count"] += len(sf)
            
        p_dir = os.path.join(agent_hub_dir, "projects")
        p_names = [p for p in os.listdir(p_dir) if os.path.isdir(os.path.join(p_dir, p))]
        res["projects_count"] = len(p_names)
    except Exception as e:
        res["status"] = "ERROR"
        res["errors"].append(f"Lỗi kiểm tra kỹ năng: {e}")
    return res

def check_docker():
    res = {"status": "OK", "running_containers": [], "details": "Docker Daemon hoạt động bình thường"}
    try:
        v = subprocess.run(["docker", "version", "--format", "{{.Server.Version}}"], capture_output=True, text=True, timeout=5)
        if v.returncode != 0:
            res["status"] = "ERROR"
            res["details"] = "Docker daemon không chạy hoặc không thể kết nối."
            return res
            
        ps = subprocess.run(
            ["docker", "ps", "--format", "{{.Names}}|{{.Image}}|{{.Status}}|{{.Ports}}"],
            capture_output=True, text=True, timeout=5
        )
        for line in ps.stdout.splitlines():
            if line.strip():
                parts = line.split("|")
                res["running_containers"].append({
                    "name": parts[0],
                    "image": parts[1] if len(parts) > 1 else "",
                    "status": parts[2] if len(parts) > 2 else "",
                    "ports": parts[3] if len(parts) > 3 else ""
                })
    except Exception as e:
        res["status"] = "ERROR"
        res["details"] = f"Lỗi gọi docker: {e}"
    return res

def check_ports():
    ports_to_check = [80, 8000, 3000, 5432, 3306, 8080]
    active_ports = {}
    for p in ports_to_check:
        active_ports[p] = check_socket_port(p)
    return active_ports

def check_token_budget():
    res = {"status": "OK", "tokens": 0, "advice": None}
    try:
        base_dir = Path.home() / ".gemini" / "antigravity" / "brain"
        t_files = list(base_dir.glob("*/.system_generated/logs/transcript.jsonl"))
        if not t_files:
            return res
        latest_transcript = max(t_files, key=lambda f: f.stat().st_mtime)
        
        total_tokens = 0
        with open(latest_transcript, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                if not line.strip(): continue
                try:
                    obj = json.loads(line)
                    content = str(obj.get("content", ""))
                    thinking = str(obj.get("thinking", ""))
                    total_tokens += int(len(content) / 3.8) + int(len(thinking) / 3.8)
                except Exception:
                    pass
        res["tokens"] = total_tokens
        if total_tokens > 120000:
            res["status"] = "WARN"
            res["advice"] = "Ngân sách token vượt 120,000! Khuyến nghị gõ `/compact` để nén ngữ cảnh."
        elif total_tokens > 90000:
            res["status"] = "INFO"
            res["advice"] = "Ngân sách token ở mức cao (>90k). Cân nhắc dùng `/compact` khi phiên kéo dài."
    except Exception:
        pass
    return res

def main():
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    print("=" * 65)
    print("🩺 BÁC SĨ TOÀN DIỆN AGENT HUB (UNIFIED HUB DOCTOR)")
    print("=" * 65)
    
    # 1. Hub Git
    git_res = check_git_hub(root_dir)
    git_badge = "[✓] OK" if git_res["status"] == "OK" else f"[{git_res['status']}]"
    print(f"\n1. Hệ Thống Agent Hub (Git): {git_badge}")
    for d in git_res["details"]:
        print(f"   * {d}")
        
    # 2. Skills Integrity
    skills_res = check_skills_integrity(root_dir)
    skill_badge = "[✓] OK" if skills_res["status"] == "OK" else "[ERROR]"
    print(f"\n2. Kỹ Năng & Phân Cấp Dự Án: {skill_badge}")
    print(f"   * Tổng số kỹ năng đã đăng ký: {skills_res['skills_count']} skills")
    print(f"   * Tổng số nhóm dự án: {skills_res['projects_count']} projects")
    for err in skills_res.get("errors", []):
        print(f"   [-] {err}")
        
    # 3. Docker Health
    doc_res = check_docker()
    doc_badge = "[✓] OK" if doc_res["status"] == "OK" else "[ERROR]"
    print(f"\n3. Môi Trường Docker Container: {doc_badge}")
    print(f"   * Trạng thái daemon: {doc_res['details']}")
    print(f"   * Số container đang chạy: {len(doc_res['running_containers'])}")
    for c in doc_res["running_containers"]:
        ports_summary = f"({c['ports']})" if c['ports'] else ""
        print(f"     - `{c['name']}`: {c['status']} {ports_summary}")
        
    # 4. Port Bindings
    ports_map = check_ports()
    print(f"\n4. Cổng Dịch Vụ Mạng (Local Ports):")
    for port, active in ports_map.items():
        state = "🟢 Đang mở / Đã bind" if active else "⚪ Sẵn sàng / Rảnh"
        print(f"   * Cổng {port:<5}: {state}")
        
    # 5. Token Budget
    tok_res = check_token_budget()
    tok_badge = "[✓] OK" if tok_res["status"] == "OK" else f"[{tok_res['status']}]"
    print(f"\n5. Giám Sát Ngân Sách Token: {tok_badge}")
    print(f"   * Lượng token phiên hiện tại: ~{tok_res['tokens']:,} tokens")
    if tok_res.get("advice"):
        print(f"   * 💡 Gợi ý: {tok_res['advice']}")

    # 6. Rules Synchronization Check
    print(f"\n6. Đồng Bộ Quy Tắc (Rules Sync & Coverage):")
    try:
        from sync_rules import collect_workspaces, SOURCE_GEMINI
        workspaces = collect_workspaces()
        source_res = SOURCE_GEMINI.resolve()
        stale_count = 0
        missing_count = 0
        seen_ws = set()
        for name, ws in workspaces:
            r_ws = ws.resolve()
            if str(r_ws) in seen_ws: continue
            seen_ws.add(str(r_ws))
            dest = r_ws / "GEMINI.md"
            if dest.resolve() == source_res: continue
            if not dest.exists():
                missing_count += 1
            else:
                dst = dest.stat()
                src = SOURCE_GEMINI.stat()
                if src.st_size != dst.st_size or src.st_mtime > dst.st_mtime:
                    stale_count += 1
        if missing_count == 0 and stale_count == 0:
            print(f"   * [✓] OK: 100% ({len(seen_ws)}) workspace đã đồng bộ GEMINI.md mới nhất")
        else:
            print(f"   * [WARN] Phát hiện {missing_count} workspace thiếu, {stale_count} workspace cũ hơn master")
            print("     -> Chạy `hub sync --force` để đồng bộ ngay lập tức!")
    except Exception as e:
        print(f"   * [WARN] Không thể kiểm tra rules sync: {e}")
        
    # Summary
    print("\n" + "=" * 65)
    overall_ok = (git_res["status"] != "ERROR" and skills_res["status"] == "OK" and doc_res["status"] == "OK")
    if overall_ok:
        print("🎯 TỔNG KẾT: TOÀN BỘ HỆ THỐNG ĐẠT CHUẨN SẴN SÀNG 100%!")
        sys.exit(0)
    else:
        print("⚠️ TỔNG KẾT: CÓ MỘT SỐ HẠNG MỤC CẦN LƯU Ý!")
        sys.exit(1)

if __name__ == "__main__":
    main()
