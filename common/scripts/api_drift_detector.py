#!/usr/bin/env python3
"""
api_drift_detector.py
Automated API Contract Drift Detector for Antigravity Agent Hub.

Compares live backend code routes (FastAPI, Flask, Django, Express) against
OpenAPI / Swagger specifications (or frontend API calls) to detect:
- Missing routes in OpenAPI spec (untested / undocumented endpoints)
- Ghost routes in OpenAPI spec (endpoints deleted or never implemented)
- HTTP method mismatches (e.g. GET vs POST)
- Path parameter discrepancies (e.g. {id} vs {patient_id})

Zero-dependency standard library implementation (ast, json, re, pathlib).
Supports both human-readable terminal output and Zero-Fat M2M JSON.
"""

import os
import sys
import ast
import re
import json
import argparse
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Any

# Ensure UTF-8 standard IO for Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass


def normalize_path(path: str) -> Tuple[str, List[str]]:
    """
    Normalizes URL path into a standard template and extracts param names.
    Examples:
      /api/v1/patients/{id} -> (/api/v1/patients/{*}, ['id'])
      api/v1/patients/<int:pk>/ -> (/api/v1/patients/{*}, ['pk'])
      /api/v1/patients/:id -> (/api/v1/patients/{*}, ['id'])
    """
    if not path.startswith('/'):
        path = '/' + path
    path = path.rstrip('/')
    if not path:
        path = '/'

    params = []

    # OpenAPI style: {param}
    def replace_curly(match):
        pname = match.group(1).strip()
        params.append(pname)
        return "{*}"

    # Django style: <int:param> or <param>
    def replace_angle(match):
        raw = match.group(1).strip()
        pname = raw.split(':')[-1] if ':' in raw else raw
        params.append(pname)
        return "{*}"

    # Express style: :param
    def replace_colon(match):
        pname = match.group(1).strip()
        params.append(pname)
        return "{*}"

    norm = re.sub(r'\{([^}]+)\}', replace_curly, path)
    norm = re.sub(r'<([^>]+)>', replace_angle, norm)
    norm = re.sub(r':([a-zA-Z_][a-zA-Z0-9_]*)', replace_colon, norm)

    return norm, params


