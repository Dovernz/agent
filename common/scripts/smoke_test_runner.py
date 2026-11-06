#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unified Smoke Test Runner (0.5s Endpoint & Container Diagnostic)
==============================================================================
Kiểm tra tức thì trạng thái sẵn sàng (Readiness) của toàn bộ các dịch vụ:
- WordPress Headless (Port 80)
- Django Dental Backend (Port 8000)
- Airflow Webserver & Health API (Port 8080)
- Airflow PostgreSQL DB (Port 5434)
- WordPress MySQL DB (Port 3306)
- Trạng thái các Docker Containers đang hoạt động
==============================================================================
"""

import sys
import time
import socket
import urllib.request
import urllib.error
import subprocess
from typing import Dict, List, Tuple

# Đảm bảo mã hóa UTF-8 cho Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


def check_tcp_port(host: str, port: int, timeout: float = 1.0) -> Tuple[bool, float]:
    """Kiểm tra kết nối TCP socket tới một port."""
    t0 = time.time()
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        elapsed = time.time() - t0
        return (result == 0, elapsed)
    except Exception:
        return (False, time.time() - t0)


def check_http_endpoint(url: str, timeout: float = 1.5) -> Tuple[bool, int, str, float]:
    """Kiểm tra phản hồi HTTP từ một endpoint."""
    t0 = time.time()
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Antigravity-SmokeRunner/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            elapsed = time.time() - t0
            return (True, resp.status, "OK", elapsed)
    except urllib.error.HTTPError as e:
        elapsed = time.time() - t0
        # Nhiều endpoint như /api/ hoặc /admin/ trả về 401 hoặc 302/404 nhưng server vẫn đang chạy
        is_alive = e.code in [200, 301, 302, 401, 403, 404]
        return (is_alive, e.code, f"HTTP {e.code}", elapsed)
    except Exception as e:
        elapsed = time.time() - t0
        return (False, 0, str(e), elapsed)


def get_docker_containers() -> List[Dict[str, str]]:
    """Lấy danh sách các container đang chạy."""
    try:
        res = subprocess.run(
            "docker ps --format \"{{.Names}}\t{{.Status}}\t{{.Ports}}\"",
            shell=True, capture_output=True, text=True, encoding="utf-8", errors="ignore"
        )
        if res.returncode != 0:
            return []
        containers = []
        for line in res.stdout.strip().splitlines():
            if line.strip():
                parts = line.split("\t")
                containers.append({
                    "name": parts[0] if len(parts) > 0 else "unknown",
                    "status": parts[1] if len(parts) > 1 else "unknown",
                    "ports": parts[2] if len(parts) > 2 else ""
                })
        return containers
    except Exception:
        return []


def main():
    print("=" * 80)
    print("🔥 BẢNG KIỂM TRA NHANH DỊCH VỤ & HẠ TẦNG DOCKER (SMOKE TEST)")
    print("=" * 80)

    # 1. Danh sách các endpoints cần kiểm tra
    services = [
        {"name": "WordPress Dental", "type": "HTTP", "target": "http://localhost:80", "port": 80},
        {"name": "Django Dental Backend", "type": "HTTP", "target": "http://localhost:8000", "port": 8000},
        {"name": "Airflow Webserver", "type": "HTTP", "target": "http://localhost:8080/health", "port": 8080},
        {"name": "Airflow PostgreSQL", "type": "TCP", "target": "localhost:5434", "host": "127.0.0.1", "port": 5434, "container": "test-postgres-1"},
        {"name": "WordPress MySQL", "type": "TCP", "target": "localhost:3306", "host": "127.0.0.1", "port": 3306, "container": "dental_wp_db"},
    ]

    print(f"{'Dịch Vụ':<24} | {'Giao Thức':<9} | {'Cổng / Endpoint':<24} | {'Độ Trễ':<8} | {'Trạng Thái'}")
    print("-" * 80)

    all_passed = True
    for s in services:
        if s["type"] == "HTTP":
            alive, code, msg, lat = check_http_endpoint(s["target"])
            status_text = f"🟢 HOẠT ĐỘNG ({code})" if alive else f"🔴 MẤT KẾT NỐI"
        else:
            alive, lat = check_tcp_port(s["host"], s["port"])
            status_text = "🟢 SẴN SÀNG" if alive else "🔴 CHƯA MỞ"

        if not alive and s.get("container"):
            # Nếu cổng không bind ra host, kiểm tra trạng thái bên trong container
            c_name = s["container"]
            try:
                res = subprocess.run(
                    f"docker inspect --format \"{{{{.State.Running}}}}\" {c_name}",
                    shell=True, capture_output=True, text=True
                )
                if res.stdout.strip().lower() == "true":
                    alive = True
                    status_text = "🟢 SẴN SÀNG (Internal Docker)"
            except Exception:
                pass

        if not alive:
            all_passed = False

        print(f"{s['name']:<24} | {s['type']:<9} | {s['target']:<24} | {lat*1000:>5.1f}ms | {status_text}")

    print("-" * 80)
    print("📦 TRẠNG THÁI DOCKER CONTAINERS ĐANG CHẠY:")
    containers = get_docker_containers()
    if containers:
        for c in containers:
            print(f"  • {c['name']:<28} : {c['status']}")
    else:
        print("  ⚠️ Không tìm thấy Docker container nào đang hoạt động.")

    print("=" * 80)
    if all_passed:
        print("🎯 TỔNG KẾT: 100% ENDPOINTS & DỊCH VỤ HOẠT ĐỘNG HOÀN HẢO!")
        sys.exit(0)
    else:
        print("⚠️ CẢNH BÁO: Phát hiện dịch vụ chưa hoạt động hoặc cổng chưa được bind!")
        sys.exit(1)


if __name__ == "__main__":
    main()
