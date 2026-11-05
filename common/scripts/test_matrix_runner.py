#!/usr/bin/env python3
"""
test_matrix_runner.py
Universal Multi-Tier Test Matrix Runner for Antigravity Agent Hub.

Features:
- Auto-discovers and executes multi-tier test suites (Python, Node/TS, Docker).
- Segregates tests into tiers: Unit, Integration, Lint/Syntax, Smoke/Contract.
- Token-saving log truncation: redirects long error logs to files and emits compact M2M JSON.
- Measures execution latency per test suite.
- Clean zero-dependency Python design with robust subprocess handling.
"""

import os
import sys
import json
import time
import argparse
import subprocess
from pathlib import Path

# Ensure UTF-8 standard IO for Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass


def detect_test_targets(project_dir):
    """Auto-detects available test suites in the target project."""
    suites = []
    project_dir = os.path.abspath(project_dir)

    # 1. Python Pytest / Unittest
    py_test_locations = [
        "tests", "test", "backend/tests", "src/tests"
    ]
    for loc in py_test_locations:
        p = os.path.join(project_dir, loc)
        if os.path.isdir(p):
            has_py = any(f.startswith("test_") or f.endswith("_test.py") for _, _, files in os.walk(p) for f in files)
            if has_py:
                suites.append({
                    "id": f"py_unit_{loc.replace('/', '_')}",
                    "name": f"Python Tests ({loc})",
                    "type": "unit",
                    "cmd": ["uv", "run", "pytest", loc, "-v", "--tb=short"],
                    "cwd": project_dir
                })
                break

    # 2. Airflow DAG Tests (vietjet-airflow specialized or template)
    airflow_script = os.path.join(project_dir, "scripts", "test_all_dags.py")
    if os.path.exists(airflow_script):
        suites.append({
            "id": "airflow_dag_suite",
            "name": "Airflow DAG Multi-Tier AST Suite",
            "type": "integration",
            "cmd": ["uv", "run", "python", airflow_script],
            "cwd": project_dir
        })

    # 3. Frontend npm / yarn test
    for pkg_loc in [".", "frontend", "web", "client"]:
        pkg_file = os.path.join(project_dir, pkg_loc, "package.json")
        if os.path.exists(pkg_file):
            try:
                with open(pkg_file, "r", encoding="utf-8") as f:
                    pkg_data = json.load(f)
                scripts = pkg_data.get("scripts", {})
                if "test" in scripts and "no test specified" not in scripts["test"].lower():
                    suites.append({
                        "id": f"npm_test_{pkg_loc.replace('.', 'root')}",
                        "name": f"Frontend Test Suite ({pkg_loc})",
                        "type": "unit",
                        "cmd": ["npm", "test", "--", "--run"],
                        "cwd": os.path.join(project_dir, pkg_loc)
                    })
            except Exception:
                pass

    # 4. Universal Linter Guard
    linter_script = os.path.join(os.path.dirname(__file__), "linter_guard.py")
    if os.path.exists(linter_script):
        suites.append({
            "id": "linter_guard_tier",
            "name": "Pre-Commit Linter & Secret Guard",
            "type": "lint",
            "cmd": ["uv", "run", "python", linter_script, project_dir, "--json"],
            "cwd": project_dir
        })

    return suites


def run_suite(suite, timeout_sec=180):
    """Executes a single test suite and tracks execution latency and output."""
    start_time = time.time()
    try:
        proc = subprocess.run(
            suite["cmd"],
            cwd=suite["cwd"],
            capture_output=True,
            text=True,
            timeout=timeout_sec
        )
        duration = round(time.time() - start_time, 2)
        passed = (proc.returncode == 0)
        output = proc.stdout + "\n" + proc.stderr
        return {
            "id": suite["id"],
            "name": suite["name"],
            "type": suite["type"],
            "passed": passed,
            "returncode": proc.returncode,
            "duration_sec": duration,
            "output": output.strip()
        }
    except subprocess.TimeoutExpired:
        duration = round(time.time() - start_time, 2)
        return {
            "id": suite["id"],
            "name": suite["name"],
            "type": suite["type"],
            "passed": False,
            "returncode": -1,
            "duration_sec": duration,
            "output": f"TIMEOUT EXPIRED: Test suite vượt quá giới hạn thời gian {timeout_sec}s"
        }
    except Exception as e:
        duration = round(time.time() - start_time, 2)
        return {
            "id": suite["id"],
            "name": suite["name"],
            "type": suite["type"],
            "passed": False,
            "returncode": -2,
            "duration_sec": duration,
            "output": str(e)
        }


