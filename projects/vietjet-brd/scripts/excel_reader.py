#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vietjet Excel Requirement Extractor
Parses requirement sheets (like 20260108_REPORT REQUEST TO IT.xlsx)
and extracts structured BRD configuration.
"""

import sys
import openpyxl
import json
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

def parse_report_from_excel(excel_path, sheet_name="set up report", report_num="10"):
    wb = openpyxl.load_workbook(excel_path, data_only=True)
    sheet = wb[sheet_name]
    
    extracted = {
        "report_id": report_num,
        "title": "",
        "purpose": "",
        "filters": [],
        "columns_summary": [],
        "columns_detail": [],
        "examples_summary": [],
        "examples_detail": []
    }
    
    # We want to find the detail block which starts around row 20 or later
    # E.g. "10.Báo cáo" or "10. Báo cáo"
    found_row = None
    for r in range(20, sheet.max_row + 1):
        v = sheet.cell(r, 1).value
        if v and str(v).strip().startswith(f"{report_num}."):
            found_row = r
            extracted["title"] = str(v).strip()
            break
            
    if not found_row:
        # Fallback to searching anywhere after row 15
        for r in range(16, sheet.max_row + 1):
            for c in range(1, 4):
                v = sheet.cell(r, c).value
                if v and f"{report_num}." in str(v):
                    found_row = r
                    extracted["title"] = str(v).strip()
                    break
            if found_row:
                break
                
    if not found_row:
        return None
        
    # Read contiguous block of rows
    for r in range(found_row, min(found_row + 20, sheet.max_row + 1)):
        # Stop if we hit the next numbered section
        if r > found_row:
            c1 = sheet.cell(r, 1).value
            if c1 and any(str(c1).strip().startswith(f"{n}.") for n in range(1, 20) if str(n) != str(report_num)):
                break
                
        # Column 1 to 9 is usually Summary / Pivot table request
        # Column 10 to 25 is usually Detailed data fields (Cột của các báo cáo cần làm)
        summary_vals = [sheet.cell(r, c).value for c in range(1, 10)]
        detail_vals = [sheet.cell(r, c).value for c in range(10, sheet.max_column + 1)]
        
        # Purpose
        for v in summary_vals:
            if v and "mục đích" in str(v).lower():
                extracted["purpose"] = str(v).replace("Mục đích:", "").replace("Mục Đích:", "").strip()
                
        # Filters (Lọc)
        if any("lọc" in str(v).lower() for v in summary_vals if v):
            filters = [str(v).strip() for v in summary_vals if v is not None and "lọc" not in str(v).lower()]
            if filters:
                extracted["filters"].extend(filters)
                
        # Summary columns (Mục)
        if any(str(v).strip().lower() == "mục" for v in summary_vals if v):
            cols = [str(v).strip() for v in summary_vals if v is not None and str(v).strip().lower() != "mục"]
            if cols and not extracted["columns_summary"]:
                extracted["columns_summary"] = cols
                
        # Summary examples (VD)
        if any(str(v).strip().lower() == "vd" for v in summary_vals if v):
            ex = [str(v).strip() for v in summary_vals if v is not None and str(v).strip().lower() != "vd"]
            if ex:
                extracted["examples_summary"].append(ex)
                
        # Detail columns (Cột chi tiết)
        if any(str(v).strip().lower() == "mục" for v in detail_vals if v):
            cols = [str(v).strip() for v in detail_vals if v is not None and str(v).strip().lower() != "mục"]
            if cols and not extracted["columns_detail"]:
                extracted["columns_detail"] = cols
                
        # Detail examples (VD chi tiết)
        if any(str(v).strip().lower() == "vd" for v in detail_vals if v):
            ex = [str(v).strip() for v in detail_vals if v is not None and str(v).strip().lower() != "vd"]
            if ex:
                extracted["examples_detail"].append(ex)
                
    return extracted

if __name__ == "__main__":
    path = r"D:\Vietjet\2026\COM - Sale Reports\20260108_REPORT REQUEST TO IT.xlsx"
    for num in ["8", "9", "10", "11"]:
        res = parse_report_from_excel(path, report_num=num)
        print(f"=== REPORT {num} ===")
        print(json.dumps(res, ensure_ascii=False, indent=2))
        print()