class OpenApiSpecParser:
    """Parses OpenAPI 3.x or Swagger 2.0 JSON specifications."""

    def __init__(self, spec_path: Path):
        self.spec_path = spec_path
        self.routes: Dict[Tuple[str, str], Dict[str, Any]] = {}

    def parse(self) -> Dict[Tuple[str, str], Dict[str, Any]]:
        if not self.spec_path.exists():
            raise FileNotFoundError(f"Spec file not found: {self.spec_path}")

        with open(self.spec_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        paths = data.get("paths", {})
        for path_str, path_item in paths.items():
            if not isinstance(path_item, dict):
                continue

            for method_str, op_item in path_item.items():
                method_upper = method_str.upper()
                if method_upper not in {"GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"}:
                    continue

                norm_path, params = normalize_path(path_str)
                op_id = op_item.get("operationId", "") if isinstance(op_item, dict) else ""
                summary = op_item.get("summary", "") if isinstance(op_item, dict) else ""

                self.routes[(method_upper, norm_path)] = {
                    "raw_path": path_str,
                    "normalized_path": norm_path,
                    "method": method_upper,
                    "params": params,
                    "operationId": op_id,
                    "summary": summary,
                    "source": str(self.spec_path)
                }

        return self.routes


class CodeRouteScanner:
    """Scans Python (FastAPI/Flask/Django) and JS/TS route definitions."""

    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.routes: Dict[Tuple[str, str], Dict[str, Any]] = {}

    def scan(self) -> Dict[Tuple[str, str], Dict[str, Any]]:
        self._scan_python_files()
        self._scan_js_ts_files()
        return self.routes

    def _scan_python_files(self):
        ignore_dirs = {'.git', 'node_modules', '.venv', 'venv', '__pycache__', 'dist', 'build'}
        for py_file in self.root_dir.rglob('*.py'):
            if any(part in ignore_dirs for part in py_file.parts):
                continue
            try:
                with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Fast pre-check to avoid AST parsing irrelevant files
                if not any(k in content for k in ['@app.', '@router.', '@bp.', 'path(', 're_path(', 'api_view']):
                    continue

                tree = ast.parse(content, filename=str(py_file))
                self._parse_python_ast(tree, py_file)
            except Exception:
                # Fallback to regex if AST fails on syntax dialect
                self._regex_scan_python(content, py_file)

    def _parse_python_ast(self, tree: ast.AST, file_path: Path):
        http_methods = {"get", "post", "put", "delete", "patch", "options", "head"}

        for node in ast.walk(tree):
            # FastAPI / Flask / Starlette style decorators: @router.get("/items")
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                for dec in node.decorator_list:
                    method = None
                    path = None

                    # @router.get(...) or @app.post(...)
                    if isinstance(dec, ast.Call) and isinstance(dec.func, ast.Attribute):
                        attr_name = dec.func.attr.lower()
                        if attr_name in http_methods:
                            method = attr_name.upper()
                            if dec.args and isinstance(dec.args[0], ast.Constant) and isinstance(dec.args[0].value, str):
                                path = dec.args[0].value
                            elif dec.keywords:
                                for kw in dec.keywords:
                                    if kw.arg in ('path', 'rule') and isinstance(kw.value, ast.Constant):
                                        path = str(kw.value.value)

                    # Flask @bp.route('/items', methods=['GET', 'POST'])
                    elif isinstance(dec, ast.Call) and isinstance(dec.func, ast.Attribute) and dec.func.attr == 'route':
                        if dec.args and isinstance(dec.args[0], ast.Constant):
                            path = str(dec.args[0].value)
                        methods_list = ['GET']
                        for kw in dec.keywords:
                            if kw.arg == 'methods' and isinstance(kw.value, (ast.List, ast.Tuple)):
                                methods_list = [
                                    elt.value.upper() for elt in kw.value.elts 
                                    if isinstance(elt, ast.Constant) and isinstance(elt.value, str)
                                ]
                        if path:
                            for m in methods_list:
                                norm_p, params = normalize_path(path)
                                self.routes[(m, norm_p)] = {
                                    "raw_path": path,
                                    "normalized_path": norm_p,
                                    "method": m,
                                    "params": params,
                                    "handler": node.name,
                                    "source": f"{file_path}:{node.lineno}"
                                }

                    if method and path:
                        norm_p, params = normalize_path(path)
                        self.routes[(method, norm_p)] = {
                            "raw_path": path,
                            "normalized_path": norm_p,
                            "method": method,
                            "params": params,
                            "handler": node.name,
                            "source": f"{file_path}:{node.lineno}"
                        }

            # Django style: path('api/v1/patients/', views.PatientListView.as_view())
            elif isinstance(node, ast.Call):
                func_id = getattr(node.func, 'id', '')
                if func_id in ('path', 're_path') and node.args:
                    first_arg = node.args[0]
                    if isinstance(first_arg, ast.Constant) and isinstance(first_arg.value, str):
                        raw_path = first_arg.value
                        norm_p, params = normalize_path(raw_path)
                        # Django paths usually support multiple methods or default to GET/POST
                        self.routes[("DJANGO", norm_p)] = {
                            "raw_path": raw_path,
                            "normalized_path": norm_p,
                            "method": "DJANGO",
                            "params": params,
                            "handler": "django_url_pattern",
                            "source": f"{file_path}:{node.lineno}"
                        }

    def _regex_scan_python(self, content: str, file_path: Path):
        # Fallback regex for FastAPI / Flask
        pattern = r'@(?:app|router|bp)\.(get|post|put|delete|patch)\s*\(\s*["\']([^"\']+)["\']'
        for match in re.finditer(pattern, content, re.IGNORECASE):
            method = match.group(1).upper()
            raw_path = match.group(2)
            norm_p, params = normalize_path(raw_path)
            self.routes[(method, norm_p)] = {
                "raw_path": raw_path,
                "normalized_path": norm_p,
                "method": method,
                "params": params,
                "handler": "regex_detected",
                "source": str(file_path)
            }

    def _scan_js_ts_files(self):
        ignore_dirs = {'.git', 'node_modules', '.next', 'dist', 'build', '.coverage'}
        for ext in ['*.ts', '*.tsx', '*.js', '*.jsx']:
            for js_file in self.root_dir.rglob(ext):
                if any(part in ignore_dirs for part in js_file.parts):
                    continue
                try:
                    with open(js_file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()

                    # Express / router: app.get('/api/...', ...)
                    expr_pattern = r'(?:app|router)\.(get|post|put|delete|patch)\s*\(\s*["\']([^"\']+)["\']'
                    for match in re.finditer(expr_pattern, content):
                        method = match.group(1).upper()
                        raw_path = match.group(2)
                        norm_p, params = normalize_path(raw_path)
                        self.routes[(method, norm_p)] = {
                            "raw_path": raw_path,
                            "normalized_path": norm_p,
                            "method": method,
                            "params": params,
                            "handler": "express_handler",
                            "source": str(js_file)
                        }
                except Exception:
                    pass


def detect_drift(
    spec_routes: Dict[Tuple[str, str], Dict[str, Any]],
    code_routes: Dict[Tuple[str, str], Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Compares spec_routes and code_routes, isolating discrepancies.
    """
    drifts = []

    # Map paths for quick cross-method lookup
    spec_paths: Dict[str, Set[str]] = {}
    for (m, p) in spec_routes:
        spec_paths.setdefault(p, set()).add(m)

    code_paths: Dict[str, Set[str]] = {}
    for (m, p) in code_routes:
        code_paths.setdefault(p, set()).add(m)

    # 1. Routes in Code but Missing from Spec
    for (method, norm_path), code_info in code_routes.items():
        if method == "DJANGO":
            # For Django URL patterns without explicit method decorator, check if path exists in spec
            if norm_path not in spec_paths:
                drifts.append({
                    "drift_type": "MISSING_IN_SPEC",
                    "method": "ANY",
                    "path": code_info["raw_path"],
                    "normalized_path": norm_path,
                    "source": code_info["source"],
                    "details": "Django URL pattern implemented in backend but missing from OpenAPI spec"
                })
        else:
            if (method, norm_path) not in spec_routes:
                if norm_path in spec_paths:
                    drifts.append({
                        "drift_type": "METHOD_MISMATCH",
                        "method": method,
                        "expected_methods": list(spec_paths[norm_path]),
                        "path": code_info["raw_path"],
                        "normalized_path": norm_path,
                        "source": code_info["source"],
                        "details": f"Path exists in spec but method '{method}' is not documented (Spec has: {list(spec_paths[norm_path])})"
                    })
                else:
                    drifts.append({
                        "drift_type": "MISSING_IN_SPEC",
                        "method": method,
                        "path": code_info["raw_path"],
                        "normalized_path": norm_path,
                        "source": code_info["source"],
                        "details": f"Endpoint implemented in code ({method} {code_info['raw_path']}) is missing from OpenAPI spec"
                    })

    # 2. Ghost routes in Spec (Documented but Missing from Code)
    for (method, norm_path), spec_info in spec_routes.items():
        if (method, norm_path) not in code_routes and ("DJANGO", norm_path) not in code_routes:
            if norm_path not in code_paths:
                drifts.append({
                    "drift_type": "GHOST_IN_CODE",
                    "method": method,
                    "path": spec_info["raw_path"],
                    "normalized_path": norm_path,
                    "source": spec_info["source"],
                    "details": f"Route documented in OpenAPI spec ({method} {spec_info['raw_path']}) was not found in code"
                })

    # 3. Parameter name verification for shared routes
    for (method, norm_path), spec_info in spec_routes.items():
        code_info = code_routes.get((method, norm_path))
        if code_info and spec_info.get("params") and code_info.get("params"):
            spec_params = spec_info["params"]
            code_params = code_info["params"]
            if spec_params != code_params:
                drifts.append({
                    "drift_type": "PARAM_MISMATCH",
                    "method": method,
                    "path": spec_info["raw_path"],
                    "normalized_path": norm_path,
                    "source": f"Code: {code_info['source']} vs Spec: {spec_info['source']}",
                    "details": f"Parameter names differ: Spec uses {spec_params}, Code uses {code_params}"
                })

    status = "PASS" if not drifts else "DRIFT_DETECTED"

    return {
        "status": status,
        "spec_route_count": len(spec_routes),
        "code_route_count": len(code_routes),
        "drift_count": len(drifts),
        "drifts": drifts
    }


def generate_draft_openapi(code_routes: Dict[Tuple[str, str], Dict[str, Any]], title: str = "Generated API Spec") -> Dict[str, Any]:
    """Generates a starter OpenAPI 3.0.3 schema from detected code routes."""
    paths: Dict[str, Any] = {}

    for (method, norm_path), route in sorted(code_routes.items(), key=lambda x: x[0][1]):
        raw_path = route["raw_path"]
        if not raw_path.startswith('/'):
            raw_path = '/' + raw_path

        m_lower = method.lower() if method != "DJANGO" else "get"
        paths.setdefault(raw_path, {})[m_lower] = {
            "summary": f"Handler: {route.get('handler', 'auto_generated')}",
            "responses": {
                "200": {
                    "description": "Successful operation"
                }
            }
        }

    return {
        "openapi": "3.0.3",
        "info": {
            "title": title,
            "version": "1.0.0",
            "description": "Auto-extracted from backend source code via api_drift_detector.py"
        },
        "paths": paths
    }


def print_human_report(result: Dict[str, Any]):
    print("\n" + "=" * 70)
    print(" 🛰️  API CONTRACT DRIFT DETECTOR REPORT")
    print("=" * 70)
    print(f" Spec Routes Found : {result['spec_route_count']}")
    print(f" Code Routes Found : {result['code_route_count']}")
    print(f" Drifts Detected   : {result['drift_count']}")
    print(f" Status            : {'[PASS] 0 Contract Drifts' if result['status'] == 'PASS' else '[FAIL] Drift Detected'}")
    print("-" * 70)

    if result["drifts"]:
        print(f"{'TYPE':<18} | {'METHOD':<7} | {'PATH':<30} | {'DETAILS'}")
        print("-" * 70)
        for d in result["drifts"]:
            m = d.get("method", "*")
            p = d.get("path", "")
            if len(p) > 28:
                p = p[:25] + "..."
            dtype = d.get("drift_type", "")
            print(f"{dtype:<18} | {m:<7} | {p:<30} | {d['details']}")
        print("-" * 70)
    else:
        print("✅ Backend code routes and OpenAPI specification are 100% in sync.")
    print("=" * 70 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="API Contract Drift Detector for Antigravity Agent Hub",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--spec", "-s", type=str, help="Path to openapi.json or swagger.json")
    parser.add_argument("--code", "-c", type=str, default=".", help="Root directory of backend code (default: .)")
    parser.add_argument("--json", action="store_true", help="Emit Zero-Fat M2M JSON output")
    parser.add_argument("--strict", action="store_true", help="Exit with code 1 if drifts are detected")
    parser.add_argument("--generate-spec", type=str, metavar="OUTPUT_PATH", help="Generate draft openapi.json from scanned code")

    args = parser.parse_args()

    code_root = Path(args.code).resolve()
    if not code_root.exists():
        print(f"Error: Code directory does not exist: {code_root}", file=sys.stderr)
        sys.exit(1)

    scanner = CodeRouteScanner(code_root)
    code_routes = scanner.scan()

    if args.generate_spec:
        out_spec_path = Path(args.generate_spec).resolve()
        spec_content = generate_draft_openapi(code_routes, title=f"API Spec for {code_root.name}")
        with open(out_spec_path, 'w', encoding='utf-8') as f:
            json.dump(spec_content, f, indent=2, ensure_ascii=False)
        print(f"✅ Generated OpenAPI draft ({len(code_routes)} routes) -> {out_spec_path}")
        sys.exit(0)

    spec_routes: Dict[Tuple[str, str], Dict[str, Any]] = {}
    if args.spec:
        spec_file = Path(args.spec).resolve()
        parser_obj = OpenApiSpecParser(spec_file)
        spec_routes = parser_obj.parse()
    else:
        # Check if default openapi.json exists in code_root
        candidate = code_root / "openapi.json"
        if candidate.exists():
            parser_obj = OpenApiSpecParser(candidate)
            spec_routes = parser_obj.parse()
        else:
            print(f"Notice: No OpenAPI spec provided (--spec). Scanned {len(code_routes)} backend code routes.")
            if args.json:
                print(json.dumps({
                    "status": "SCANNED_ONLY",
                    "code_routes_count": len(code_routes),
                    "routes": [r for r in code_routes.values()]
                }, indent=2))
            else:
                print(f"Found {len(code_routes)} routes in {code_root}. Use --generate-spec openapi.json to create a spec.")
            sys.exit(0)

    result = detect_drift(spec_routes, code_routes)

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print_human_report(result)

    if args.strict and result["status"] != "PASS":
        sys.exit(1)


if __name__ == "__main__":
    main()