def run_matrix(project_dir, target_type="all", log_dir=None):
    """Runs matched test suites and compiles comprehensive test matrix report."""
    project_dir = os.path.abspath(project_dir)
    suites = detect_test_targets(project_dir)

    if target_type != "all":
        suites = [s for s in suites if s["type"] == target_type]

    if not suites:
        return {
            "status": "PASS",
            "message": "Không phát hiện bộ test suite nào cần chạy.",
            "suites_total": 0,
            "passed_count": 0,
            "failed_count": 0,
            "total_duration_sec": 0.0,
            "suites": []
        }

    results = []
    all_passed = True
    total_start = time.time()

    for s in suites:
        res = run_suite(s)
        results.append(res)
        if not res["passed"]:
            all_passed = False

    total_duration = round(time.time() - total_start, 2)
    failed_suites = [r for r in results if not r["passed"]]

    # Save detailed error trace to log file if there are failures (Rule 2 & 4 log truncation)
    log_file_path = None
    if failed_suites:
        if not log_dir:
            log_dir = os.path.join(project_dir, "logs")
        os.makedirs(log_dir, exist_ok=True)
        log_file_path = os.path.join(log_dir, "test_failure_trace.log")
        with open(log_file_path, "w", encoding="utf-8") as f:
            for r in failed_suites:
                f.write(f"=== FAILURE IN SUITE: {r['name']} ({r['id']}) ===\n")
                f.write(r["output"] + "\n\n")

    return {
        "status": "PASS" if all_passed else "FAIL",
        "project": project_dir,
        "suites_total": len(results),
        "passed_count": len([r for r in results if r["passed"]]),
        "failed_count": len(failed_suites),
        "total_duration_sec": total_duration,
        "log_file": log_file_path,
        "suites": [
            {
                "id": r["id"],
                "name": r["name"],
                "type": r["type"],
                "passed": r["passed"],
                "duration_sec": r["duration_sec"]
            }
            for r in results
        ]
    }


def main():
    parser = argparse.ArgumentParser(description="Universal Multi-Tier Test Matrix Runner for Antigravity Agent Hub")
    parser.add_argument("project", nargs="?", default=".", help="Đường dẫn thư mục dự án cần test")
    parser.add_argument("--suite", choices=["all", "unit", "integration", "lint"], default="all", help="Nhóm test suite mục tiêu")
    parser.add_argument("--json", action="store_true", help="Xuất kết quả định dạng JSON M2M")
    args = parser.parse_args()

    report = run_matrix(args.project, target_type=args.suite)

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
        sys.exit(0 if report["status"] == "PASS" else 1)

    print("\n" + "=" * 65)
    print("🧪 ANTIGRAVITY MULTI-TIER TEST MATRIX RUNNER")
    print(f"📍 Dự án: {report.get('project', args.project)}")
    print(f"⏱️  Tổng thời gian: {report['total_duration_sec']}s | Suites: {report['suites_total']}")
    print("=" * 65)

    for s in report["suites"]:
        status_icon = "✅ PASS" if s["passed"] else "❌ FAIL"
        print(f"  {status_icon} | [{s['type'].upper()}] {s['name']} ({s['duration_sec']}s)")

    if report["status"] == "PASS":
        print("\n🎉 [STATUS: PASS] TẤT CẢ CÁC BỘ TEST TRONG MA TRẬN ĐỀU VƯỢT QUA!")
        print("=" * 65 + "\n")
        sys.exit(0)
    else:
        print(f"\n💥 [STATUS: FAIL] CÓ {report['failed_count']} BỘ TEST THẤT BẠI!")
        if report.get("log_file"):
            print(f"📄 Chi tiết log lỗi đã được lưu tại: {report['log_file']}")
            print("💡 QA hãy mở file log để kiểm tra chi tiết lỗi, không in tràn màn hình chat.")
        print("=" * 65 + "\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
