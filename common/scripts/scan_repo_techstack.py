#!/usr/bin/env python3
"""
scan_repo_techstack.py
Automated Tech Stack & Environment Discovery Engine for Antigravity Agent Hub
Scans codebases, Docker configs, package managers, and generates structured tech-stack.md.
"""

import os
import sys
import json
import re
import argparse
from pathlib import Path

# Ensure UTF-8 standard IO for Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def parse_docker_compose(compose_path):
    """Simple parser for docker-compose.yml to extract services, images, ports."""
    services = {}
    if not os.path.exists(compose_path):
        return services
        
    try:
        with open(compose_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            
        current_service = None
        in_services = False
        in_ports = False
        
        for line in lines:
            stripped = line.strip()
            indent = len(line) - len(line.lstrip())
            
            if re.match(r'^services:\s*$', stripped):
                in_services = True
                continue
                
            if in_services and indent == 2 and stripped.endswith(':'):
                current_service = stripped[:-1].strip()
                services[current_service] = {"ports": [], "image": None, "container_name": None}
                in_ports = False
                continue
                
            if current_service and in_services and indent >= 4:
                if stripped.startswith("container_name:"):
                    services[current_service]["container_name"] = stripped.split(":", 1)[1].strip().strip('"\'')
                elif stripped.startswith("image:"):
                    services[current_service]["image"] = stripped.split(":", 1)[1].strip().strip('"\'')
                elif stripped.startswith("ports:"):
                    in_ports = True
                    continue
                elif in_ports:
                    if stripped.startswith("-"):
                        port_str = stripped.lstrip("-").strip().strip('"\'')
                        services[current_service]["ports"].append(port_str)
                    elif indent == 4 and not stripped.startswith("-"):
                        in_ports = False
    except Exception as e:
        print(f"[!] Warning reading docker compose: {e}", file=sys.stderr)
        
    return services

def scan_repository(repo_path):
    repo_path = os.path.abspath(repo_path)
    if not os.path.isdir(repo_path):
        raise ValueError(f"Path is not a valid directory: {repo_path}")
        
    discovery = {
        "repo_path": repo_path,
        "repo_name": os.path.basename(repo_path),
        "docker_services": {},
        "dockerfiles": [],
        "backend": {
            "type": "Unknown",
            "frameworks": [],
            "dependencies": []
        },
        "frontend": {
            "type": "Unknown",
            "frameworks": [],
            "dependencies": []
        },
        "database": [],
        "cms": [],
        "ports": [],
        "env_files": []
    }
    
    # 1. Scan Docker & Compose
    compose_candidates = ["docker-compose.yml", "docker-compose.yaml", "compose.yml", "compose.yaml"]
    for c in compose_candidates:
        c_path = os.path.join(repo_path, c)
        if os.path.exists(c_path):
            discovery["docker_services"] = parse_docker_compose(c_path)
            for s_name, s_data in discovery["docker_services"].items():
                for p in s_data.get("ports", []):
                    discovery["ports"].append(p)
                    
    for root, dirs, files in os.walk(repo_path):
        # Limit search depth to 3
        depth = os.path.relpath(root, repo_path).count(os.sep)
        if depth > 3:
            dirs.clear()
            continue
            
        # Ignore bulky node_modules, .git, venv
        dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', '.venv', 'venv', '__pycache__', 'dist', 'build']]
        
        for file in files:
            file_lower = file.lower()
            full_file = os.path.join(root, file)
            
            if file_lower.startswith("dockerfile"):
                discovery["dockerfiles"].append(os.path.relpath(full_file, repo_path))
                
            if file_lower in [".env.example", ".env.sample", ".env"]:
                discovery["env_files"].append(os.path.relpath(full_file, repo_path))
                
            # Python check
            if file_lower == "requirements.txt" or file_lower == "pyproject.toml":
                discovery["backend"]["type"] = "Python"
                try:
                    with open(full_file, "r", encoding="utf-8", errors="ignore") as pf:
                        content = pf.read().lower()
                        if "django" in content and "django" not in discovery["backend"]["frameworks"]:
                            discovery["backend"]["frameworks"].append("Django")
                        if "django-unfold" in content:
                            discovery["backend"]["frameworks"].append("Django Unfold Admin")
                        if "fastapi" in content:
                            discovery["backend"]["frameworks"].append("FastAPI")
                        if "flask" in content:
                            discovery["backend"]["frameworks"].append("Flask")
                        if "celery" in content:
                            discovery["backend"]["frameworks"].append("Celery")
                        if "apache-airflow" in content or "airflow" in content:
                            discovery["backend"]["frameworks"].append("Apache Airflow")
                        if "psycopg" in content or "postgresql" in content:
                            if "PostgreSQL" not in discovery["database"]: discovery["database"].append("PostgreSQL")
                        if "mysqlclient" in content or "pymysql" in content or "mysql" in content:
                            if "MySQL/MariaDB" not in discovery["database"]: discovery["database"].append("MySQL/MariaDB")
                        if "redis" in content:
                            if "Redis" not in discovery["database"]: discovery["database"].append("Redis")
                except Exception:
                    pass

            # Node / JS / Frontend check
            if file_lower == "package.json":
                try:
                    with open(full_file, "r", encoding="utf-8", errors="ignore") as jf:
                        pkg = json.load(jf)
                        all_deps = {}
                        all_deps.update(pkg.get("dependencies", {}))
                        all_deps.update(pkg.get("devDependencies", {}))
                        
                        for dep in all_deps.keys():
                            d_lower = dep.lower()
                            if "react" in d_lower and "React" not in discovery["frontend"]["frameworks"]:
                                discovery["frontend"]["frameworks"].append("React")
                            if "vue" in d_lower and "Vue" not in discovery["frontend"]["frameworks"]:
                                discovery["frontend"]["frameworks"].append("Vue.js")
                            if "next" in d_lower and "Next.js" not in discovery["frontend"]["frameworks"]:
                                discovery["frontend"]["frameworks"].append("Next.js")
                            if "tailwind" in d_lower and "Tailwind CSS" not in discovery["frontend"]["frameworks"]:
                                discovery["frontend"]["frameworks"].append("Tailwind CSS")
                            if "vite" in d_lower and "Vite" not in discovery["frontend"]["frameworks"]:
                                discovery["frontend"]["frameworks"].append("Vite")
                            if "lucide" in d_lower:
                                discovery["frontend"]["dependencies"].append("Lucide Icons")
                            if "playwright" in d_lower:
                                discovery["frontend"]["dependencies"].append("Playwright")
                            if "express" in d_lower:
                                discovery["backend"]["frameworks"].append("Express.js")
                            if "nestjs" in d_lower:
                                discovery["backend"]["frameworks"].append("NestJS")
                except Exception:
                    pass
                    
            # PHP / WordPress
            if file_lower == "wp-config.php" or file_lower == "wp-settings.php":
                if "WordPress" not in discovery["cms"]:
                    discovery["cms"].append("WordPress")
                if "MySQL/MariaDB" not in discovery["database"]:
                    discovery["database"].append("MySQL/MariaDB")
            if file_lower == "composer.json":
                try:
                    with open(full_file, "r", encoding="utf-8", errors="ignore") as cf:
                        c_data = cf.read().lower()
                        if "laravel" in c_data and "Laravel" not in discovery["backend"]["frameworks"]:
                            discovery["backend"]["frameworks"].append("Laravel")
                except Exception:
                    pass

    # Deduplicate & normalize
    discovery["ports"] = sorted(list(set(discovery["ports"])))
    if discovery["backend"]["frameworks"] and discovery["backend"]["type"] == "Unknown":
        discovery["backend"]["type"] = "Multi-Service / Detected"
    if discovery["frontend"]["frameworks"] and discovery["frontend"]["type"] == "Unknown":
        discovery["frontend"]["type"] = "Modern Web UI"
        
    return discovery

def generate_tech_stack_markdown(discovery):
    repo_name = discovery["repo_name"]
    repo_path = discovery["repo_path"]
    
    md = [
        f"# Tech Stack & Architecture Context: {repo_name}",
        "",
        f"> **Đường dẫn mã nguồn:** `{repo_path}`  ",
        f"> **Tự động khảo sát bởi:** `lead-ba` (Universal Business Analyst)  ",
        "",
        "---",
        "",
        "## 🏗️ 1. Tổng Quan Kiến Trúc & Môi Trường",
        ""
    ]
    
    # Docker services
    if discovery["docker_services"]:
        md.append("### Containerization & Docker Services")
        md.append("| Service | Container Name | Image | Port Bindings |")
        md.append("| :--- | :--- | :--- | :--- |")
        for s_name, s_info in discovery["docker_services"].items():
            c_name = s_info.get("container_name") or s_name
            img = s_info.get("image") or "build from Dockerfile"
            ports = ", ".join(s_info.get("ports", [])) or "Internal"
            md.append(f"| `{s_name}` | `{c_name}` | `{img}` | `{ports}` |")
        md.append("")
    else:
        md.append("- **Môi trường:** Local / Standalone (Không phát hiện `docker-compose.yml`)")
        md.append("")
        
    # Backend
    md.append("## ⚙️ 2. Backend & Dịch Vụ API")
    md.append(f"- **Ngôn ngữ / Nền tảng:** {discovery['backend']['type']}")
    if discovery["backend"]["frameworks"]:
        md.append(f"- **Frameworks:** {', '.join(discovery['backend']['frameworks'])}")
    else:
        md.append("- **Frameworks:** Custom / Chưa xác định")
    md.append("")
    
    # Frontend
    md.append("## 🎨 3. Frontend & Giao Diện Người Dùng")
    md.append(f"- **Phân loại giao diện:** {discovery['frontend']['type']}")
    if discovery["frontend"]["frameworks"]:
        md.append(f"- **UI Frameworks / Thư viện:** {', '.join(discovery['frontend']['frameworks'])}")
    if discovery["frontend"]["dependencies"]:
        md.append(f"- **Bổ trợ:** {', '.join(set(discovery['frontend']['dependencies']))}")
    md.append("")
    
    # Database & Storage
    md.append("## 🗄️ 4. Cơ Sở Dữ Liệu & CMS")
    if discovery["database"]:
        md.append(f"- **Hệ quản trị CSDL:** {', '.join(discovery['database'])}")
    else:
        md.append("- **Hệ quản trị CSDL:** Không xác định / Dùng file hoặc DB ngoài")
    if discovery["cms"]:
        md.append(f"- **CMS:** {', '.join(discovery['cms'])}")
    md.append("")
    
    # Ports & Endpoints
    if discovery["ports"]:
        md.append("## 🔌 5. Cổng Dịch Vụ Mở (Active Ports)")
        for p in discovery["ports"]:
            md.append(f"- `{p}`")
        md.append("")
        
    md.append("---")
    md.append("*Tài liệu được sinh tự động. Lead BA sẽ tiếp tục cập nhật sau mỗi chu kỳ phát triển.*")
    return "\n".join(md)

def main():
    parser = argparse.ArgumentParser(description="Scan codebase and generate structured tech-stack.md")
    parser.add_argument("repo_path", help="Path to repository or code folder")
    parser.add_argument("--output", "-o", help="Optional output path for tech-stack.md", default=None)
    parser.add_argument("--json", action="store_true", help="Output raw JSON discovery")
    
    args = parser.parse_args()
    
    try:
        discovery = scan_repository(args.repo_path)
    except Exception as e:
        print(f"[-] Lỗi khảo sát: {e}", file=sys.stderr)
        sys.exit(1)
        
    if args.json:
        print(json.dumps(discovery, indent=2, ensure_ascii=False))
        return
        
    md_content = generate_tech_stack_markdown(discovery)
    
    if args.output:
        out_dir = os.path.dirname(os.path.abspath(args.output))
        os.makedirs(out_dir, exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(md_content)
        print(f"[+] Đã tạo thành công hồ sơ Tech Stack tại: {args.output}")
    else:
        print(md_content)

if __name__ == "__main__":
    main()
