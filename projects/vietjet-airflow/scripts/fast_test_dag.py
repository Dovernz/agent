#!/usr/bin/env python3
"""
Ultra-fast, zero-token overhead Airflow DAG Validator.
Runs static AST checks, cycle detection, Vietjet standards, and Docker DagBag verification.
Outputs machine-readable compact JSON.
"""

import sys
import os
import ast
import json
import argparse
import subprocess
from typing import Dict, Any, List

def run_ast_and_syntax_check(code_str: str) -> Dict[str, Any]:
    try:
        tree = ast.parse(code_str)
        return {"status": "OK", "tree": tree}
    except SyntaxError as e:
        return {
            "status": "FAIL",
            "stage": "ast_syntax",
            "errors": [{
                "line": e.lineno,
                "type": "SyntaxError",
                "message": e.msg or str(e)
            }]
        }

def analyze_dag_ast(tree: ast.AST) -> Dict[str, Any]:
    dag_ids = []
    task_ids = set()
    dependencies = [] # list of (source, target)
    has_pendulum = False
    has_catchup = False
    has_tags = False
    owner = None

    for node in ast.walk(tree):
        # Check imports
        if isinstance(node, ast.Import):
            for alias in node.names:
                if "pendulum" in alias.name:
                    has_pendulum = True
        elif isinstance(node, ast.ImportFrom):
            if node.module and "pendulum" in node.module:
                has_pendulum = True

        # Check @dag decorator or DAG() instantiation
        if isinstance(node, ast.Call):
            func_name = ""
            if isinstance(node.func, ast.Name):
                func_name = node.func.id
            elif isinstance(node.func, ast.Attribute):
                func_name = node.func.attr
            
            if func_name == "dag" or func_name == "DAG":
                # Look for dag_id argument
                for kw in node.keywords:
                    if kw.arg == "dag_id" and isinstance(kw.value, ast.Constant):
                        dag_ids.append(str(kw.value.value))
                    elif kw.arg == "catchup":
                        has_catchup = True
                    elif kw.arg == "tags":
                        has_tags = True
                if node.args and isinstance(node.args[0], ast.Constant):
                    dag_ids.append(str(node.args[0].value))

        # Check @task decorator or Operator task_id
        if isinstance(node, ast.Call):
            for kw in node.keywords:
                if kw.arg == "task_id" and isinstance(kw.value, ast.Constant):
                    task_ids.add(str(kw.value.value))
                elif kw.arg == "owner" and isinstance(kw.value, ast.Constant):
                    owner = str(kw.value.value)

        # Check TaskFlow @task function defs
        if isinstance(node, ast.FunctionDef):
            for dec in node.decorator_list:
                dec_id = ""
                if isinstance(dec, ast.Name):
                    dec_id = dec.id
                elif isinstance(dec, ast.Call) and isinstance(dec.func, ast.Name):
                    dec_id = dec.func.id
                if dec_id == "task":
                    task_ids.add(node.name)

        # Check binary bitshift >> or <<
        if isinstance(node, ast.BinOp):
            if isinstance(node.op, ast.RShift): # a >> b
                left = getattr(node.left, "id", None)
                right = getattr(node.right, "id", None)
                if left and right:
                    dependencies.append((left, right))
            elif isinstance(node.op, ast.LShift): # a << b
                left = getattr(node.left, "id", None)
                right = getattr(node.right, "id", None)
                if left and right:
                    dependencies.append((right, left))

    # Cycle check via DFS
    graph = {}
    for src, dst in dependencies:
        graph.setdefault(src, []).append(dst)

    visited = {}
    cycle_detected = False
    cycle_path = []

    def dfs(node, path):
        nonlocal cycle_detected, cycle_path
        visited[node] = 1 # visiting
        path.append(node)
        for neighbor in graph.get(node, []):
            if visited.get(neighbor) == 1:
                cycle_detected = True
                cycle_path = list(path) + [neighbor]
                return
            if visited.get(neighbor) == 0 or neighbor not in visited:
                dfs(neighbor, path)
        visited[node] = 2 # visited
        path.pop()

    for node in list(graph.keys()):
        if node not in visited:
            dfs(node, [])
        if cycle_detected:
            break

    if cycle_detected:
        return {
            "status": "FAIL",
            "stage": "cycle_check",
            "errors": [{
                "type": "CyclicDependencyError",
                "message": f"Cycle detected in DAG task flow: {' -> '.join(cycle_path)}"
            }]
        }

    warnings = []
    if not has_pendulum:
        warnings.append("Missing pendulum timezone. Recommend pendulum.timezone('Asia/Ho_Chi_Minh').")
    if not has_tags:
        warnings.append("No tags specified for DAG.")

    return {
        "status": "PASS",
        "dag_id": dag_ids[0] if dag_ids else "unknown_dag_id",
        "task_count": len(task_ids),
        "tasks": sorted(list(task_ids)),
        "warnings": warnings,
        "owner": owner
    }

