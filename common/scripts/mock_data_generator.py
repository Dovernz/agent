#!/usr/bin/env python3
"""
mock_data_generator.py
Intelligent Domain Mock Data & DB Seeding Engine for Antigravity Agent Hub
Generates realistic Vietnamese domain records for Dental, Airflow, and E-commerce,
outputting JSON, SQL Inserts, or Django Fixtures ready for Docker DB seeding.
"""

import os
import sys
import json
import random
import argparse
from datetime import datetime, timedelta

# Ensure UTF-8 standard IO for Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

VIETNAMESE_LAST_NAMES = ["Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Huỳnh", "Phan", "Vũ", "Võ", "Đặng", "Bùi", "Đỗ", "Hồ", "Ngô", "Dương"]
VIETNAMESE_MIDDLE_NAMES = ["Văn", "Thị", "Hữu", "Đức", "Thành", "Minh", "Thu", "Ngọc", "Phương", "Hoàng", "Xuân", "Thanh", "Quang"]
VIETNAMESE_FIRST_NAMES = ["An", "Bình", "Cường", "Dũng", "Em", "Giang", "Hải", "Hương", "Huy", "Khoa", "Linh", "Long", "Nam", "Nga", "Phúc", "Quân", "Sơn", "Thảo", "Tùng", "Vy", "Yến"]

DENTAL_SERVICES = [
    ("Khám & Tư vấn răng tổng quát", 100000),
    ("Cạo vôi răng & Đánh bóng siêu âm", 250000),
    ("Trám răng thẩm mỹ Laser Composite", 350000),
    ("Tẩy trắng răng công nghệ Laser Whitening", 1800000),
    ("Nhổ răng khôn không đau Piezotome", 1200000),
    ("Bọc răng sứ Zirconia chính hãng", 3500000),
    ("Chỉnh nha Niềng răng mắc cài thông minh", 28000000),
    ("Cấy ghép Implant Straumann chuẩn Thụy Sĩ", 18500000)
]

def generate_vietnamese_name():
    return f"{random.choice(VIETNAMESE_LAST_NAMES)} {random.choice(VIETNAMESE_MIDDLE_NAMES)} {random.choice(VIETNAMESE_FIRST_NAMES)}"

def generate_vietnamese_phone():
    prefixes = ["090", "091", "098", "097", "086", "088", "038", "077"]
    return f"{random.choice(prefixes)}{random.randint(1000000, 9999999)}"

def generate_dental_records(count):
    records = []
    base_date = datetime.now()
    for i in range(1, count + 1):
        name = generate_vietnamese_name()
        phone = generate_vietnamese_phone()
        service, price = random.choice(DENTAL_SERVICES)
        book_dt = base_date + timedelta(days=random.randint(1, 14), hours=random.randint(8, 17))
        teeth = random.sample([11, 12, 13, 21, 22, 23, 31, 32, 36, 46, 48], k=random.randint(1, 3))
        
        records.append({
            "id": i,
            "patient_name": name,
            "phone": phone,
            "gender": random.choice(["Nam", "Nữ"]),
            "birth_year": random.randint(1975, 2005),
            "service_name": service,
            "estimated_price": price,
            "teeth_numbers": teeth,
            "appointment_time": book_dt.strftime("%Y-%m-%d %H:%M"),
            "status": random.choice(["PENDING", "CONFIRMED", "COMPLETED"]),
            "notes": f"Bệnh nhân yêu cầu bác sĩ chuyên khoa răng hàm mặt khám răng {teeth}."
        })
    return records

def generate_airflow_records(count):
    records = []
    dag_names = ["vj_ancillary_daily_sync", "vj_booking_etl_pipeline", "vj_pss_gl_charges_loader", "vj_passenger_databricks_sync"]
    base_time = datetime.now() - timedelta(days=2)
    for i in range(1, count + 1):
        dag = random.choice(dag_names)
        start = base_time + timedelta(hours=i * 2)
        duration = random.randint(45, 900)
        end = start + timedelta(seconds=duration)
        state = random.choices(["success", "failed", "running"], weights=[80, 10, 10])[0]
        records.append({
            "dag_id": dag,
            "run_id": f"manual__{start.strftime('%Y-%m-%dT%H_%M_%S')}",
            "execution_date": start.strftime("%Y-%m-%d %H:%M:%S"),
            "start_date": start.strftime("%Y-%m-%d %H:%M:%S"),
            "end_date": end.strftime("%Y-%m-%d %H:%M:%S") if state != "running" else None,
            "duration_seconds": duration if state != "running" else None,
            "state": state,
            "operator": "TaskFlowPythonOperator"
        })
    return records

