#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Output Verifier & Quality Gatekeeper (Zero-Dependency)
==============================================================================
Mục đích: Tự động thẩm định tính đúng đắn, toàn vẹn và an toàn của kết quả
do API ngoài hoặc các Sub-agent sinh ra trước khi đưa vào hệ thống mã nguồn
hoặc báo cáo lên cho người dùng.
==============================================================================
"""

import os
import sys
import ast
import json
import re
import argparse
from pathlib import Path
from typing import Dict, List, Tuple

# Đảm bảo mã hóa UTF-8 cho Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


def verify_python(content: str, file_path: Path) -> Tuple[bool, int, List[str]]:
    """Thẩm định cú pháp và an ninh của mã nguồn Python bằng AST Parser."""
    issues = []
    score = 100

    # 1. Kiểm tra Cú Pháp (Syntax Check qua AST)
    try:
        tree = ast.parse(content, filename=str(file_path))
    except SyntaxError as e:
        return False, 0, [f"Lỗi cú pháp Python (Line {e.lineno}, Col {e.offset}): {e.msg}"]
    except Exception as e:
        return False, 0, [f"Lỗi phân tích cú pháp AST: {e}"]

    # 2. Kiểm tra gọi hàm nguy hiểm qua AST Call Nodes (Không bị nhầm lẫn trong chuỗi)
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                if node.func.id in ("eval", "exec"):
                    issues.append(f"[CẢNH BÁO BẢO MẬT] Gọi hàm nguy hiểm {node.func.id}() tại dòng {getattr(node, 'lineno', '?')}")
                    score -= 25
            elif isinstance(node.func, ast.Attribute):
                # Phát hiện os.system('rm -rf ...')
                if node.func.attr == "system" and isinstance(node.func.value, ast.Name) and node.func.value.id == "os":
                    if node.args and isinstance(node.args[0], ast.Constant):
                        val = str(node.args[0].value).lower()
                        if "rm -rf" in val or "format " in val:
                            issues.append(f"[CẢNH BÁO PHÁ HOẠI] Lệnh hệ thống nguy hiểm os.system({val[:20]}...) tại dòng {getattr(node, 'lineno', '?')}")
                            score -= 40

    # 3. Kiểm tra tính hoàn thiện (Placeholder / TODO chưa xong)
    todos = re.findall(r"#\s*(TODO|FIXME|XXX):?\s*(.*)", content, re.IGNORECASE)
    if len(todos) > 3:
        issues.append(f"[CHƯA HOÀN THIỆN] Phát hiện {len(todos)} điểm đánh dấu TODO/FIXME chưa giải quyết")
        score -= 15

    # 4. Kiểm tra file rỗng hoặc quá ngắn
    if len(content.strip()) < 20:
        issues.append("[NỘI DUNG RỖNG] File code quá ngắn hoặc không chứa logic thực tế")
        score -= 50

    return (score >= 70, max(0, score), issues)


def verify_json(content: str, file_path: Path) -> Tuple[bool, int, List[str]]:
    """Thẩm định tính toàn vẹn của dữ liệu cấu trúc JSON."""
    issues = []
    score = 100

    try:
        data = json.loads(content)
    except json.JSONDecodeError as e:
        return False, 0, [f"Lỗi cú pháp JSON không hợp lệ (Dòng {e.lineno}, Cột {e.colno}): {e.msg}"]

    if data is None:
        return False, 0, ["Dữ liệu JSON là null"]

    if isinstance(data, list):
        if len(data) == 0:
            issues.append("[CẢNH BÁO] Danh sách JSON rỗng (0 bản ghi)")
            score -= 30
        else:
            first_keys = set(data[0].keys()) if isinstance(data[0], dict) else set()
            for idx, item in enumerate(data[1:10], 2):
                if isinstance(item, dict) and set(item.keys()) != first_keys:
                    issues.append(f"[CẤU TRÚC LỆCH] Bản ghi #{idx} có các trường không đồng nhất với bản ghi đầu tiên")
                    score -= 10
                    break
    elif isinstance(data, dict):
        if len(data) == 0:
            issues.append("[CẢNH BÁO] Đối tượng JSON rỗng ({})")
            score -= 30

    return (score >= 70, max(0, score), issues)


def verify_markdown(content: str, file_path: Path) -> Tuple[bool, int, List[str]]:
    """Thẩm định tài liệu Markdown (chống lỗi cụt dòng / cắt cụt code)."""
    issues = []
    score = 100

    code_blocks = re.findall(r"^```", content, re.MULTILINE)
    if len(code_blocks) % 2 != 0:
        issues.append("[CẮT CỤT DỮ LIỆU] Khối mã nguồn (```) chưa được đóng ở cuối tệp (dấu hiệu bị ngắt token giữa chừng)")
        score -= 40

    lines = [l.strip() for l in content.splitlines() if l.strip()]
    if lines:
        last_line = lines[-1]
        abrupt_endings = [",", "và", "hoặc", "nhưng", "tại", "là", "with", "and", "the", "in", "to", "for"]
        for ending in abrupt_endings:
            if last_line.lower().endswith(" " + ending) or last_line.lower() == ending:
                issues.append(f"[CỤT CÂU] Tệp kết thúc bất thường bằng từ nối: '{ending}'")
                score -= 20
                break

    if len(content.strip()) < 50:
        issues.append("[NỘI DUNG QUÁ NGẮN] Tài liệu markdown dưới 50 ký tự")
        score -= 30

    return (score >= 70, max(0, score), issues)


def verify_sql(content: str, file_path: Path) -> Tuple[bool, int, List[str]]:
    """Thẩm định an toàn của câu lệnh SQL."""
    issues = []
    score = 100

    dangerous_destructive = [
        (r"\bDELETE\s+FROM\s+\w+\s*(;|$)", "Phát hiện lệnh DELETE không có mệnh đề WHERE"),
        (r"\bUPDATE\s+\w+\s+SET\s+[^;]+(;|$)(?!.*\bWHERE\b)", "Phát hiện lệnh UPDATE không có mệnh đề WHERE"),
        (r"\bDROP\s+DATABASE\b", "Phát hiện lệnh hủy cơ sở dữ liệu DROP DATABASE"),
        (r"\bDROP\s+TABLE\b", "Phát hiện lệnh hủy bảng dữ liệu DROP TABLE")
    ]
    for pat, desc in dangerous_destructive:
        if re.search(pat, content, re.IGNORECASE):
            issues.append(f"[CẢNH BÁO SQL PHÁ HOẠI] {desc}")
            score -= 35

    if content.count("(") != content.count(")"):
        issues.append("[LỖI CÚ PHÁP SQL] Số lượng dấu ngoặc đơn '(' và ')' không khớp")
        score -= 30

    return (score >= 70, max(0, score), issues)


def verify_yaml(content: str, file_path: Path) -> Tuple[bool, int, List[str]]:
    """Thẩm định cấu trúc và cú pháp của tệp cấu hình YAML (Docker Compose, CI/CD, Airflow)."""
    issues = []
    score = 100

    # 1. Kiểm tra cấm dùng Tab (Quy chuẩn nghiêm ngặt của YAML)
    for idx, line in enumerate(content.splitlines(), 1):
        if "\t" in line:
            issues.append(f"[YAML LỖI CÚ PHÁP] Phát hiện ký tự Tab (\\t) tại dòng {idx}. YAML bắt buộc dùng dấu cách (Spaces)")
            score -= 25
            break

    # 2. Thử parse bằng thư viện yaml nếu có
    try:
        import yaml
        try:
            yaml.safe_load(content)
        except Exception as e:
            issues.append(f"[YAML PARSE ERROR] {e}")
            score -= 40
    except ImportError:
        # Kiểm tra ngoặc vuông, ngoặc nhọn cân bằng
        if content.count("{") != content.count("}"):
            issues.append("[YAML LỖI CÚ PHÁP] Dấu ngoặc nhọn '{' và '}' không cân bằng")
            score -= 20
        if content.count("[") != content.count("]"):
            issues.append("[YAML LỖI CÚ PHÁP] Dấu ngoặc vuông '[' và ']' không cân bằng")
            score -= 20

    if len(content.strip()) < 10:
        issues.append("[YAML RỖNG] Tệp cấu hình quá ngắn")
        score -= 50

    return (score >= 70, max(0, score), issues)


def verify_dockerfile(content: str, file_path: Path) -> Tuple[bool, int, List[str]]:
    """Thẩm định tính hợp lệ của tệp Dockerfile."""
    issues = []
    score = 100

    valid_instructions = {
        "FROM", "RUN", "CMD", "LABEL", "MAINTAINER", "EXPOSE", "ENV",
        "ADD", "COPY", "ENTRYPOINT", "VOLUME", "USER", "WORKDIR",
        "ARG", "ONBUILD", "STOPSIGNAL", "HEALTHCHECK", "SHELL"
    }

    first_instruction = None
    lines = content.splitlines()

    for idx, line in enumerate(lines, 1):
        line_clean = line.strip()
        if not line_clean or line_clean.startswith("#"):
            continue

        parts = line_clean.split(None, 1)
        inst = parts[0].upper()

        if first_instruction is None:
            first_instruction = inst
            if inst not in ("FROM", "ARG"):
                issues.append(f"[DOCKERFILE LỖI] Chỉ thị đầu tiên phải là FROM hoặc ARG (hiện tại: {inst} tại dòng {idx})")
                score -= 30

        if inst not in valid_instructions:
            # Kiểm tra xem có phải continuation line không
            prev_line = lines[idx - 2].strip() if idx > 1 else ""
            if not prev_line.endswith("\\"):
                issues.append(f"[DOCKERFILE LỖI CÚ PHÁP] Chỉ thị không hợp lệ '{inst}' tại dòng {idx}")
                score -= 20

    if first_instruction is None:
        issues.append("[DOCKERFILE RỖNG] Tệp không chứa bất kỳ chỉ thị Docker nào")
        score -= 60

    return (score >= 70, max(0, score), issues)


def verify_file(target_path: str) -> Dict:
    """Thẩm định tự động một tệp bất kỳ theo phần mở rộng."""
    f_path = Path(target_path).resolve()
    if not f_path.exists():
        return {
            "file": str(f_path),
            "status": "NOT_FOUND",
            "passed": False,
            "score": 0,
            "issues": [f"Tệp không tồn tại: {f_path}"]
        }

    try:
        with open(f_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
    except Exception as e:
        return {
            "file": str(f_path),
            "status": "READ_ERROR",
            "passed": False,
            "score": 0,
            "issues": [f"Không thể đọc tệp: {e}"]
        }

    ext = f_path.suffix.lower()
    fname = f_path.name.lower()

    if ext == ".py":
        passed, score, issues = verify_python(content, f_path)
    elif ext == ".json":
        passed, score, issues = verify_json(content, f_path)
    elif ext in [".yaml", ".yml"]:
        passed, score, issues = verify_yaml(content, f_path)
    elif "dockerfile" in fname:
        passed, score, issues = verify_dockerfile(content, f_path)
    elif ext in [".md", ".markdown", ".txt"]:
        passed, score, issues = verify_markdown(content, f_path)
    elif ext == ".sql":
        passed, score, issues = verify_sql(content, f_path)
    else:
        passed = len(content.strip()) > 0
        score = 100 if passed else 0
        issues = [] if passed else ["[RỖNG] Tệp không có nội dung"]

    status_tag = "PASS" if passed else "FAIL"
    return {
        "file": str(f_path),
        "extension": ext,
        "status": status_tag,
        "passed": passed,
        "score": score,
        "issues": issues
    }


def main():
    parser = argparse.ArgumentParser(description="Output Verifier & Quality Gatekeeper")
    parser.add_argument("file", help="Đường dẫn tệp cần thẩm định (.py, .json, .md, .sql)")
    parser.add_argument("--json", action="store_true", help="Xuất kết quả dưới dạng JSON cho Agent đọc")

    args = parser.parse_args()
    res = verify_file(args.file)

    if args.json:
        print(json.dumps(res, indent=2, ensure_ascii=False))
    else:
        print("=" * 65)
        print("🛡️ BÁO CÁO THẨM ĐỊNH CHẤT LƯỢNG OUTPUT (QUALITY GATE)")
        print("=" * 65)
        print(f"Tệp kiểm tra: {res['file']}")
        print(f"Điểm chất lượng: {res['score']}/100")
        print(f"Trạng thái: {'🟢 [VERIFIED: PASS]' if res['passed'] else '🔴 [VERIFIED: FAIL]'}")
        print("-" * 65)
        if res["issues"]:
            print("Các vấn đề ghi nhận:")
            for issue in res["issues"]:
                print(f"  ⚠️ {issue}")
        else:
            print("  ✅ Tệp hoàn toàn sạch sẽ, cú pháp chuẩn xác và đạt chuẩn an toàn!")
        print("=" * 65)

    sys.exit(0 if res["passed"] else 1)


if __name__ == "__main__":
    main()
