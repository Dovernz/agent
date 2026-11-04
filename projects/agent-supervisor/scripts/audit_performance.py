#!/usr/bin/env python3
"""
Performance, Token & Script Reusability Auditor for Antigravity Multi-Agent System
Analyzes conversation transcripts, quantifies token usage, evaluates tool execution,
detects repeatedly generated scripts for promotion to common/scripts, and generates
actionable optimization advice.
"""

import os
import sys
import json
import glob
import re
from datetime import datetime

# Ensure UTF-8 standard IO for Windows Terminal
if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def find_latest_transcript(explicit_path=None):
    if explicit_path and os.path.exists(explicit_path):
        return explicit_path
    
    brain_dir = os.path.expanduser(r"~/.gemini/antigravity/brain")
    if not os.path.exists(brain_dir):
        return None
        
    pattern = os.path.join(brain_dir, "*", ".system_generated", "logs", "transcript.jsonl")
    candidates = glob.glob(pattern)
    if not candidates:
        return None
    # Pick the most recently modified transcript
    candidates.sort(key=os.path.getmtime, reverse=True)
    return candidates[0]

def analyze_transcript(transcript_path):
    if not os.path.exists(transcript_path):
        return {"error": f"File not found: {transcript_path}"}
        
    steps = []
    with open(transcript_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    steps.append(json.loads(line))
                except Exception:
                    pass
                    
    total_steps = len(steps)
    if total_steps == 0:
        return {"error": "Empty transcript"}
        
    type_counts = {}
    tool_counts = {}
    tool_errors = 0
    total_prompt_chars = 0
    total_completion_chars = 0
    total_thinking_chars = 0
    timestamps = []
    
    created_scripts = {}
    hotspots = []
    
    for s in steps:
        stype = s.get("type", "UNKNOWN")
        type_counts[stype] = type_counts.get(stype, 0) + 1
        
        created = s.get("created_at")
        if created:
            try:
                ts = datetime.fromisoformat(created.replace('Z', '+00:00'))
                timestamps.append(ts)
            except Exception:
                pass
                
        content = s.get("content", "")
        if isinstance(content, str):
            if stype == "USER_INPUT":
                total_prompt_chars += len(content)
            elif stype in ["PLANNER_RESPONSE", "GENERIC"]:
                total_completion_chars += len(content)
                
        thinking = s.get("thinking", "")
        if isinstance(thinking, str):
            total_thinking_chars += len(thinking)
            
        tool_calls = s.get("tool_calls", [])
        if isinstance(tool_calls, list):
            for tc in tool_calls:
                # check actual tool function
                call_info = tc.get("call", {})
                call_args = call_info.get("args", {}) if isinstance(call_info, dict) else {}
                if not call_args:
                    call_args = tc
                    
                tool_func = call_info.get("name") if isinstance(call_info, dict) else None
                if not tool_func:
                    for k in ["run_command", "read_file", "write_file", "edit_file", "manage_subagents", "invoke_subagent"]:
                        if k in tc:
                            tool_func = k
                            break
                if not tool_func:
                    tool_func = tc.get("toolSummary") or "custom_tool"
                    
                tool_counts[tool_func] = tool_counts.get(tool_func, 0) + 1
                
                # Detect generated scripts from write_file
                f_path = call_args.get("Path") or call_args.get("TargetFile")
                if f_path and any(f_path.endswith(ext) for ext in [".py", ".ps1", ".sh", ".js", ".ts", ".sql"]):
                    fname = os.path.basename(f_path)
                    created_scripts[fname] = created_scripts.get(fname, 0) + 1
                    
                # Detect generated scripts from terminal commands (e.g. cat << 'EOF' > script.py or python -c "..." > script.py)
                cmd_line = call_args.get("CommandLine", "")
                if cmd_line:
                    script_matches = re.findall(r'>+\s*([a-zA-Z0-9_\-\.\/\\\:]+\.(?:py|ps1|sh|js|ts|sql))', cmd_line)
                    for sm in script_matches:
                        fname = os.path.basename(sm)
                        created_scripts[fname] = created_scripts.get(fname, 0) + 1
                
        status = s.get("status")
        if status == "ERROR":
            tool_errors += 1
            hotspots.append({
                "step_index": s.get("step_index"),
                "type": stype,
                "reason": "Step marked as ERROR"
            })
            
    # Calculate duration
    duration_sec = 0
    if len(timestamps) >= 2:
        duration_sec = (max(timestamps) - min(timestamps)).total_seconds()
        
    # Heuristic Token estimation (~3.8 characters per token for mixed Vietnamese & code)
    prompt_tokens = int(total_prompt_chars / 3.8)
    completion_tokens = int(total_completion_chars / 3.8)
    thinking_tokens = int(total_thinking_chars / 3.8)
    total_tokens = prompt_tokens + completion_tokens + thinking_tokens
    
    # Efficiency scoring (1-100)
    score = 100
    if tool_errors > 0:
        score -= min(30, tool_errors * 5)
    if total_tokens > 150000:
        score -= min(25, int((total_tokens - 150000) / 20000))
    if duration_sec > 600:
        score -= min(15, int((duration_sec - 600) / 120))
    score = max(30, score)
    
    # Analyze scripts for promotion to common/scripts or project scripts
    promotable_scripts = []
    for sname, count in created_scripts.items():
        # Identify common patterns (qa_*, inspect_*, test_*, rewrite_*, append_*, seed_*)
        is_pattern = any(sname.startswith(p) for p in ["qa_", "test_", "inspect_", "rewrite_", "append_", "seed_", "audit_"])
        if count >= 1 and is_pattern:
            promotable_scripts.append({
                "script_name": sname,
                "generation_count": count,
                "recommendation": "Đóng gói tham số hóa đưa vào `common/scripts/` hoặc `projects/<dự án>/scripts/`"
            })
            
    # Generate recommendations
    recommendations = []
    if promotable_scripts:
        script_list_str = ", ".join([f"`{item['script_name']}`" for item in promotable_scripts[:4]])
        recommendations.append(
            f"Phát hiện các script thường xuyên được tạo để chạy thử/test: {script_list_str}. "
            "Đề xuất: Tham số hóa và chuyển thẳng vào `common/scripts/` hoặc thư mục `scripts/` của dự án để tái sử dụng ngay bằng lệnh CLI, "
            "tiết kiệm ~1,500 - 3,500 tokens và 30-60 giây cho mỗi lần chạy lặp lại."
        )
    if tool_counts.get("read_file", 0) > 10:
        recommendations.append("Phát hiện gọi `read_file` nhiều lần (>10 lượt). Cần siết chặt quy tắc Peek-and-Script, chỉ đọc Header + 3 dòng mẫu và dùng script ngoài context.")
    if tool_errors > 2:
        recommendations.append(f"Có {tool_errors} lệnh gặp lỗi/chạy lại. Cần tăng cường kiểm thử nội bộ Shift-Left trước khi bàn giao sang QA.")
    if thinking_tokens > completion_tokens * 1.5:
        recommendations.append("Lượng Thinking tokens cao vượt trội so với Output code. Cần cô đọng các tệp SKILL.md để giảm tải thời gian suy luận logic của mô hình.")
    if not recommendations:
        recommendations.append("Hiệu năng phiên làm việc rất tối ưu. Tiếp tục duy trì chuẩn giao tiếp M2M Zero-Fat và Inherit Model.")
        
    return {
        "transcript_file": transcript_path,
        "total_steps": total_steps,
        "duration_minutes": round(duration_sec / 60, 2),
        "steps_by_type": type_counts,
        "top_tools": dict(sorted(tool_counts.items(), key=lambda x: x[1], reverse=True)[:8]),
        "tool_errors": tool_errors,
        "created_scripts": created_scripts,
        "promotable_scripts": promotable_scripts,
        "token_metrics": {
            "estimated_prompt_tokens": prompt_tokens,
            "estimated_completion_tokens": completion_tokens,
            "estimated_thinking_tokens": thinking_tokens,
            "estimated_total_tokens": total_tokens
        },
        "efficiency_score": score,
        "recommendations": recommendations
    }

def format_markdown_report(data):
    if "error" in data:
        return f"# Audit Error\n{data['error']}"
        
    tm = data["token_metrics"]
    dt_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    tools_md = "\n".join([f"| `{k}` | {v} |" for k, v in data["top_tools"].items()])
    recs_md = "\n".join([f"- 💡 {r}" for r in data["recommendations"]])
    
    scripts_section = ""
    if data.get("promotable_scripts"):
        scripts_rows = "\n".join([f"| `{s['script_name']}` | {s['generation_count']} | {s['recommendation']} |" for s in data["promotable_scripts"]])
        scripts_section = f"""
---

## ♻️ 3. Đánh Giá Khả Năng Tái Sử Dụng Mã Nguồn (Script Harvester & Promotion)

Phát hiện các mã nguồn thường xuyên được sinh ra tự động trong phiên chạy:

| Tên Script | Số lần tạo/gọi | Đề xuất tối ưu hóa tái sử dụng |
| :--- | :--- | :--- |
{scripts_rows}
"""
    
    md = f"""# Báo Cáo Giám Sát Hiệu Năng, Đo Đạc Token & Tái Sử Dụng Script

- **Thời gian lập báo cáo:** `{dt_str}`
- **Tập tin transcript:** `{data['transcript_file']}`
- **Thời lượng phiên làm việc:** `{data['duration_minutes']} phút`
- **Tổng số bước xử lý (Steps):** `{data['total_steps']}`
- **Điểm hiệu năng tổng thể:** `{data['efficiency_score']}/100`

---

## 📊 1. Bảng Định Lượng Token Tiêu Thụ

| Hạng mục Token | Số lượng ước tính | Tỷ trọng |
| :--- | :--- | :--- |
| **Input / Prompt Tokens** | `{tm['estimated_prompt_tokens']:,}` | `{round(tm['estimated_prompt_tokens']/max(1, tm['estimated_total_tokens'])*100, 1)}%` |
| **Output / Completion Tokens** | `{tm['estimated_completion_tokens']:,}` | `{round(tm['estimated_completion_tokens']/max(1, tm['estimated_total_tokens'])*100, 1)}%` |
| **Thinking / Reasoning Tokens** | `{tm['estimated_thinking_tokens']:,}` | `{round(tm['estimated_thinking_tokens']/max(1, tm['estimated_total_tokens'])*100, 1)}%` |
| **TỔNG LƯỢNG TOKEN** | **`{tm['estimated_total_tokens']:,}`** | **100%** |

---

## 🛠️ 2. Thống Kê Công Cụ Thực Thi (Tool Calls)

| Công cụ / Thao tác | Số lần gọi |
| :--- | :--- |
{tools_md}

- **Số bước gặp lỗi (Tool Errors):** `{data['tool_errors']}`
{scripts_section}
---

## 🎯 4. Đề Xuất Tối Ưu Hóa & Nâng Cấp Skill (Meta-Learning Advice)

{recs_md}
"""
    return md

if __name__ == "__main__":
    t_path = sys.argv[1] if len(sys.argv) > 1 else None
    target_file = find_latest_transcript(t_path)
    if not target_file:
        print(json.dumps({"error": "No transcript found."}))
        sys.exit(1)
        
    analysis = analyze_transcript(target_file)
    
    if "--json" in sys.argv:
        print(json.dumps(analysis, indent=2, ensure_ascii=False))
    else:
        report = format_markdown_report(analysis)
        print(report)
        
        # Save report
        report_dir = os.path.dirname(os.path.abspath(__file__))
        report_out = os.path.join(os.path.dirname(report_dir), "reports", f"audit_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
        try:
            with open(report_out, "w", encoding="utf-8") as rf:
                rf.write(report)
            print(f"\n[+] Đã lưu báo cáo tại: {report_out}")
        except Exception:
            pass