def generate_ecommerce_records(count):
    records = []
    products = [
        ("Bàn chải điện Sonic Wave X3", 650000),
        ("Máy tăm nước gia đình ProClean", 1250000),
        ("Bộ kem đánh răng thảo dược thiên nhiên", 145000),
        ("Nước súc miệng diệt khuẩn bạc hà 500ml", 85000),
        ("Chỉ nha khoa tiệt trùng sợi mảnh", 45000)
    ]
    for i in range(1, count + 1):
        prod, price = random.choice(products)
        qty = random.randint(1, 3)
        records.append({
            "order_id": f"ORD-2026-{1000 + i}",
            "customer_name": generate_vietnamese_name(),
            "phone": generate_vietnamese_phone(),
            "shipping_address": f"{random.randint(1, 250)} Đường Nguyễn Thị Minh Khai, Quận 1, TP. Hồ Chí Minh",
            "item_name": prod,
            "unit_price": price,
            "quantity": qty,
            "total_amount": price * qty,
            "order_status": random.choice(["SHIPPED", "DELIVERED", "PROCESSING"]),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    return records

def format_sql_inserts(table_name, records):
    if not records:
        return ""
    lines = []
    cols = list(records[0].keys())
    col_str = ", ".join([f"`{c}`" for c in cols])
    
    for r in records:
        val_list = []
        for c in cols:
            val = r[c]
            if val is None:
                val_list.append("NULL")
            elif isinstance(val, (int, float)):
                val_list.append(str(val))
            elif isinstance(val, list):
                val_list.append(f"'{json.dumps(val)}'")
            else:
                escaped = str(val).replace("'", "''")
                val_list.append(f"'{escaped}'")
        val_str = ", ".join(val_list)
        lines.append(f"INSERT INTO `{table_name}` ({col_str}) VALUES ({val_str});")
    return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser(description="Intelligent Mock Data & DB Seeder Engine")
    parser.add_argument("--domain", "-d", choices=["dental", "airflow", "ecommerce"], default="dental", help="Nghiệp vụ cần sinh dữ liệu")
    parser.add_argument("--count", "-c", type=int, default=10, help="Số lượng bản ghi cần sinh (mặc định 10)")
    parser.add_argument("--format", "-f", choices=["json", "sql"], default="json", help="Định dạng kết xuất (json hoặc sql)")
    parser.add_argument("--output", "-o", help="Đường dẫn file lưu dữ liệu mồi")
    parser.add_argument("--table", "-t", default="mock_table", help="Tên bảng dữ liệu nếu xuất định dạng SQL")
    
    args = parser.parse_args()
    
    if args.domain == "dental":
        records = generate_dental_records(args.count)
        table_name = args.table if args.table != "mock_table" else "dental_patient_appointments"
    elif args.domain == "airflow":
        records = generate_airflow_records(args.count)
        table_name = args.table if args.table != "mock_table" else "airflow_dag_runs"
    elif args.domain == "ecommerce":
        records = generate_ecommerce_records(args.count)
        table_name = args.table if args.table != "mock_table" else "ecommerce_orders"
        
    if args.format == "sql":
        output_data = format_sql_inserts(table_name, records)
    else:
        output_data = json.dumps(records, indent=2, ensure_ascii=False)
        
    if args.output:
        out_dir = os.path.dirname(os.path.abspath(args.output))
        os.makedirs(out_dir, exist_ok=True)
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output_data)
        print(f"[✓] Đã sinh thành công {len(records)} bản ghi mồi ({args.domain.upper()}) lưu tại: {args.output}")
    else:
        print(output_data)

if __name__ == "__main__":
    main()