def verify_dag_in_docker(file_path: str) -> Dict[str, Any]:
    container = "test-airflow-webserver-1"
    check_docker = subprocess.run(
        ["docker", "ps", "--filter", f"name={container}", "--format", "{{.Names}}"],
        capture_output=True, text=True
    )
    if container not in check_docker.stdout:
        return {"status": "SKIPPED", "reason": "Docker test container not currently running"}

    # Copy dag file into container tmp
    abs_path = os.path.abspath(file_path)
    target_in_container = "/tmp/_test_check_dag.py"
    copy_proc = subprocess.run(["docker", "cp", abs_path, f"{container}:{target_in_container}"], capture_output=True, text=True)
    if copy_proc.returncode != 0:
        return {"status": "SKIPPED", "reason": f"Failed to copy file to container: {copy_proc.stderr.strip()}"}

    # Execute DagBag load with proper multiline script
    script = (
        "import sys\n"
        "from airflow.models import DagBag\n"
        "bag = DagBag('/tmp/_test_check_dag.py', include_examples=False)\n"
        "errors = [f'{k}: {v}' for k, v in bag.import_errors.items()]\n"
        "print('DAG_COUNT=' + str(len(bag.dags)))\n"
        "if errors:\n"
        "    print('ERRORS=' + ';;;'.join(errors))\n"
        "    sys.exit(1)\n"
    )
    exec_proc = subprocess.run(["docker", "exec", container, "python", "-c", script], capture_output=True, text=True)

    # Clean up file in container
    subprocess.run(["docker", "exec", container, "rm", "-f", target_in_container], capture_output=True)

    if exec_proc.returncode != 0:
        err_msg = exec_proc.stdout.strip() + " " + exec_proc.stderr.strip()
        return {
            "status": "FAIL",
            "stage": "dagbag_load",
            "errors": [{
                "type": "DagBagImportError",
                "message": err_msg
            }]
        }

    return {"status": "PASS", "stage": "dagbag_load"}

def main():
    parser = argparse.ArgumentParser(description="Validate Airflow DAG fast")
    parser.add_argument("dag_file", help="Path to DAG python file")
    parser.add_argument("--docker", action="store_true", help="Force Docker DagBag check if running")
    args = parser.parse_args()

    if not os.path.exists(args.dag_file):
        print(json.dumps({"status": "FAIL", "errors": [{"message": f"File not found: {args.dag_file}"}]}))
        sys.exit(1)

    with open(args.dag_file, "r", encoding="utf-8") as f:
        code = f.read()

    # Step 1: AST & Syntax Check
    ast_res = run_ast_and_syntax_check(code)
    if ast_res["status"] == "FAIL":
        print(json.dumps(ast_res))
        sys.exit(1)

    # Step 2: Semantic & Cycle Check
    sem_res = analyze_dag_ast(ast_res["tree"])
    if sem_res["status"] == "FAIL":
        print(json.dumps(sem_res))
        sys.exit(1)

    # Step 3: Docker DagBag validation (if flag or auto-detect container)
    docker_res = verify_dag_in_docker(args.dag_file)
    if docker_res["status"] == "FAIL":
        sem_res["status"] = "FAIL"
        sem_res["stage"] = "dagbag_load"
        sem_res["errors"] = docker_res["errors"]
        print(json.dumps(sem_res))
        sys.exit(1)

    if docker_res["status"] == "PASS":
        sem_res["docker_dagbag_verified"] = True

    print(json.dumps(sem_res))
    sys.exit(0)

if __name__ == "__main__":
    main()
