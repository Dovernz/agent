#!/usr/bin/env python3
"""
Universal Data Peeker (Cross-Project Shared Utility)
Provides instant, token-saving inspection of CSV, TSV, Excel, JSON, and text files.
Dumps only file dimension, sheet names, headers, and first N sample rows.
"""

import os
import sys
import json
import csv

# Ensure UTF-8 standard IO for Windows
if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def peek_csv(file_path, sample_rows=3, delimiter=None):
    if not delimiter:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            first_line = f.readline()
            if ';' in first_line and first_line.count(';') > first_line.count(','):
                delimiter = ';'
            elif '\t' in first_line:
                delimiter = '\t'
            else:
                delimiter = ','
                
    rows = []
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        reader = csv.reader(f, delimiter=delimiter)
        for i, row in enumerate(reader):
            if i <= sample_rows:
                rows.append(row)
            else:
                break
                
    headers = rows[0] if rows else []
    samples = rows[1:] if len(rows) > 1 else []
    return {
        "file_type": "CSV/TSV",
        "delimiter": delimiter,
        "total_columns": len(headers),
        "headers": headers,
        "sample_rows": samples
    }

def peek_excel(file_path, sample_rows=3):
    try:
        import openpyxl
        wb = openpyxl.load_workbook(file_path, read_only=True, data_only=True)
        sheet_info = {}
        for sname in wb.sheetnames[:5]:
            ws = wb[sname]
            rows = []
            for i, r in enumerate(ws.iter_rows(values_only=True)):
                if i <= sample_rows:
                    rows.append([str(c) if c is not None else "" for c in r])
                else:
                    break
            sheet_info[sname] = {
                "headers": rows[0] if rows else [],
                "sample_rows": rows[1:] if len(rows) > 1 else []
            }
        wb.close()
        return {
            "file_type": "Excel (.xlsx)",
            "sheets": wb.sheetnames,
            "inspected_sheets": sheet_info
        }
    except Exception as e:
        return {"file_type": "Excel", "error": str(e)}

def peek_json(file_path, sample_rows=3):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        try:
            data = json.load(f)
            if isinstance(data, list):
                return {
                    "file_type": "JSON List",
                    "total_items": len(data),
                    "sample_items": data[:sample_rows]
                }
            elif isinstance(data, dict):
                return {
                    "file_type": "JSON Object",
                    "top_keys": list(data.keys())[:20],
                    "sample_data": {k: data[k] for k in list(data.keys())[:sample_rows]}
                }
        except Exception as e:
            return {"file_type": "JSON", "error": str(e)}

def main():
    if len(sys.argv) < 2:
        print("Usage: python peek_data.py <path_to_file> [--rows N]")
        sys.exit(1)
        
    fpath = sys.argv[1]
    rows = 3
    if "--rows" in sys.argv:
        idx = sys.argv.index("--rows")
        if idx + 1 < len(sys.argv):
            rows = int(sys.argv[idx + 1])
            
    if not os.path.exists(fpath):
        print(json.dumps({"error": f"File not found: {fpath}"}, ensure_ascii=False))
        sys.exit(1)
        
    ext = os.path.splitext(fpath)[1].lower()
    res = {}
    if ext in [".csv", ".txt", ".tsv"]:
        res = peek_csv(fpath, sample_rows=rows)
    elif ext in [".xlsx", ".xlsm"]:
        res = peek_excel(fpath, sample_rows=rows)
    elif ext in [".json"]:
        res = peek_json(fpath, sample_rows=rows)
    else:
        # Generic text peek
        with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = [f.readline().strip() for _ in range(rows + 1)]
        res = {"file_type": "Text", "headers": lines[0] if lines else "", "sample_lines": lines[1:]}
        
    res["file_path"] = fpath
    res["file_size_bytes"] = os.path.getsize(fpath)
    print(json.dumps(res, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
