#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Universal Task Fan-Out & Sub-Agent Sizing Planner (task_fanout_planner.py)
==============================================================================
TÍNH NĂNG:
1. Đánh giá độ phức tạp của Yêu cầu/Feature (Scope & Complexity Assessment).
2. Tự động tính toán số lượng Sub-agent Worker tối ưu dưới quyền Lead (N in [1, 5]).
3. Phân chia rõ ràng vai trò từng Worker và tầng Model API tương ứng (bulk, standard, deep).
4. Xuất kế hoạch điều phối dạng JSON chuẩn M2M Protocol và hiển thị bảng Markdown trực quan.
==============================================================================
"""

import sys
import os
import json
import argparse
from typing import Dict, List, Any

# Đảm bảo mã hóa UTF-8 cho Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


ROLE_TEMPLATES = {
    "backend": [
        {"suffix": "models-migrations", "role": "Data Model & Schema Architect", "tier": "standard", "task": "Xây dựng Models ORM, quan hệ Foreign Key và chạy DB Migration trong Docker."},
        {"suffix": "serializers-views", "role": "API Views & Endpoints Builder", "tier": "standard", "task": "Xây dựng Serializers, ViewSets/Controllers, phân trang và định tuyến API."},
        {"suffix": "seeder-mockdata", "role": "DB Seeder & Fixture Specialist", "tier": "bulk", "task": "Viết script seeding dữ liệu mẫu giả lập thực tế cho DB."},
        {"suffix": "query-optimizer", "role": "DB Query & Index Specialist", "tier": "deep", "task": "Profile truy vấn, thêm select_related/prefetch_related và đánh index tối ưu."},
        {"suffix": "security-cors", "role": "Auth & Middleware Hardener", "tier": "standard", "task": "Cấu hình JWT/Session auth, CORS, Rate Limiting và RBAC permissions."}
    ],
    "frontend": [
        {"suffix": "routing-layout", "role": "Page Layout & Router Specialist", "tier": "bulk", "task": "Xây dựng layout, điều hướng route, sidebar và mobile navigation responsive."},
        {"suffix": "api-client", "role": "API Client & State Manager", "tier": "standard", "task": "Tạo API fetch hooks/React Query từ OpenAPI spec và thiết lập Zustand/SWR state."},
        {"suffix": "ui-components", "role": "Component & Form Designer", "tier": "standard", "task": "Xây dựng components tái sử dụng, form validation và modal popups."},
        {"suffix": "mock-tester", "role": "Frontend Mock & E2E Tester", "tier": "bulk", "task": "Kết nối Mock Server và kiểm thử tương tác người dùng trên giao diện."},
        {"suffix": "style-theming", "role": "Tailwind & Theme Specialist", "tier": "bulk", "task": "Đồng bộ hóa typography, bảng màu nhận diện và dark/light mode."}
    ],
    "qa": [
        {"suffix": "unit-tests", "role": "Unit Test Specialist", "tier": "standard", "task": "Viết bộ kiểm thử đơn vị (Unit tests) bao phủ 100% các hàm nghiệp vụ trọng yếu."},
        {"suffix": "integration-tests", "role": "API Integration Tester", "tier": "standard", "task": "Viết kiểm thử tích hợp API endpoints, kiểm tra status codes và response payload."},
        {"suffix": "security-scanner", "role": "Security & Lint Inspector", "tier": "bulk", "task": "Chạy linter guard, quét secret leaks và rà soát lỗ hổng OWASP."},
        {"suffix": "e2e-playwright", "role": "End-to-End User Flow Tester", "tier": "standard", "task": "Viết kịch bản tự động hóa browser Playwright kiểm thử luồng người dùng."}
    ],
    "ba": [
        {"suffix": "user-stories", "role": "User Story & AC Refiner", "tier": "deep", "task": "Bóc tách yêu cầu thành các User Stories và Acceptance Criteria chuẩn Gherkin."},
        {"suffix": "schema-contract", "role": "Data Schema Specifier", "tier": "standard", "task": "Định rõ schema trường dữ liệu, validation rules và edge cases."},
        {"suffix": "doc-sync", "role": "Living Documentation Specialist", "tier": "bulk", "task": "Đồng bộ tech-stack.md và rules sau khi hoàn thành tính năng."}
    ],
    "architect": [
        {"suffix": "openapi-designer", "role": "OpenAPI Spec Architect", "tier": "deep", "task": "Thiết kế file đặc tả OpenAPI/Swagger 3.0 với đầy đủ schemas và mock examples."},
        {"suffix": "db-schema", "role": "Database Normalization Specialist", "tier": "deep", "task": "Thiết kế thực thể quan hệ ERD, khóa chính, khóa ngoại và chỉ mục index."},
        {"suffix": "mock-launcher", "role": "Instant Mock Service Operator", "tier": "bulk", "task": "Khởi tạo và cấu hình mock server tức thì cho Frontend phát triển song song."}
    ],
    "cyber": [
        {"suffix": "sast-scanner", "role": "Static Code & Secret Auditor", "tier": "bulk", "task": "Rà soát toàn bộ source code tìm hardcoded keys, passwords và lỗ hổng OWASP."},
        {"suffix": "rbac-auditor", "role": "Access Control & Auth Verifier", "tier": "deep", "task": "Kiểm tra ma trận phân quyền, JWT token expiration và CSRF protection."},
        {"suffix": "dependency-patcher", "role": "Dependency CVE Specialist", "tier": "bulk", "task": "Quét CVE phụ thuộc và sinh bản vá tự động nâng cấp package an toàn."}
    ]
}


def calculate_fanout(role: str, scope: str, files_count: int, complexity: str) -> Dict[str, Any]:
    role_key = role.lower()
    if role_key not in ROLE_TEMPLATES:
        role_key = "backend"

    templates = ROLE_TEMPLATES[role_key]

    # Tính toán độ phức tạp tự động nếu không chỉ định rõ
    if complexity == "auto":
        score = 0
        scope_len = len(scope)
        if scope_len > 100:
            score += 1
        if scope_len > 300:
            score += 2
        if files_count >= 3:
            score += 1
        if files_count >= 6:
            score += 2
        
        # Keyword checks
        heavy_keywords = ["crud", "toàn diện", "full", "hệ thống", "quản lý", "module", "tích hợp", "e2e", "refactor"]
        for kw in heavy_keywords:
            if kw in scope.lower():
                score += 1

        if score <= 1:
            detected_complexity = "low"
        elif score <= 3:
            detected_complexity = "medium"
        else:
            detected_complexity = "high"
    else:
        detected_complexity = complexity.lower()

    # Tính N workers
    if detected_complexity == "low":
        worker_count = 1
    elif detected_complexity == "medium":
        worker_count = min(len(templates), max(2, min(3, files_count if files_count > 0 else 2)))
    else:  # high
        worker_count = min(len(templates), max(3, min(5, files_count if files_count > 0 else 4)))

    selected_workers = []
    for i in range(worker_count):
        tmpl = templates[i]
        selected_workers.append({
            "worker_id": f"subagent-{role_key}-{tmpl['suffix']}",
            "role_title": tmpl["role"],
            "assigned_task": tmpl["task"],
            "recommended_api_tier": tmpl["tier"],
            "api_command_example": f"hub gemini --tier {tmpl['tier']} --prompt \"{tmpl['task']}\""
        })

    plan = {
        "lead_role": f"lead-{role_key}",
        "complexity": detected_complexity,
        "files_count": files_count,
        "recommended_worker_count": worker_count,
        "parallel_execution": worker_count > 1,
        "workers": selected_workers,
        "lead_governance": {
            "anti_nesting": "Các Worker bắt buộc được tạo với EnableSubagentTools: false (Khóa cấm đẻ thêm cấp 4).",
            "model_policy": "Toàn bộ Worker kế thừa Model: inherit từ Lead.",
            "verification_step": "Mỗi Worker chạy 'hub verify <file>' trước khi nộp bài cho Lead.",
            "lead_aggregation": "Lead thu thập kết quả, chạy 'hub lint' / 'hub test' và xuất payload M2M [STATUS: DONE] lên PM."
        }
    }
    return plan


def format_markdown(plan: Dict[str, Any]) -> str:
    lines = []
    lines.append("======================================================================")
    lines.append(f"🤖 KẾ HOẠCH PHÂN NHÁNH ĐỘNG SUB-AGENT ({plan['lead_role'].upper()})")
    lines.append("======================================================================")
    lines.append(f"Độ phức tạp xác định: {plan['complexity'].upper()} | Số lượng files dự kiến: {plan['files_count']}")
    lines.append(f"Số lượng Sub-agent con khuyến nghị: {plan['recommended_worker_count']} Workers (Thực thi: {'Song song' if plan['parallel_execution'] else 'Đơn lẻ'})")
    lines.append("----------------------------------------------------------------------")
    lines.append("DANH SÁCH WORKER SUB-AGENTS DƯỚI QUYỀN:")
    
    for idx, w in enumerate(plan["workers"], 1):
        lines.append(f"  #{idx} [{w['worker_id']}]")
        lines.append(f"     Vai trò: {w['role_title']}")
        lines.append(f"     Nhiệm vụ: {w['assigned_task']}")
        lines.append(f"     Tầng API: '{w['recommended_api_tier']}' ({w['api_command_example']})")
    
    lines.append("----------------------------------------------------------------------")
    lines.append("🛡️ QUY TRÌNH QUẢN TRỊ CỦA LEAD (LEAD GOVERNANCE):")
    lines.append(f"  1. Khóa đệ quy: {plan['lead_governance']['anti_nesting']}")
    lines.append(f"  2. Đồng bộ Model: {plan['lead_governance']['model_policy']}")
    lines.append(f"  3. Kiểm định chất lượng: {plan['lead_governance']['verification_step']}")
    lines.append(f"  4. Thẩm định hợp nhất: {plan['lead_governance']['lead_aggregation']}")
    lines.append("======================================================================")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Task Fan-Out & Sub-Agent Sizing Planner")
    parser.add_argument("--role", default="backend", choices=["backend", "frontend", "qa", "ba", "architect", "cyber"], help="Lead Role")
    parser.add_argument("--scope", default="", help="Mô tả phạm vi yêu cầu hoặc tính năng")
    parser.add_argument("--files", type=int, default=1, help="Số lượng file dự kiến thay đổi/tạo mới")
    parser.add_argument("--complexity", default="auto", choices=["auto", "low", "medium", "high"], help="Độ phức tạp")
    parser.add_argument("--json", action="store_true", help="Xuất định dạng JSON cho giao thức M2M")

    args = parser.parse_args()

    plan = calculate_fanout(args.role, args.scope, args.files, args.complexity)

    if args.json:
        print(json.dumps(plan, ensure_ascii=False, indent=2))
    else:
        print(format_markdown(plan))


if __name__ == "__main__":
    main()
