import csv
import json

path = r'D:\Vietjet\Gitlab\test\files\Maureva\20261026\VJ_SPEC_SALESSTATS_COUPON_ISSUE_DATE_On 20261026\VJ_SPEC_SALESSTATS_COUPON_ISSUE_DATE_On 20261026.csv'

with open(path, 'r', encoding='utf-8', errors='ignore') as f:
    line1 = f.readline()
    header_line = f.readline().strip()
    headers = [h.strip() for h in header_line.split(';')]
    print(f"Total headers: {len(headers)}")
    
    reader = csv.reader(f, delimiter=';')
    rows = []
    for i, row in enumerate(reader):
        if i < 2000:
            rows.append(row)
        else:
            break

target_cols = [
    'MNTH', 'PERI', 'NJOB', 'SMOD', 'ZONE', 'TYPDOC', 'FARE_TYPE', 'RBKD', 'ETCA', 'BASE',
    'TMFA', 'TMFF', 'YQ', 'CUTP_TO_EUR', 'REDU', 'NPAX', 'TOUR', 'SSPA', 'ETKT', 'BASE_REDU',
    'OCCA', 'OCFT', 'CABC', 'EFCM', 'FBTD_ALT', 'FBTD', 'FFRF', 'TPAX', 'CJCP', 'TDPT',
    'FRCA', 'ENRS', 'FBAL', 'NBDA', 'NADA', 'BOON', 'FCMI', 'SQNU_EMIS', 'TTEM', 'TTEF',
    'DOM_INT', 'RPSI', 'FPI2', 'FPI1', 'RVNR_FARE', 'CPCF_CORR', 'CPVF_CORR', 'TMFF_CORR',
    'CPVF_NO_VAT', 'YQ_USD', 'YR_USD', 'AGENCYTYPE', 'MNTH_SALES_KEY', 'CSHR_BLNG'
]

col_indices = {}
for i, h in enumerate(headers):
    if h in target_cols:
        if h not in col_indices:
            col_indices[h] = []
        col_indices[h].append(i)

results = {}
for col in target_cols:
    idxs = col_indices.get(col, [])
    sample_vals = set()
    non_empty = 0
    total = 0
    for r in rows:
        for idx in idxs:
            if idx < len(r):
                val = r[idx].strip()
                total += 1
                if val:
                    non_empty += 1
                    if len(sample_vals) < 15:
                        sample_vals.add(val)
    results[col] = {
        'indices': idxs,
        'non_empty_count': non_empty,
        'samples': list(sample_vals)
    }

for col, data in results.items():
    print(f"[{col}] (indices: {data['indices']}) non_empty: {data['non_empty_count']}")
    print(f"   samples: {data['samples'][:8]}")
