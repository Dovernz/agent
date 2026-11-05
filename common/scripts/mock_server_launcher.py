#!/usr/bin/env python3
"""
mock_server_launcher.py
Instant Lightweight API Mock Server for Antigravity Agent Hub.

Features:
- 100% Zero-Dependency (built on standard library http.server).
- Ingests OpenAPI 3.0 / Swagger JSON specifications.
- Regex-based dynamic URL path parameter matching (e.g. /api/v1/users/{id}).
- In-memory stateful CRUD simulation (GET, POST, PUT, PATCH, DELETE).
- Built-in full CORS support for modern frontend dev (React, Vue, Svelte).
- Diagnostic routes: /_mock/health, /_mock/routes, /_mock/reset.
- Auto-generation of starter openapi.json template if none exists.
"""

import os
import sys
import json
import re
import time
import argparse
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# UTF-8 IO encoding for Windows compatibility
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass


def generate_mock_from_schema(schema, parent_name=""):
    """Recursively generates mock JSON data from an OpenAPI schema definition."""
    if not isinstance(schema, dict):
        return "sample_value"

    schema_type = schema.get("type")
    
    # Check for direct example
    if "example" in schema:
        return schema["example"]

    if schema_type == "string":
        fmt = schema.get("format", "")
        prop_lower = parent_name.lower()
        if fmt == "date" or "date" in prop_lower:
            return "2026-11-05"
        elif fmt == "date-time" or "time" in prop_lower:
            return "2026-11-05T12:00:00Z"
        elif fmt == "email" or "email" in prop_lower:
            return "user@example.com"
        elif "phone" in prop_lower or "tel" in prop_lower:
            return "0901234567"
        elif "name" in prop_lower:
            return "Nguyễn Văn Mẫu"
        elif "status" in prop_lower:
            return schema.get("enum", ["active", "pending"])[0] if "enum" in schema else "active"
        elif "id" in prop_lower:
            return f"mock-{int(time.time()) % 10000}"
        return f"sample_{parent_name or 'text'}"

    elif schema_type in ("integer", "number"):
        prop_lower = parent_name.lower()
        if "id" in prop_lower:
            return 101
        elif "price" in prop_lower or "cost" in prop_lower:
            return 500000
        return 1

    elif schema_type == "boolean":
        return True

    elif schema_type == "array":
        items_schema = schema.get("items", {})
        sample_item = generate_mock_from_schema(items_schema, parent_name=parent_name)
        return [sample_item]

    elif schema_type == "object" or "properties" in schema:
        props = schema.get("properties", {})
        result = {}
        for prop_name, prop_schema in props.items():
            result[prop_name] = generate_mock_from_schema(prop_schema, parent_name=prop_name)
        if not result and "additionalProperties" in schema:
            return {"sample_key": "sample_value"}
        return result

    return {"status": "ok", "message": "sample response"}


