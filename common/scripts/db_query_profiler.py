#!/usr/bin/env python3
"""
db_query_profiler.py
Database Slow Query & N+1 Query Profiler for Antigravity Agent Hub.

Features:
- Analyzes SQL query logs, Django/FastAPI SQL logs, and slow query logs.
- Detects N+1 query patterns (repeated identical queries with parameterized IDs).
- Detects slow queries exceeding threshold (default: 100ms).
- Identifies missing index indicators (full table scans, Seq Scan, type: ALL).
- Suggests concrete optimizations (CREATE INDEX, Django select_related/prefetch_related).
- Zero-Fat M2M JSON output (--json) or human-readable console report.
"""

import os
import sys
import re
import json
import argparse
from collections import defaultdict
from pathlib import Path

# Ensure UTF-8 standard IO for Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Regex patterns for query log formats
# Format 1: Django/SQLAlchemy format: (0.125) SELECT "table"."id"... WHERE ...
DJANGO_LOG_PATTERN = re.compile(
    r'(?:\((\d+\.\d+)\)\s+)?(SELECT|INSERT|UPDATE|DELETE)\s+(.+?)(?:;\s*|--|\n|$)',
    re.IGNORECASE | re.DOTALL
)

# Format 2: PostgreSQL slow query log: duration: 125.432 ms  statement: SELECT ...
PG_SLOW_LOG_PATTERN = re.compile(
    r'duration:\s*(\d+(?:\.\d+)?)\s*ms\s+statement:\s*(SELECT|INSERT|UPDATE|DELETE)\s+(.+?)(?:;\s*|$)',
    re.IGNORECASE | re.DOTALL
)

# Format 3: MySQL slow query log: # Query_time: 0.125432 ... SELECT ...
MYSQL_SLOW_LOG_PATTERN = re.compile(
    r'#\s*Query_time:\s*(\d+(?:\.\d+)?).*?(SELECT|INSERT|UPDATE|DELETE)\s+(.+?)(?:;\s*|$)',
    re.IGNORECASE | re.DOTALL
)


def normalize_query(sql):
    """Replaces numeric IDs, string literals, and whitespace to find query templates."""
    sql = re.sub(r'--.*', '', sql)
    sql = re.sub(r'/\*.*?\*/', '', sql, flags=re.DOTALL)
    sql = re.sub(r"\'[^\']*\'", "'?'", sql)
    sql = re.sub(r'\b\d+\b', '?', sql)
    sql = re.sub(r'\s+', ' ', sql).strip()
    return sql


def extract_table_name(sql):
    """Attempts to extract primary table name from SQL query."""
    m = re.search(r'\bFROM\s+["`]?([a-zA-Z0-9_]+)["`]?', sql, re.IGNORECASE)
    if m:
        return m.group(1)
    m = re.search(r'\b(?:INTO|UPDATE)\s+["`]?([a-zA-Z0-9_]+)["`]?', sql, re.IGNORECASE)
    if m:
        return m.group(1)
    return "unknown_table"


def analyze_query_logs(raw_text, slow_threshold_ms=100.0, n_plus_one_threshold=3):
    """Parses raw SQL query logs and analyzes for performance bottlenecks."""
    queries = []
    
    # 1. Parse PG format
    for m in PG_SLOW_LOG_PATTERN.finditer(raw_text):
        duration_ms = float(m.group(1))
        verb = m.group(2).upper()
        stmt = m.group(2) + " " + m.group(3)
        queries.append({"duration_ms": duration_ms, "verb": verb, "raw_sql": stmt.strip()})

    # 2. Parse MySQL format if no PG logs matched
    if not queries:
        for m in MYSQL_SLOW_LOG_PATTERN.finditer(raw_text):
            duration_s = float(m.group(1))
            duration_ms = duration_s * 1000.0
            verb = m.group(2).upper()
            stmt = m.group(2) + " " + m.group(3)
            queries.append({"duration_ms": duration_ms, "verb": verb, "raw_sql": stmt.strip()})

    # 3. Parse Django / Generic format
    if not queries:
        for m in DJANGO_LOG_PATTERN.finditer(raw_text):
            dur_str = m.group(1)
            duration_ms = (float(dur_str) * 1000.0) if dur_str else 0.0
            verb = m.group(2).upper()
            stmt = m.group(2) + " " + m.group(3)
            queries.append({"duration_ms": duration_ms, "verb": verb, "raw_sql": stmt.strip()})

    # If still empty, split lines into individual queries
    if not queries:
        lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
        for line in lines:
            if re.match(r'^(SELECT|INSERT|UPDATE|DELETE)\b', line, re.IGNORECASE):
                queries.append({"duration_ms": 0.0, "verb": line.split()[0].upper(), "raw_sql": line})

    # Aggregations
    template_counts = defaultdict(lambda: {"count": 0, "total_ms": 0.0, "max_ms": 0.0, "examples": [], "table": ""})
    slow_queries = []
    missing_index_candidates = []

    for q in queries:
        raw_sql = q["raw_sql"]
        dur = q["duration_ms"]
        template = normalize_query(raw_sql)
        table = extract_table_name(raw_sql)

        entry = template_counts[template]
        entry["count"] += 1
        entry["total_ms"] += dur
        entry["max_ms"] = max(entry["max_ms"], dur)
        entry["table"] = table
        if len(entry["examples"]) < 2:
            entry["examples"].append(raw_sql[:160] + ("..." if len(raw_sql) > 160 else ""))

        if dur >= slow_threshold_ms:
            slow_queries.append({
                "table": table,
                "duration_ms": dur,
                "sql": raw_sql[:200]
            })

        # Missing index heuristic: WHERE with unindexed filter or Seq Scan
        if "seq scan" in raw_sql.lower() or "type: all" in raw_sql.lower():
            missing_index_candidates.append({
                "table": table,
                "evidence": "Seq Scan / type: ALL detected in query plan"
            })

    # Detect N+1 patterns
    n_plus_one_violations = []
    for template, stats in template_counts.items():
        if stats["count"] >= n_plus_one_threshold and template.startswith("SELECT"):
            # Check if query has WHERE ... id = ? or foreign key filter
            if "WHERE" in template and "?" in template:
                n_plus_one_violations.append({
                    "table": stats["table"],
                    "occurrences": stats["count"],
                    "template": template[:180] + ("..." if len(template) > 180 else ""),
                    "avg_ms": round(stats["total_ms"] / stats["count"], 2) if stats["count"] else 0.0,
                    "example": stats["examples"][0] if stats["examples"] else "",
                    "recommendation": f"Sử dụng `select_related()` hoặc `prefetch_related()` (ORM) để batch fetch bảng '{stats['table']}'"
                })

    status = "WARN" if (n_plus_one_violations or slow_queries) else "PASS"

    return {
        "status": status,
        "total_queries_analyzed": len(queries),
        "unique_query_templates": len(template_counts),
        "slow_queries_count": len(slow_queries),
        "n_plus_one_count": len(n_plus_one_violations),
        "slow_queries": slow_queries[:10],
        "n_plus_one_violations": n_plus_one_violations,
        "missing_index_candidates": missing_index_candidates
    }


