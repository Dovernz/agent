#!/usr/bin/env python3
"""
Airflow Multi-Agent Pipeline Orchestrator & CLI Tool.
Handles schema validation, fast DAG verification, and inter-agent payloads.
"""

import os
import sys
import json
import argparse
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SCHEMAS_DIR = BASE_DIR / "schemas"
SCRIPTS_DIR = BASE_DIR / "scripts"

def validate_json_spec(spec_data: dict) -> dict:
    required_keys = ["dag_id", "schedule", "tasks"]
    missing = [k for k in required_keys if k not in spec_data]
    if missing:
        return {"status": "FAIL", "stage": "spec_validation", "errors": [f"Missing required keys: {missing}"]}
    if not isinstance(spec_data["tasks"], list) or len(spec_data["tasks"]) == 0:
        return {"status": "FAIL", "stage": "spec_validation", "errors": ["'tasks' must be a non-empty list"]}
    return {"status": "PASS"}

def test_dag_file(dag_path: str, docker: bool = True) -> dict:
    validator_script = SCRIPTS_DIR / "fast_test_dag.py"
    python_bin = sys.executable
    cmd = [python_bin, str(validator_script), dag_path]
    if docker:
        cmd.append("--docker")
    proc = subprocess.run(cmd, capture_output=True, text=True)
    try:
        return json.loads(proc.stdout.strip())
    except Exception:
        return {
            "status": "FAIL",
            "stage": "exec_error",
            "errors": [{"message": proc.stderr or proc.stdout}]
        }

def main():
    parser = argparse.ArgumentParser(description="Multi-Agent DAG Runner")
    parser.add_argument("--validate-spec", help="Validate a DAG JSON spec file")
    parser.add_argument("--test-dag", help="Validate a generated DAG Python file")
    parser.add_argument("--no-docker", action="store_true", help="Skip Docker DagBag test")
    args = parser.parse_args()

    if args.validate_spec:
        with open(args.validate_spec, "r", encoding="utf-8") as f:
            data = json.load(f)
        result = validate_json_spec(data)
        print(json.dumps(result))
        sys.exit(0 if result["status"] == "PASS" else 1)

    if args.test_dag:
        result = test_dag_file(args.test_dag, docker=not args.no_docker)
        print(json.dumps(result))
        sys.exit(0 if result.get("status") == "PASS" else 1)

    parser.print_help()

if __name__ == "__main__":
    main()