class MockDataRegistry:
    """Stores routes compiled from OpenAPI spec and handles dynamic path matching."""

    def __init__(self, spec_data=None):
        self.routes = []  # list of (method, regex_pattern, param_names, response_def, path_template)
        self.memory_store = {}  # {resource_key: [items]}
        self.spec_title = "Antigravity Mock API"
        self.start_time = time.time()
        
        if spec_data:
            self.load_openapi(spec_data)

    def load_openapi(self, spec):
        self.spec_title = spec.get("info", {}).get("title", "Antigravity Mock API")
        paths = spec.get("paths", {})
        
        for path_template, methods in paths.items():
            # Convert OpenAPI /path/{id}/detail to regex ^/path/(?P<id>[^/]+)/detail$
            param_names = re.findall(r'\{([a-zA-Z0-9_]+)\}', path_template)
            pattern_str = "^" + re.sub(r'\{[a-zA-Z0-9_]+\}', r'([^/]+)', path_template) + "$"
            regex_pat = re.compile(pattern_str)

            for method, op_def in methods.items():
                if method.lower() not in ("get", "post", "put", "patch", "delete", "options"):
                    continue
                
                # Determine mock response payload & status code
                responses = op_def.get("responses", {})
                status_code = 200
                res_payload = None

                for code_str in ("200", "201", "204", "default"):
                    if code_str in responses:
                        status_code = int(code_str) if code_str.isdigit() else 200
                        res_obj = responses[code_str]
                        
                        # Look inside content -> application/json
                        content = res_obj.get("content", {})
                        app_json = content.get("application/json", {})
                        if "example" in app_json:
                            res_payload = app_json["example"]
                        elif "schema" in app_json:
                            res_payload = generate_mock_from_schema(app_json["schema"])
                        elif "schema" in res_obj:
                            res_payload = generate_mock_from_schema(res_obj["schema"])
                        else:
                            res_payload = {"message": res_obj.get("description", "OK")}
                        break

                if res_payload is None:
                    res_payload = {"status": "success", "endpoint": path_template}

                self.routes.append({
                    "method": method.upper(),
                    "regex": regex_pat,
                    "param_names": param_names,
                    "template": path_template,
                    "status_code": status_code,
                    "default_payload": res_payload,
                    "summary": op_def.get("summary", path_template)
                })

    def match(self, method, request_path):
        """Find matching route definition and extract path params."""
        # Normalize trailing slash
        norm_path = request_path.rstrip('/') if request_path != '/' else '/'
        
        for route in self.routes:
            if route["method"] != method.upper():
                continue
            
            m = route["regex"].match(norm_path)
            if m:
                path_params = {}
                for idx, name in enumerate(route["param_names"]):
                    path_params[name] = m.group(idx + 1)
                return route, path_params
                
        return None, {}