def main():
    parser = argparse.ArgumentParser(description="Database Slow Query & N+1 Query Profiler for Antigravity Agent Hub")
    parser.add_argument("file", nargs="?", help="Đường dẫn file log truy vấn SQL hoặc slow query log")
    parser.add_argument("--query", "-q", help="Chuỗi câu lệnh SQL cần phân tích trực tiếp")
    parser.add_argument("--threshold-ms", type=float, default=100.0, help="Ngưỡng cảnh báo truy vấn chậm (ms, mặc định: 100)")
    parser.add_argument("--n1-threshold", type=int, default=3, help="Ngưỡng phát hiện lặp câu truy vấn N+1 (mặc định: 3 lần)")
    parser.add_argument("--json", action="store_true", help="Xuất kết quả định dạng JSON M2M")
    args = parser.parse_args()

    raw_text = ""
    source_name = ""

    if args.query:
        raw_text = args.query
        source_name = "Inline Query Input"
    elif args.file and os.path.exists(args.file):
        source_name = args.file
        try:
            with open(args.file, "r", encoding="utf-8", errors="ignore") as f:
                raw_text = f.read()
        except Exception as e:
            print(f"[!] Lỗi đọc tệp log: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        # Check standard default log candidate paths
        for cand in ["logs/db_query.log", "logs/slow_query.log", "query.log"]:
            if os.path.exists(cand):
                source_name = cand
                with open(cand, "r", encoding="utf-8", errors="ignore") as f:
                    raw_text = f.read()
                break

    if not raw_text:
        print("[!] Không tìm thấy dữ liệu truy vấn SQL. Hãy truyền đường dẫn file log hoặc dùng cờ -q / --query.", file=sys.stderr)
        sys.exit(1)

    result = analyze_query_logs(raw_text, slow_threshold_ms=args.threshold_ms, n_plus_one_threshold=args.n1_threshold)

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
        sys.exit(0 if result["status"] == "PASS" else 1)

    print("\n" + "=" * 65)
    print("📊 ANTIGRAVITY DATABASE SLOW QUERY & N+1 PROFILER")
    print(f"📍 Nguồn dữ liệu: {source_name}")
    print(f"🔍 Tổng số truy vấn: {result['total_queries_analyzed']} | Dạng mẫu (Templates): {result['unique_query_templates']}")
    print("=" * 65)

    if result["status"] == "PASS":
        print("\n✅ [STATUS: PASS] KHÔNG PHÁT HIỆN LỖI HIỆU NĂNG TRUY VẤN!")
        print(f"   - Không có truy vấn nào vượt ngưỡng chậm ({args.threshold_ms}ms)")
        print(f"   - Không phát hiện hành vi truy vấn lặp N+1 (ngưỡng >= {args.n1_threshold} lần)")
        print("\n" + "=" * 65 + "\n")
        sys.exit(0)
    else:
        print(f"\n⚠️  [STATUS: WARN] PHÁT HIỆN CÁC ĐIỂM NÓNG CẦN TỐI ƯU HÓA:")

        if result["n_plus_one_violations"]:
            print(f"\n🔥 1. Phát hiện {len(result['n_plus_one_violations'])} mẫu truy vấn N+1 lặp lại:")
            for idx, item in enumerate(result["n_plus_one_violations"], 1):
                print(f"  [{idx}] Bảng `{item['table']}` bị gọi lặp {item['occurrences']} lần:")
                print(f"      Mẫu: {item['template']}")
                print(f"      💡 Đề xuất: {item['recommendation']}")

        if result["slow_queries"]:
            print(f"\n⏱️  2. Phát hiện {len(result['slow_queries'])} truy vấn chậm (>= {args.threshold_ms}ms):")
            for idx, item in enumerate(result["slow_queries"], 1):
                print(f"  [{idx}] Bảng `{item['table']}` | Thời gian: {item['duration_ms']}ms")
                print(f"      SQL: {item['sql']}")
                print(f"      💡 Đề xuất: Tạo INDEX trên các trường trong mệnh đề WHERE/JOIN")

        print("\n" + "=" * 65 + "\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
