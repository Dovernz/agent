#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vietjet BRD Builder Engine
Automates the generation of official Vietjet Business Requirements Documents (BRD)
preserving 100% of the corporate layout, cover pages, sections A-F, tables, and styles.
Enforces the exact empirical font size matrix extracted from all official Vietjet BRDs:
  - Cover Title: 24.0 pt (Bold)
  - TOC Title: 16.0 pt (Bold)
  - Heading 1 (Section A-F, I, II, III): 13.0 pt (Bold, Vietjet Red #EE0000)
  - Heading 2 (Sub-sections 1.1, 2.1...): 13.0 pt (Bold, Black #000000)
  - Body Text & Lists: 12.0 pt (Regular)
  - Table Headers: 12.0 pt (Bold, Gray #D7D7D7)
  - Table Data Cells: 12.0 pt (Regular)
  - Running Header: 9.0 pt
"""

import os
import sys
import copy
import json
import argparse
from datetime import datetime
import docx
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, RGBColor

sys.stdout.reconfigure(encoding='utf-8')

# ==============================================================================
# VIETJET TYPOGRAPHY STANDARDS MATRIX (Trích xuất từ khảo sát 100% BRD Vietjet)
# ==============================================================================
FONT_FAMILY = "Times New Roman"

COVER_TITLE_SIZE = 24.0          # Tiêu đề trang bìa
TOC_TITLE_SIZE = 16.0            # Tiêu đề Mục lục
HEADING_1_SIZE = 13.0            # Tiêu đề mục lớn (Mục A-F, I, II, III) - Đỏ Vietjet #EE0000
HEADING_2_SIZE = 13.0            # Tiêu đề mục con (1.1, 1.2, 2.1, 2.3...) - Đen #000000
BODY_FONT_SIZE = 12.0            # Nội dung đoạn văn, gạch đầu dòng
TABLE_HEADER_SIZE = 12.0         # Tiêu đề cột các bảng (In đậm, nền xám)
TABLE_CELL_SIZE = 12.0           # Nội dung ô dữ liệu trong bảng (Thường)
HEADER_FONT_SIZE = 9.0           # Running header Section 1

# Color Palette
COLOR_VJ_RED = RGBColor(238, 0, 0)       # #EE0000 (Màu đỏ thương hiệu Vietjet)
COLOR_VJ_GREEN = RGBColor(0, 153, 0)     # #009900 (Màu xanh trang bìa BRD)
COLOR_BLACK = RGBColor(0, 0, 0)          # #000000
COLOR_MUTED = RGBColor(89, 89, 89)
HEX_HEADER_GRAY = "D7D7D7"


def apply_vietjet_font(run, font_name=FONT_FAMILY, size_pt=BODY_FONT_SIZE, bold=None, italic=None, color_rgb=None):
    """
    Applies font family and size both through python-docx API and directly into OpenXML (rFonts, sz, szCs)
    guaranteeing 100% cross-platform typography preservation.
    """
    if font_name:
        run.font.name = font_name
    if size_pt is not None:
        run.font.size = Pt(size_pt)
    if bold is not None:
        run.bold = bold
    if italic is not None:
        run.italic = italic
    if color_rgb is not None:
        run.font.color.rgb = color_rgb

    # Explicit OpenXML enforcement
    rPr = run._element.get_or_add_rPr()
    rFonts = rPr.xpath('w:rFonts')
    if not rFonts:
        rf = OxmlElement('w:rFonts')
        rPr.append(rf)
    else:
        rf = rFonts[0]
    rf.set(qn('w:ascii'), font_name)
    rf.set(qn('w:hAnsi'), font_name)
    rf.set(qn('w:cs'), font_name)
    rf.set(qn('w:eastAsia'), font_name)

    if size_pt is not None:
        half_pts = str(int(size_pt * 2))
        sz = rPr.xpath('w:sz')
        if sz:
            sz[0].set(qn('w:val'), half_pts)
        else:
            s_elem = OxmlElement('w:sz')
            s_elem.set(qn('w:val'), half_pts)
            rPr.append(s_elem)
            
        szCs = rPr.xpath('w:szCs')
        if not szCs:
            sc = OxmlElement('w:szCs')
            sc.set(qn('w:val'), half_pts)
            rPr.append(sc)
        else:
            szCs[0].set(qn('w:val'), half_pts)


def set_paragraph_text(p, text, font_name=FONT_FAMILY, size_pt=BODY_FONT_SIZE, bold=None, italic=None, color_rgb=None, space_after=2):
    for r in list(p.runs):
        p._element.remove(r._element)
        
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.15
    run = p.add_run(text if text is not None else "")
    apply_vietjet_font(run, font_name=font_name, size_pt=size_pt, bold=bold, italic=italic, color_rgb=color_rgb)
    return run


def set_cell_font(cell, text, font_name=FONT_FAMILY, size_pt=TABLE_CELL_SIZE, bold=False, color_rgb=None):
    p = cell.paragraphs[0]
    for r in list(p.runs):
        p._element.remove(r._element)
        
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.0
    run = p.add_run(str(text) if text is not None else "")
    apply_vietjet_font(run, font_name=font_name, size_pt=size_pt, bold=bold, color_rgb=color_rgb)


def set_cell_shading(cell, color_hex):
    tcPr = cell._element.get_or_add_tcPr()
    shd = tcPr.xpath('w:shd')
    if shd:
        shd[0].set(qn('w:val'), 'clear')
        shd[0].set(qn('w:color'), 'auto')
        shd[0].set(qn('w:fill'), color_hex)
    else:
        new_shd = OxmlElement('w:shd')
        new_shd.set(qn('w:val'), 'clear')
        new_shd.set(qn('w:color'), 'auto')
        new_shd.set(qn('w:fill'), color_hex)
        tcPr.append(new_shd)


def copy_cell_properties(src_cell, dst_cell):
    src_tcPr = src_cell._element.xpath('w:tcPr')
    if src_tcPr:
        dst_tcPr = dst_cell._element.get_or_add_tcPr()
        for child in src_tcPr[0]:
            tag = child.tag.split('}')[-1]
            if tag in ['tcW', 'tcBorders', 'tcMar', 'vAlign']:
                existing = dst_tcPr.xpath(f'w:{tag}')
                if existing:
                    dst_tcPr.remove(existing[0])
                dst_tcPr.append(copy.deepcopy(child))


def populate_table_data(table, data_rows, header_font_size=TABLE_HEADER_SIZE, cell_font_size=TABLE_CELL_SIZE):
    """
    Clears old data rows in a table and populates new rows matching header formatting.
    Header: Times New Roman, 12pt, Bold, Shading #D7D7D7.
    Data: Times New Roman, 12pt, Regular.
    """
    if len(table.rows) == 0:
        return
    
    # 1. Format header row: Times New Roman, 12pt, Bold
    header_row = table.rows[0]
    for cell in header_row.cells:
        txt = cell.text.strip()
        set_cell_font(cell, txt, font_name=FONT_FAMILY, size_pt=header_font_size, bold=True)
    
    # 2. Remove existing data rows
    while len(table.rows) > 1:
        tr = table.rows[-1]._element
        tr.getparent().remove(tr)
        
    # 3. Add new data rows: Times New Roman, 12pt, Regular
    for r_idx, row_values in enumerate(data_rows, start=1):
        new_row = table.add_row()
        trPr = new_row._element.get_or_add_trPr()
        cantSplit = OxmlElement('w:cantSplit')
        trPr.append(cantSplit)
        
        for c_idx, val in enumerate(row_values):
            if c_idx < len(new_row.cells):
                cell = new_row.cells[c_idx]
                copy_cell_properties(header_row.cells[c_idx], cell)
                set_cell_font(cell, val, font_name=FONT_FAMILY, size_pt=cell_font_size, bold=False)


def build_brd(config, template_path, output_path):
    """
    Loads master template docx, updates metadata, front pages, sections A-F,
    populates content with the exact specific font size for each part:
      - Cover Title: 24pt Bold
      - Heading 1: 13pt Bold (Red #EE0000)
      - Heading 2: 13pt Bold (Black #000000)
      - Body Text: 12pt Regular
      - Table Header: 12pt Bold
      - Table Data Cells: 12pt Regular
      - Running Header: 9pt
    """
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Template not found at: {template_path}")
        
    doc = docx.Document(template_path)
    
    # 1. METADATA EXTRACTION
    report_title = config.get("report_title", "BÁO CÁO QUẢN TRỊ THƯƠNG MẠI").strip()
    title_line1 = config.get("title_line1", report_title).strip()
    title_line2 = config.get("title_line2", "").strip()
    
    create_date_raw = config.get("create_date", datetime.today().strftime("%d-%m-%Y"))
    date_dash = create_date_raw.replace("/", "-")
    date_slash = create_date_raw.replace("-", "/")
    
    project_name = config.get("project_name", "Báo cáo quản trị thương mại")
    doc_id = config.get("doc_id", "")
    issued_by = config.get("issued_by", "Cao Tiến Thành")
    version = config.get("version", "1.0")
    effective_date = config.get("effective_date", "")
    
    # 2. UPDATE COVER PAGE PARAGRAPHS
    # P0 is Vietjet logo (PRESERVED)
    # P1: Title line 1 (Times New Roman, 24pt, Bold)
    set_paragraph_text(doc.paragraphs[1], title_line1, font_name=FONT_FAMILY, size_pt=COVER_TITLE_SIZE, bold=True)
    # P2: Title line 2 (Times New Roman, 24pt, Bold)
    if title_line2:
        set_paragraph_text(doc.paragraphs[2], title_line2, font_name=FONT_FAMILY, size_pt=COVER_TITLE_SIZE, bold=True)
    else:
        for r in list(doc.paragraphs[2].runs):
            doc.paragraphs[2]._element.remove(r._element)
        doc.paragraphs[2].text = ""
        
    # P4: Business Requirements Document (BRD) - Times New Roman, 12pt, Bold, Green
    set_paragraph_text(doc.paragraphs[4], "Business Requirements Document (BRD)", font_name=FONT_FAMILY, size_pt=BODY_FONT_SIZE, bold=True, color_rgb=COLOR_VJ_GREEN)
    # P5: Date - Times New Roman, 12pt, Regular, Green
    set_paragraph_text(doc.paragraphs[5], date_dash, font_name=FONT_FAMILY, size_pt=BODY_FONT_SIZE, bold=False, color_rgb=COLOR_VJ_GREEN)
    # P6: Version - Times New Roman, 12pt, Regular, Green
    set_paragraph_text(doc.paragraphs[6], f"Version {version}", font_name=FONT_FAMILY, size_pt=BODY_FONT_SIZE, bold=False, color_rgb=COLOR_VJ_GREEN)
    
    # 3. UPDATE TABLE 0 (Document Metadata - Times New Roman 12pt)
    t0 = doc.tables[0]
    set_cell_font(t0.rows[0].cells[1], project_name, font_name=FONT_FAMILY, size_pt=TABLE_CELL_SIZE)
    set_cell_font(t0.rows[1].cells[1], doc_id, font_name=FONT_FAMILY, size_pt=TABLE_CELL_SIZE)
    set_cell_font(t0.rows[2].cells[1], issued_by, font_name=FONT_FAMILY, size_pt=TABLE_CELL_SIZE)
    set_cell_font(t0.rows[3].cells[1], version, font_name=FONT_FAMILY, size_pt=TABLE_CELL_SIZE)
    set_cell_font(t0.rows[4].cells[1], effective_date, font_name=FONT_FAMILY, size_pt=TABLE_CELL_SIZE)
    
    # 4. UPDATE SECTION 1 HEADER TABLE (Running Header: 9pt)
    full_title = f"{title_line1} {title_line2}".strip()
    if len(doc.sections) > 1:
        sec1 = doc.sections[1]
        if sec1.header and sec1.header.tables:
            hdr_t = sec1.header.tables[0]
            for r_idx in range(len(hdr_t.rows)):
                set_cell_font(hdr_t.rows[r_idx].cells[1], full_title, font_name=FONT_FAMILY, size_pt=HEADER_FONT_SIZE, bold=True)
            if len(hdr_t.rows) > 1 and len(hdr_t.rows[1].cells) > 2:
                set_cell_font(hdr_t.rows[1].cells[2], date_slash, font_name=FONT_FAMILY, size_pt=HEADER_FONT_SIZE, bold=False)
            if len(hdr_t.rows) > 2 and len(hdr_t.rows[2].cells) > 2:
                set_cell_font(hdr_t.rows[2].cells[2], f"Version : {version}", font_name=FONT_FAMILY, size_pt=HEADER_FONT_SIZE, bold=False)

    # 5. SECTION I: MỤC TIÊU BÁO CÁO VÀ ĐỀ XUẤT
    objectives = config.get("objectives", [
        f"Cung cấp dữ liệu chi tiết và toàn diện cho báo cáo {full_title}.",
        "Hỗ trợ các khối nghiệp vụ và Ban Lãnh đạo giám sát hiệu quả khai thác, doanh thu và đưa ra quyết định kịp thời.",
        "Cho phép người dùng tra cứu, phân tích đa chiều theo thời gian bay, thị trường, đường bay, đại lý và phân khúc khách hàng."
    ])
    # Heading 1: 13.0 pt, Bold, Vietjet Red #EE0000
    set_paragraph_text(doc.paragraphs[42], "MỤC TIÊU BÁO CÁO VÀ ĐỀ XUẤT", font_name=FONT_FAMILY, size_pt=HEADING_1_SIZE, bold=True, color_rgb=COLOR_VJ_RED)
    # Heading 2: 13.0 pt, Bold, Black #000000
    set_paragraph_text(doc.paragraphs[43], "1.1. Mục tiêu báo cáo", font_name=FONT_FAMILY, size_pt=HEADING_2_SIZE, bold=True, color_rgb=COLOR_BLACK)
    # Body text: 12.0 pt, Regular
    set_paragraph_text(doc.paragraphs[44], "Báo cáo nhằm cung cấp dữ liệu chi tiết và chuyên sâu. Các mục chính của báo cáo bao gồm:", font_name=FONT_FAMILY, size_pt=BODY_FONT_SIZE)
    set_paragraph_text(doc.paragraphs[45], f"• {objectives[0]}", font_name=FONT_FAMILY, size_pt=BODY_FONT_SIZE)
    set_paragraph_text(doc.paragraphs[46], f"• {objectives[1] if len(objectives) > 1 else ''}", font_name=FONT_FAMILY, size_pt=BODY_FONT_SIZE)
    set_paragraph_text(doc.paragraphs[47], f"• {objectives[2] if len(objectives) > 2 else ''}", font_name=FONT_FAMILY, size_pt=BODY_FONT_SIZE)
    
    # Scope: Heading 2: 13.0 pt, Body: 12.0 pt
    scopes = config.get("scopes", [
        "Tất cả các đường bay (nội địa & quốc tế) hiện được khai thác bởi Vietjet (VJ) và Thái Vietjet (VZ).",
        "Toàn bộ các thị trường bay hiện tại (Việt Nam, Thái Lan, Trung Quốc, Hàn Quốc, Ấn Độ, Kazakhstan, Australia, ...).",
        "Dữ liệu được trích xuất đồng bộ từ hệ thống đặt chỗ Amelia / PSS và hệ thống Data Lakehouse Databricks trên tất cả các kênh bán (Website, Mobile App, OTA, GDS, Đại lý truyền thống)."
    ])
    set_paragraph_text(doc.paragraphs[48], "1.2. Phạm vi báo cáo", font_name=FONT_FAMILY, size_pt=HEADING_2_SIZE, bold=True, color_rgb=COLOR_BLACK)
    set_paragraph_text(doc.paragraphs[49], f"• {scopes[0]}", font_name=FONT_FAMILY, size_pt=BODY_FONT_SIZE)
    set_paragraph_text(doc.paragraphs[50], f"• {scopes[1] if len(scopes) > 1 else ''}", font_name=FONT_FAMILY, size_pt=BODY_FONT_SIZE)
    set_paragraph_text(doc.paragraphs[51], f"• {scopes[2] if len(scopes) > 2 else ''}", font_name=FONT_FAMILY, size_pt=BODY_FONT_SIZE)
    
    # Target Users: Heading 2: 13.0 pt, Table: Header 12pt Bold, Data 12pt Regular
    set_paragraph_text(doc.paragraphs[53], "1.3. Đối tượng sử dụng", font_name=FONT_FAMILY, size_pt=HEADING_2_SIZE, bold=True, color_rgb=COLOR_BLACK)
    user_departments = config.get("target_departments", [
        ["Thương Mại", "Tất cả các bộ phận trong khối thương mại: Charter, GDS, Sale nội địa, Sale quốc tế, Marketing, RM ..."],
        ["Ban Lãnh Đạo", "Ban Giám Đốc Khối, Ban Điều Hành theo dõi doanh thu và KPI."],
        ["Công Nghệ Thông Tin", "Data Team, IT Operations vận hành và bảo trì pipeline."]
    ])
    if len(doc.tables) > 8:
        populate_table_data(doc.tables[8], user_departments, header_font_size=TABLE_HEADER_SIZE, cell_font_size=TABLE_CELL_SIZE)
        
    # 6. SECTION II: CHI TIẾT BÁO CÁO
    # Heading 1: 13.0 pt, Bold, Vietjet Red #EE0000
    sec2_title = full_title.upper() if full_title.upper().startswith("BÁO CÁO") else f"BÁO CÁO {full_title.upper()}"
    set_paragraph_text(doc.paragraphs[56], sec2_title, font_name=FONT_FAMILY, size_pt=HEADING_1_SIZE, bold=True, color_rgb=COLOR_VJ_RED)
    
    # 2.1 Overview: Heading 2: 13.0 pt, Body: 12.0 pt
    set_paragraph_text(doc.paragraphs[57], "2.1. Tổng quan báo cáo", font_name=FONT_FAMILY, size_pt=HEADING_2_SIZE, bold=True, color_rgb=COLOR_BLACK)
    overview_text = config.get("overview_text", 
        f"Báo cáo cung cấp góc nhìn trực quan và số liệu chi tiết về {full_title}, "
        "giúp khối nghiệp vụ theo dõi biến động, đánh giá đóng góp doanh thu và tối ưu hóa chính sách bán."
    )
    set_paragraph_text(doc.paragraphs[58], overview_text, font_name=FONT_FAMILY, size_pt=BODY_FONT_SIZE)
    
    # 2.2 Definitions: Heading 2: 13.0 pt, Table: Header 12pt Bold, Data 12pt Regular
    set_paragraph_text(doc.paragraphs[60], "2.2. Định nghĩa", font_name=FONT_FAMILY, size_pt=HEADING_2_SIZE, bold=True, color_rgb=COLOR_BLACK)
    definitions = config.get("definitions", [
        ["1", "Thị trường", "Xác định theo điểm đi và điểm đến của chặng bay (Việt Nam, Trung Quốc, Thái Lan, Ấn Độ, ...)."],
        ["2", "Doanh thu", "Tổng doanh thu vé (Fare) và các khoản phụ thu (Ancillary) ghi nhận theo quy tắc kế toán."],
        ["3", "Tỷ lệ đóng góp (%)", "Tỷ trọng doanh thu hoặc số lượng của từng phân khúc trên tổng số chung của đường bay / chuyến bay."]
    ])
    if len(doc.tables) > 9:
        populate_table_data(doc.tables[9], definitions, header_font_size=TABLE_HEADER_SIZE, cell_font_size=TABLE_CELL_SIZE)
        
    # 2.3 Input Parameters: Heading 2: 13.0 pt, Table: Header 12pt Bold, Data 12pt Regular
    set_paragraph_text(doc.paragraphs[63], "2.3. Tham số đầu vào", font_name=FONT_FAMILY, size_pt=HEADING_2_SIZE, bold=True, color_rgb=COLOR_BLACK)
    input_parameters = config.get("input_parameters", [
        ["1", "Flight Date From", "Chọn ngày bay bắt đầu", "01/01/2026", "Bắt buộc"],
        ["2", "Flight Date To", "Chọn ngày bay kết thúc", "31/01/2026", "Bắt buộc"],
        ["3", "Market", "Chọn thị trường bay", "Vietnam", "Mặc định ALL"],
        ["4", "Airline Code", "Chọn mã hãng khai thác (VJ/VZ)", "VJ", "Mặc định ALL"],
        ["5", "Route", "Chọn đường bay", "SGN - HAN", "Mặc định ALL"],
        ["6", "Agency", "Chọn đại lý / kênh bán", "CTRIP", "Mặc định ALL"]
    ])
    if len(doc.tables) > 10:
        populate_table_data(doc.tables[10], input_parameters, header_font_size=TABLE_HEADER_SIZE, cell_font_size=TABLE_CELL_SIZE)
        
    # 2.4 Detailed Data Fields: Heading 2: 13.0 pt, Table: Header 12pt Bold, Data 12pt Regular
    set_paragraph_text(doc.paragraphs[67], "2.4. Bảng dữ liệu chi tiết", font_name=FONT_FAMILY, size_pt=HEADING_2_SIZE, bold=True, color_rgb=COLOR_BLACK)
    detailed_fields = config.get("detailed_fields", [
        ["1", "Flight_Date", "Ngày bay thực tế", "15/01/2026", ""],
        ["2", "Flight_Nmbr", "Số hiệu chuyến bay", "VJ123", ""],
        ["3", "Dep", "Sân bay khởi hành", "SGN", ""],
        ["4", "Arr", "Sân bay đến", "HAN", ""],
        ["5", "Market", "Thị trường chặng bay", "Vietnam", ""],
        ["6", "PNR", "Mã đặt chỗ hành khách", "K3T89X", ""],
        ["7", "Pax_Name", "Tên hành khách", "NGUYEN VAN A", ""],
        ["8", "Agent_Code", "Mã đại lý bán vé", "34001038", ""],
        ["9", "Agent_Name", "Tên đại lý bán vé", "CTRIP.COM", ""],
        ["10", "Revenue", "Doanh thu ghi nhận (VND)", "1,850,000", "Fare + Surcharges"]
    ])
    if len(doc.tables) > 11:
        populate_table_data(doc.tables[11], detailed_fields, header_font_size=TABLE_HEADER_SIZE, cell_font_size=TABLE_CELL_SIZE)
        
    # 7. SECTION III: DASHBOARD BÁO CÁO
    # Heading 1: 13.0 pt, Bold, Vietjet Red #EE0000
    set_paragraph_text(doc.paragraphs[73], "DASHBOARD BÁO CÁO", font_name=FONT_FAMILY, size_pt=HEADING_1_SIZE, bold=True, color_rgb=COLOR_VJ_RED)
    # Heading 2: 13.0 pt, Bold, Black #000000
    set_paragraph_text(doc.paragraphs[74], "3.1. Tổng quan", font_name=FONT_FAMILY, size_pt=HEADING_2_SIZE, bold=True, color_rgb=COLOR_BLACK)
    
    kpis = config.get("dashboard_kpis", [
        "Total Revenue: Tổng doanh thu ghi nhận trên các đường bay trong khoảng thời gian được chọn.",
        "Total Volume / Pax: Tổng sản lượng / số lượng hành khách trong kỳ.",
        "Top Category / Route: Hạng mục hoặc chặng bay đạt doanh thu cao nhất.",
        "Average Performance: Tỷ lệ hoặc giá trị bình quân trên mỗi chặng bay."
    ])
    set_paragraph_text(doc.paragraphs[78], f"• {kpis[0]}", font_name=FONT_FAMILY, size_pt=BODY_FONT_SIZE)
    set_paragraph_text(doc.paragraphs[79], f"• {kpis[1] if len(kpis) > 1 else ''}", font_name=FONT_FAMILY, size_pt=BODY_FONT_SIZE)
    set_paragraph_text(doc.paragraphs[80], f"• {kpis[2] if len(kpis) > 2 else ''}", font_name=FONT_FAMILY, size_pt=BODY_FONT_SIZE)
    set_paragraph_text(doc.paragraphs[81], f"• {kpis[3] if len(kpis) > 3 else ''}", font_name=FONT_FAMILY, size_pt=BODY_FONT_SIZE)
    
    # 3.2 Route level summary: Heading 2: 13.0 pt, Body: 12.0 pt
    route_heading = config.get("route_heading", "3.2. Báo cáo tổng hợp theo đường bay / đối tác")
    set_paragraph_text(doc.paragraphs[83], route_heading, font_name=FONT_FAMILY, size_pt=HEADING_2_SIZE, bold=True, color_rgb=COLOR_BLACK)
    
    route_text = config.get("route_summary_text", 
        f"Bảng tổng hợp cấp đường bay thể hiện tổng doanh thu và tỷ trọng cơ cấu của các đường bay được chọn."
    )
    set_paragraph_text(doc.paragraphs[84], route_text, font_name=FONT_FAMILY, size_pt=BODY_FONT_SIZE)
    
    # 3.3 Flight level summary: Heading 2: 13.0 pt, Body: 12.0 pt
    flight_heading = config.get("flight_heading", "3.3. Báo cáo chi tiết theo chuyến bay / giao dịch")
    set_paragraph_text(doc.paragraphs[90], flight_heading, font_name=FONT_FAMILY, size_pt=HEADING_2_SIZE, bold=True, color_rgb=COLOR_BLACK)
    
    flight_text = config.get("flight_summary_text",
        f"Bảng chi tiết cấp chuyến bay thể hiện chi tiết từng số hiệu chuyến bay theo từng ngày bay thực tế."
    )
    set_paragraph_text(doc.paragraphs[91], flight_text, font_name=FONT_FAMILY, size_pt=BODY_FONT_SIZE)

    # 8. SAVE OUTPUT
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    doc.save(output_path)
    print(f"[SUCCESS] BRD generated successfully at: {output_path}")
    return output_path


def main():
    parser = argparse.ArgumentParser(description="Vietjet BRD Document Builder")
    parser.add_argument("--config", help="Path to JSON configuration file")
    parser.add_argument("--output", help="Output .docx file path")
    parser.add_argument("--template", default=r"D:\Thành\Agent\projects\vietjet-brd\templates\template_vietjet_brd.docx", help="Template .docx path")
    args = parser.parse_args()
    
    if args.config:
        with open(args.config, "r", encoding="utf-8") as f:
            config = json.load(f)
    else:
        config = {
            "report_title": "BÁO CÁO CÁC DỊCH VỤ BÁN THÊM CỦA ĐỐI TÁC",
            "title_line1": "BÁO CÁO CÁC DỊCH VỤ BÁN THÊM CỦA ĐỐI TÁC",
            "title_line2": "THEO ĐƯỜNG BAY VÀ ĐẠI LÝ",
            "create_date": datetime.today().strftime("%d-%m-%Y"),
            "project_name": "Báo cáo quản trị thương mại",
            "issued_by": "Cao Tiến Thành",
            "version": "1.0",
            "overview_text": "Báo cáo theo dõi toàn diện doanh thu và sản lượng các dịch vụ phụ trợ (Ancillary / Add-on services: Suất ăn, Hành lý ký gửi, Chọn chỗ ngồi, Bảo hiểm, Priority check-in...) do các đối tác đại lý phát sinh trên từng đường bay.",
            "definitions": [
                ["1", "Dịch vụ bán thêm (Ancillary/Add-on)", "Bao gồm hành lý ký gửi quá cước, suất ăn nóng, chọn chỗ ngồi trước, phòng chờ, bảo hiểm du lịch và các gói tiện ích."],
                ["2", "Đại lý (Agency/Partner)", "Các đối tác bán vé bao gồm kênh OTA (Ctrip, Trip.com), đại lý chỉ định (PSA), GDS và đại lý truyền thống."],
                ["3", "Doanh thu Add-on", "Khoản tiền ròng thu được từ việc bán dịch vụ bổ sung, chưa bao gồm giá vé cơ bản (Fare)."]
            ],
            "input_parameters": [
                ["1", "Flight Date From", "Chọn ngày bay bắt đầu cần kiểm tra", "01/01/2026", "Bắt buộc"],
                ["2", "Flight Date To", "Chọn ngày bay kết thúc cần kiểm tra", "31/01/2026", "Bắt buộc"],
                ["3", "Market", "Chọn thị trường chặng bay", "Vietnam", "Mặc định ALL"],
                ["4", "Airline Code", "Chọn mã hãng hàng không (VJ / VZ)", "VJ", "Mặc định ALL"],
                ["5", "Route", "Chọn đường bay", "SGN - HAN", "Mặc định ALL"],
                ["6", "Agent Name", "Chọn tên đại lý đối tác", "CTRIP.COM", "Mặc định ALL"],
                ["7", "Addon Category", "Nhóm dịch vụ (Baggage, Meal, Seat, Priority)", "Baggage", "Mặc định ALL"]
            ],
            "detailed_fields": [
                ["1", "Flight_Date", "Ngày bay thực tế của chuyến bay", "15/01/2026", ""],
                ["2", "Flight_Nmbr", "Số hiệu chuyến bay", "VJ123", ""],
                ["3", "Dep", "Mã sân bay khởi hành", "SGN", ""],
                ["4", "Arr", "Mã sân bay đến", "HAN", ""],
                ["5", "Market", "Thị trường đường bay", "Vietnam", ""],
                ["6", "PNR", "Mã đặt chỗ của hành khách", "K3T89X", ""],
                ["7", "Pax_Name", "Họ tên hành khách", "NGUYEN VAN A", ""],
                ["8", "Agent_Code", "Mã định danh đại lý", "34001038", ""],
                ["9", "Agent_Name", "Tên đại lý đối tác", "CTRIP.COM (HONG KONG) LIMITED", ""],
                ["10", "Addon_Category", "Nhóm dịch vụ bổ sung", "Baggage", "Baggage/Meal/Seat"],
                ["11", "Addon_Code", "Mã gói dịch vụ bổ sung", "BAG20", ""],
                ["12", "Addon_Desc", "Mô tả chi tiết gói dịch vụ", "Hành lý ký gửi 20kg", ""],
                ["13", "Quantity", "Số lượng gói dịch vụ đặt mua", "1", ""],
                ["14", "Currency", "Loại đồng tiền giao dịch", "VND", ""],
                ["15", "Addon_Amount", "Tổng tiền dịch vụ bán thêm (VND)", "250,000", "Đơn giá x Số lượng"]
            ]
        }
        
    output_path = args.output or r"D:\Vietjet\2026\COM - Sale Reports\BRD\BRD_10 Addon_Services (draft v0.1).docx"
    build_brd(config, args.template, output_path)


if __name__ == "__main__":
    main()
