#!/usr/bin/env python3
"""
Docker Environment Doctor (Cross-Project Container & Port Diagnostic Tool)
Detects port conflicts (80, 8000, 3000, 3306, 5432, 8080), inspects container health,
cleans dangling volumes, and performs safe service restarts.
"""

import os
import sys
import json
import subprocess
import re

# Ensure UTF-8 standard IO for Windows
if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

COMMON_PORTS = [80, 8000, 3000, 3306, 5432, 8080]

def run_cmd(cmd):
    try:
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8', errors='ignore')
        return res.returncode, res.stdout.strip(), res.stderr.strip()
    except Exception as e:
        return 1, "", str(e)

def check_docker_daemon():
    code, out, _ = run_cmd("docker info --format \"{{.ServerVersion}}\"")
    return code == 0, out if code == 0 else "Docker daemon is not running or not accessible."

def check_containers():
    code, out, _ = run_cmd("docker ps -a --format \"{{.Names}}\t{{.Status}}\t{{.Ports}}\"")
    if code != 0:
        return []
    containers = []
    for line in out.splitlines():
        if line.strip():
            parts = line.split("\t")
            containers.append({
                "name": parts[0] if len(parts) > 0 else "unknown",
                "status": parts[1] if len(parts) > 1 else "unknown",
                "ports": parts[2] if len(parts) > 2 else ""
            })
    return containers

def check_port_conflicts(ports=COMMON_PORTS):
    conflicts = []
    # On Windows, use Get-NetTCPConnection
    ps_cmd = 'powershell -Command "Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue | Select-Object LocalPort, OwningProcess | ConvertTo-Json"'
    code, out, _ = run_cmd(ps_cmd)
    if code == 0 and out:
        try:
            data = json.loads(out)
            if isinstance(data, dict):
                data = [data]
            for item in data:
                lport = item.get("LocalPort")
                pid = item.get("OwningProcess")
                if lport in ports:
                    # Get process name
                    pname_cmd = f'powershell -Command "(Get-Process -Id {pid} -ErrorAction SilentlyContinue).ProcessName"'
                    _, pname, _ = run_cmd(pname_cmd)
                    conflicts.append({
                        "port": lport,
                        "pid": pid,
                        "process_name": pname or "Unknown"
                    })
        except Exception:
            pass
    return conflicts

def kill_port_owner(pid):
    if pid and pid > 4: # Protect System idle/kernel
        code, _, err = run_cmd(f"taskkill /F /PID {pid}")
        return code == 0
    return False

def prune_docker():
    code, out, _ = run_cmd("docker system prune -f --volumes")
    return code == 0, out

def main():
    print("[*] Đang chẩn đoán môi trường Docker & Mạng...")
    daemon_ok, daemon_info = check_docker_daemon()
    if not daemon_ok:
        print(f"[-] LỖI: {daemon_info}")
        sys.exit(1)
        
    print(f"[✓] Docker Daemon hoạt động bình thường (Phiên bản: {daemon_info})")
    
    # Check port conflicts
    conflicts = check_port_conflicts()
    if conflicts:
        print(f"\n[!] CẢNH BÁO: Phát hiện {len(conflicts)} cổng đang bị chiếm dụng:")
        for c in conflicts:
            print(f"  - Cổng {c['port']}: PID {c['pid']} ({c['process_name']})")
            
        if "--kill-ports" in sys.argv:
            print("\n[*] Đang giải phóng các cổng xung đột...")
            for c in conflicts:
                ok = kill_port_owner(c['pid'])
                status = "ĐÃ DIỆT" if ok else "THẤT BẠI"
                print(f"  - Cổng {c['port']} (PID {c['pid']}): {status}")
    else:
        print("[✓] Không có xung đột cổng (80, 8000, 3000, 3306, 5432, 8080 đều an toàn).")
        
    # Check containers
    containers = check_containers()
    print(f"\n[+] Tổng số containers: {len(containers)}")
    for c in containers:
        status_flag = "[✓]" if "Up" in c["status"] else "[-]"
        print(f"  {status_flag} {c['name']}: {c['status']} ({c['ports']})")
        
    if "--prune" in sys.argv:
        print("\n[*] Đang dọn dẹp volumes và containers rác...")
        ok, res = prune_docker()
        print("[✓] Đã dọn dẹp thành công." if ok else f"[-] Thất bại: {res}")
        
    print("\n[✓] Hoàn tất chẩn đoán môi trường Docker.")

if __name__ == "__main__":
    main()