def create_sample_spec(output_path="openapi.json"):
    """Generates a clean starter OpenAPI 3.0 specification file."""
    spec = {
        "openapi": "3.0.3",
        "info": {
            "title": "Starter Mock API Spec",
            "version": "1.0.0",
            "description": "Auto-generated OpenAPI spec by Antigravity Mock Server Launcher."
        },
        "paths": {
            "/api/v1/health": {
                "get": {
                    "summary": "Health check status",
                    "responses": {
                        "200": {
                            "description": "System is healthy",
                            "content": {
                                "application/json": {
                                    "example": {"status": "ok", "service": "api-backend", "uptime_sec": 3600}
                                }
                            }
                        }
                    }
                }
            },
            "/api/v1/items": {
                "get": {
                    "summary": "List all items",
                    "responses": {
                        "200": {
                            "description": "A list of items",
                            "content": {
                                "application/json": {
                                    "example": [
                                        {"id": 1, "name": "Mục mẫu 1", "category": "medical", "active": True},
                                        {"id": 2, "name": "Mục mẫu 2", "category": "equipment", "active": True}
                                    ]
                                }
                            }
                        }
                    }
                },
                "post": {
                    "summary": "Create a new item",
                    "responses": {
                        "201": {
                            "description": "Item created successfully",
                            "content": {
                                "application/json": {
                                    "example": {"id": 103, "name": "Mục mới", "created_at": "2026-11-05T12:00:00Z"}
                                }
                            }
                        }
                    }
                }
            },
            "/api/v1/items/{id}": {
                "get": {
                    "summary": "Get item detail by ID",
                    "responses": {
                        "200": {
                            "description": "Item detail",
                            "content": {
                                "application/json": {
                                    "example": {"id": 1, "name": "Mục mẫu chi tiết", "price": 450000, "status": "active"}
                                }
                            }
                        }
                    }
                },
                "put": {
                    "summary": "Update item by ID",
                    "responses": {
                        "200": {
                            "description": "Item updated",
                            "content": {
                                "application/json": {
                                    "example": {"id": 1, "status": "updated", "updated_at": "2026-11-05T12:00:00Z"}
                                }
                            }
                        }
                    }
                },
                "delete": {
                    "summary": "Delete item by ID",
                    "responses": {
                        "200": {
                            "description": "Item deleted",
                            "content": {
                                "application/json": {
                                    "example": {"success": True, "message": "Đã xóa thành công"}
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(spec, f, indent=2, ensure_ascii=False)
    return output_path


def make_request_handler(registry: MockDataRegistry):
    class MockHTTPRequestHandler(BaseHTTPRequestHandler):
        def _set_cors_headers(self, status_code=200, content_type="application/json"):
            self.send_response(status_code)
            self.send_header("Content-Type", f"{content_type}; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, PATCH, DELETE, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization, X-Requested-With, Accept, Origin")
            self.end_headers()

        def do_OPTIONS(self):
            # Preflight response
            self._set_cors_headers(status_code=204)

        def log_message(self, format, *args):
            # Formatted compact log
            sys.stdout.write(f"[MockServer] {self.command} {self.path} - {format % args}\n")
            sys.stdout.flush()

        def _read_json_body(self):
            try:
                length = int(self.headers.get("Content-Length", 0))
                if length > 0:
                    raw = self.rfile.read(length).decode("utf-8")
                    return json.loads(raw)
            except Exception:
                pass
            return {}

        def _send_json_response(self, status_code, data):
            self._set_cors_headers(status_code)
            body = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
            self.wfile.write(body)

        def handle_internal_routes(self, parsed_url):
            path = parsed_url.path
            if path == "/_mock/health":
                self._send_json_response(200, {
                    "status": "UP",
                    "title": registry.spec_title,
                    "routes_registered": len(registry.routes),
                    "uptime_seconds": round(time.time() - registry.start_time, 2)
                })
                return True
            elif path == "/_mock/routes":
                routes_summary = [
                    {
                        "method": r["method"],
                        "endpoint": r["template"],
                        "summary": r["summary"],
                        "status_code": r["status_code"]
                    }
                    for r in registry.routes
                ]
                self._send_json_response(200, {"routes": routes_summary})
                return True
            elif path == "/_mock/reset" and self.command == "POST":
                registry.memory_store.clear()
                self._send_json_response(200, {"message": "Memory store reset successfully"})
                return True
            return False

        def do_GET(self):
            parsed = urlparse(self.path)
            if self.handle_internal_routes(parsed):
                return

            route, path_params = registry.match("GET", parsed.path)
            if route:
                payload = route["default_payload"]
                # If path params exist, merge them if payload is dict
                if path_params and isinstance(payload, dict):
                    payload = dict(payload)
                    for k, v in path_params.items():
                        payload[k] = int(v) if v.isdigit() else v
                self._send_json_response(route["status_code"], payload)
            else:
                self._send_json_response(404, {
                    "error": "Not Found",
                    "message": f"Route GET {parsed.path} not defined in OpenAPI spec",
                    "registered_routes_url": "/_mock/routes"
                })

        def do_POST(self):
            parsed = urlparse(self.path)
            if self.handle_internal_routes(parsed):
                return

            route, path_params = registry.match("POST", parsed.path)
            body = self._read_json_body()
            
            if route:
                payload = route["default_payload"]
                if isinstance(payload, dict):
                    merged = dict(payload)
                    if isinstance(body, dict):
                        merged.update(body)
                    if "id" not in merged:
                        merged["id"] = int(time.time() % 100000)
                    payload = merged
                self._send_json_response(route["status_code"], payload)
            else:
                self._send_json_response(404, {"error": "Not Found", "message": f"Route POST {parsed.path} not matched"})

        def do_PUT(self):
            parsed = urlparse(self.path)
            route, path_params = registry.match("PUT", parsed.path)
            body = self._read_json_body()
            if route:
                payload = route["default_payload"]
                if isinstance(payload, dict):
                    merged = dict(payload)
                    if isinstance(body, dict):
                        merged.update(body)
                    merged.update(path_params)
                    payload = merged
                self._send_json_response(route["status_code"], payload)
            else:
                self._send_json_response(404, {"error": "Not Found", "message": f"Route PUT {parsed.path} not matched"})

        def do_PATCH(self):
            parsed = urlparse(self.path)
            route, path_params = registry.match("PATCH", parsed.path)
            body = self._read_json_body()
            if route:
                payload = route["default_payload"]
                if isinstance(payload, dict):
                    merged = dict(payload)
                    if isinstance(body, dict):
                        merged.update(body)
                    merged.update(path_params)
                    payload = merged
                self._send_json_response(route["status_code"], payload)
            else:
                self._send_json_response(404, {"error": "Not Found", "message": f"Route PATCH {parsed.path} not matched"})

        def do_DELETE(self):
            parsed = urlparse(self.path)
            route, path_params = registry.match("DELETE", parsed.path)
            if route:
                payload = route["default_payload"]
                if isinstance(payload, dict):
                    payload = dict(payload)
                    payload.update(path_params)
                self._send_json_response(route["status_code"], payload)
            else:
                self._send_json_response(200, {"success": True, "deleted_path": parsed.path})

    return MockHTTPRequestHandler


def run_mock_server(spec_path=None, host="0.0.0.0", port=8089, auto_sample=False):
    spec_data = None
    
    if spec_path and os.path.exists(spec_path):
        try:
            with open(spec_path, "r", encoding="utf-8") as f:
                spec_data = json.load(f)
            print(f"[+] Đã nạp thành công OpenAPI spec từ: {spec_path}")
        except Exception as e:
            print(f"[!] Lỗi đọc OpenAPI spec JSON: {e}", file=sys.stderr)
            sys.exit(1)
    elif auto_sample or not spec_path:
        default_file = "openapi_sample.json"
        print(f"[*] Không tìm thấy spec, tự động sinh tệp mẫu chuẩn: {default_file}")
        create_sample_spec(default_file)
        with open(default_file, "r", encoding="utf-8") as f:
            spec_data = json.load(f)
    else:
        print(f"[!] Không tìm thấy tệp OpenAPI spec tại: {spec_path}", file=sys.stderr)
        sys.exit(1)

    registry = MockDataRegistry(spec_data)
    handler = make_request_handler(registry)
    
    server_address = (host, port)
    try:
        httpd = HTTPServer(server_address, handler)
    except OSError as e:
        print(f"[!] Cổng {port} đang bị chiếm dụng: {e}", file=sys.stderr)
        sys.exit(1)

    print("\n" + "=" * 65)
    print(f"🚀 ANTIGRAVITY INSTANT API MOCK SERVER ĐÃ KHỞI CHẠY!")
    print(f"📍 Địa chỉ: http://localhost:{port} (Binding: {host}:{port})")
    print(f"📚 Tiêu đề Spec: {registry.spec_title}")
    print(f"🛣️  Tổng số Endpoints hỗ trợ: {len(registry.routes)}")
    print(f"🏥 Kiểm tra sức khỏe: http://localhost:{port}/_mock/health")
    print(f"📋 Danh sách API:       http://localhost:{port}/_mock/routes")
    print("=" * 65 + "\n")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[*] Đang tắt Mock Server an toàn...")
        httpd.server_close()
        print("[+] Đã dừng Mock Server.")


def main():
    parser = argparse.ArgumentParser(description="Instant API Mock Server for Antigravity Agent Hub")
    parser.add_argument("--spec", help="Đường dẫn tệp openapi.json hoặc swagger.json")
    parser.add_argument("--port", type=int, default=8089, help="Cổng chạy mock server (mặc định: 8089)")
    parser.add_argument("--host", default="0.0.0.0", help="Địa chỉ host binding (mặc định: 0.0.0.0)")
    parser.add_argument("--generate-sample", help="Sinh tệp starter openapi.json mẫu và thoát")
    parser.add_argument("--sample", action="store_true", help="Tự động sinh và chạy với spec mẫu")
    args = parser.parse_args()

    if args.generate_sample:
        out = create_sample_spec(args.generate_sample)
        print(f"[+] Đã tạo OpenAPI spec mẫu tại: {out}")
        return

    # Check for common openapi locations if not specified
    spec_path = args.spec
    if not spec_path:
        for cand in ["openapi.json", "docs/openapi.json", "api/openapi.json"]:
            if os.path.exists(cand):
                spec_path = cand
                break

    run_mock_server(spec_path=spec_path, host=args.host, port=args.port, auto_sample=args.sample or not spec_path)


if __name__ == "__main__":
    main()
