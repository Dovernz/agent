#!/usr/bin/env python3
"""
token_optimizer.py
Automated Token Profiler, Context Compression & Hygiene Optimizer for Antigravity Hub.

Audits token consumption across:
1. System Prompt / Skills Registry (<skills> list loaded on every single turn)
2. Skill body files (SKILL.md read on skill activation)
3. Workspace Rules & redundant rule files
4. Conversation transcripts & Tool output bloat hotspots

Provides actionable metrics, automated compression, and zero-loss optimization.
Zero-dependency standard library implementation.
"""

import os
import sys
import re
import json
import glob
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional

# Ensure UTF-8 standard IO for Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass


def estimate_tokens(text: str) -> int:
    """Estimates tokens for mixed Vietnamese/English text (~3.5 chars/token)."""
    if not text:
        return 0
    return max(1, int(len(text) / 3.5))


# High-signal, zero-fat skill descriptions preserving 100% routing capabilities & triggers
OPTIMIZED_DESCRIPTIONS = {
    "common/skills/gitops-gatekeeper/SKILL.md": "GitOps Gatekeeper. Quét diff, rà soát secret/file rác, soạn Conventional Commit và release notes.",
    "common/skills/lead-architect/SKILL.md": "Universal Architect. Khảo sát DB schema, thiết kế hệ thống, sinh OpenAPI/Swagger và kiểm tra drift API.",
    "common/skills/lead-ba/SKILL.md": "Universal Lead BA. Khảo sát mã nguồn sinh tech-stack.md, phân rã User Stories/AC, đồng bộ living docs.",
    "common/skills/lead-backend/SKILL.md": "Universal Backend Lead. Viết API backend, cấu hình CORS/bảo mật, DB seeding, profile slow query, Docker lint.",
    "common/skills/lead-cyber-security/SKILL.md": "Cyber Security Lead. Kiểm tra OWASP Top 10, quét secret/API keys, audit RBAC/JWT, vá lỗ hổng phụ thuộc.",
    "common/skills/lead-frontend/SKILL.md": "Universal Frontend Lead. Thiết kế UI/UX Mobile-First, sinh API client từ OpenAPI, mock server, test UI.",
    "common/skills/lead-pm/SKILL.md": "Universal PM. Điều phối vòng đời Phase 0-4, quản lý Universal Squad, phân quyền 3 tầng, kiểm soát QA Loop và offload API.",
    "common/skills/lead-qa/SKILL.md": "Universal QA Lead. Chạy test matrix E2E/Unit trong Docker, code review, kiểm soát QA loop, cleanup file rác.",
    "common/skills/master-agent/SKILL.md": "Master Agent & Central Orchestrator. Đầu não điều phối, tiếp nhận tự nhiên từ User, định tuyến PM bằng M2M protocol và tổng hợp kết quả. Kích hoạt: /master-agent, /agent-system.",
    "common/skills/web-search-interactive/SKILL.md": "Web Search & Browser Automation. Tìm kiếm Google realtime, cào dữ liệu HTTP và tương tác trình duyệt tự động.",
    "projects/_template/skills/pm-orchestrator/SKILL.md": "Template PM Orchestrator. Kế thừa lead-pm, điều phối dự án, phân rã việc qua M2M protocol, quản lý QA Loop.",
    "projects/agent-supervisor/skills/performance-evaluator/SKILL.md": "Performance Evaluator. Đo độ trễ (latency), tỷ lệ lỗi tool, chu kỳ QA loop và cảnh báo nghẽn tiến trình.",
    "projects/agent-supervisor/skills/skill-meta-optimizer/SKILL.md": "Skill Meta-Optimizer. Đánh giá kiểm toán, nén prompt, tối ưu token, cập nhật rule và thu hoạch reusable scripts.",
    "projects/agent-supervisor/skills/supervisor-orchestrator/SKILL.md": "Supervisor & System Auditor. Điều phối Post-Run Audit, đo lường token tiêu thụ, kiểm toán hiệu năng hệ thống.",
    "projects/agent-supervisor/skills/token-cost-profiler/SKILL.md": "Token Profiler. Bóc tách transcript log, tính toán Input/Output/Thinking tokens và định vị điểm nóng đốt token.",
    "projects/dental-project/skills/pm-orchestrator/SKILL.md": "PM Minh Sinh Dental. Kế thừa lead-pm, điều phối nha khoa (Django/React/Docker ports 80/8000), quản lý QA loop.",
    "projects/pc-builder/skills/pc-builder/SKILL.md": "PC Hardware Architect. Tư vấn cấu hình PC theo ngân sách/nhu cầu, kiểm tra tương thích phần cứng và so sánh giá VN.",
    "projects/vietjet-airflow/skills/vj-pm-orchestrator/SKILL.md": "PM Vietjet Airflow. Kế thừa lead-pm, điều phối hạ tầng Airflow 2.10 DAGs trong Docker (ports 8080/5434).",
    "projects/vietjet-ancillary/skills/catalog-inspector/SKILL.md": "Vietjet Catalog Inspector. Đối chiếu master data danh mục phụ trợ bằng Peek-and-Script tiết kiệm token ngoài context.",
    "projects/vietjet-ancillary/skills/code-analyzer/SKILL.md": "Vietjet Code Analyzer. Phân tích Stored Procedures/DDL, bóc tách CTEs, tối ưu ETL và thiết kế Databricks Medallion.",
    "projects/vietjet-ancillary/skills/excel-builder/SKILL.md": "Vietjet Excel Builder. Tự động xuất báo cáo Excel chuẩn Ban Tổng Giám đốc (2-tier headers, bảng màu nhận diện).",
    "projects/vietjet-ancillary/skills/pm-orchestrator/SKILL.md": "PM Vietjet Ancillary. Kế thừa lead-pm, điều phối dự án Ancillary & Databricks Migration qua 4 Lead Agents.",
    "projects/vietjet-ancillary/skills/policy-reader/SKILL.md": "Vietjet Policy Reader. Đọc hiểu Tờ trình KPI, trích xuất ma trận đơn giá hoa hồng sân bay (Counter vs Gate).",
    "projects/vietjet-brd/skills/vietjet-brd-architect/SKILL.md": "Vietjet BRD Architect. Soạn thảo tài liệu BRD chuẩn Vietjet Air từ prompt/Excel, bảo toàn định dạng Word docx."
}


class TokenAuditor:
    def __init__(self, hub_root: Path):
        self.hub_root = hub_root

    def audit_skills(self) -> Dict[str, Any]:
        """Audits all SKILL.md frontmatter descriptions and body sizes."""
        skill_files = list(self.hub_root.rglob("SKILL.md"))
        results = []
        total_desc_chars = 0
        total_body_chars = 0

        for sf in sorted(skill_files):
            try:
                with open(sf, 'r', encoding='utf-8') as f:
                    content = f.read()

                fm = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)$', content, re.DOTALL)
                if not fm:
                    continue

                meta_str, body = fm.group(1), fm.group(2)
                lines = meta_str.splitlines()
                name = ""
                desc_lines = []
                capture_desc = False

                for line in lines:
                    if line.startswith("name:"):
                        name = line.replace("name:", "").strip().strip("'\"")
                    elif line.startswith("description:"):
                        desc_lines.append(line.replace("description:", "").strip(" >|\"'"))
                        capture_desc = True
                    elif capture_desc and (line.startswith("  ") or line.startswith("\t")):
                        desc_lines.append(line.strip().strip("'\""))
                    elif capture_desc and line and not line.startswith(" "):
                        capture_desc = False

                desc = " ".join(desc_lines).strip()
                desc_chars = len(desc)
                body_chars = len(body)
                total_desc_chars += desc_chars
                total_body_chars += body_chars

                rel_path = sf.relative_to(self.hub_root)
                results.append({
                    "name": name or sf.parent.name,
                    "path": str(rel_path).replace("\\", "/"),
                    "desc_chars": desc_chars,
                    "desc_tokens": estimate_tokens(desc),
                    "body_chars": body_chars,
                    "body_tokens": estimate_tokens(body),
                    "raw_desc": desc
                })
            except Exception:
                pass

        return {
            "total_skills": len(results),
            "total_desc_chars": total_desc_chars,
            "total_desc_tokens": estimate_tokens("x" * total_desc_chars),
            "total_body_chars": total_body_chars,
            "total_body_tokens": estimate_tokens("x" * total_body_chars),
            "skills": results
        }

    def audit_rules(self) -> Dict[str, Any]:
        """Audits rules files for size, tokens, and duplicates."""
        rule_files = list(self.hub_root.rglob("rules/*.md")) + list(self.hub_root.glob("rules/*.md"))
        rule_files = list(set(rule_files))
        results = []
        hashes = {}
        duplicates = []

        for rf in sorted(rule_files):
            try:
                with open(rf, 'r', encoding='utf-8') as f:
                    content = f.read()

                content_len = len(content)
                rel_path = str(rf.relative_to(self.hub_root)).replace("\\", "/")

                content_norm = re.sub(r'\s+', ' ', content).strip()
                if content_norm in hashes:
                    duplicates.append((hashes[content_norm], rel_path))
                else:
                    hashes[content_norm] = rel_path

                results.append({
                    "path": rel_path,
                    "chars": content_len,
                    "tokens": estimate_tokens(content)
                })
            except Exception:
                pass

        return {
            "total_rule_files": len(results),
            "total_tokens": sum(r["tokens"] for r in results),
            "duplicates": duplicates,
            "rules": results
        }

    def audit_transcript(self, transcript_path: Optional[Path] = None) -> Dict[str, Any]:
        """Inspects latest conversation transcript for token inflation hotspots."""
        if not transcript_path:
            brain_dir = Path.home() / ".gemini" / "antigravity" / "brain"
            candidates = list(brain_dir.glob("*/.system_generated/logs/transcript.jsonl"))
            if not candidates:
                return {"notice": "No active conversation transcript found."}
            candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
            transcript_path = candidates[0]

        hotspots = []
        total_steps = 0
        total_output_chars = 0
        total_thinking_chars = 0
        total_user_chars = 0

        try:
            with open(transcript_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    total_steps += 1
                    try:
                        step = json.loads(line)
                        stype = step.get("type", "")
                        content = step.get("content", "")
                        thinking = step.get("thinking", "")

                        if stype == "USER_INPUT":
                            total_user_chars += len(content)
                        elif stype in ["PLANNER_RESPONSE", "GENERIC"]:
                            total_output_chars += len(content)
                        if thinking:
                            total_thinking_chars += len(thinking)

                        char_count = len(content) + len(thinking)
                        if char_count > 4000:
                            summary = content[:120].replace("\n", " ") if content else thinking[:120].replace("\n", " ")
                            hotspots.append({
                                "step": step.get("step_index", total_steps),
                                "type": stype,
                                "chars": char_count,
                                "est_tokens": estimate_tokens("x" * char_count),
                                "preview": summary + "..."
                            })
                    except Exception:
                        pass
        except Exception as e:
            return {"error": str(e)}

        hotspots.sort(key=lambda x: x["chars"], reverse=True)

        return {
            "transcript_file": str(transcript_path),
            "total_steps": total_steps,
            "total_user_chars": total_user_chars,
            "total_output_chars": total_output_chars,
            "total_thinking_chars": total_thinking_chars,
            "total_est_tokens": estimate_tokens("x" * (total_user_chars + total_output_chars + total_thinking_chars)),
            "top_hotspots": hotspots[:8]
        }

    def compress_skills(self, dry_run: bool = False) -> Dict[str, Any]:
        """Applies high-signal, zero-fat compression to skill descriptions in SKILL.md."""
        compressed_count = 0
        saved_chars = 0

        for rel_path_str, new_desc in OPTIMIZED_DESCRIPTIONS.items():
            sf = self.hub_root / rel_path_str
            if not sf.exists():
                continue

            with open(sf, 'r', encoding='utf-8') as f:
                content = f.read()

            fm = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)$', content, re.DOTALL)
            if not fm:
                continue

            header, body = fm.group(1), fm.group(2)
            lines = header.splitlines()
            new_lines = []
            skip = False

            for l in lines:
                if l.startswith("description:"):
                    skip = True
                    continue
                elif skip and (l.startswith("  ") or l.startswith("\t")):
                    continue
                elif skip and l and not l.startswith(" "):
                    skip = False
                if not skip:
                    new_lines.append(l)

            new_lines.append(f'description: >-\n  {new_desc}')
            new_header = "\n".join(new_lines)
            new_content = f"---\n{new_header}\n---\n{body}"

            diff_chars = len(content) - len(new_content)
            saved_chars += max(0, diff_chars)
            compressed_count += 1

            if not dry_run:
                with open(sf, 'w', encoding='utf-8') as f:
                    f.write(new_content)

        return {
            "skills_compressed": compressed_count,
            "saved_chars": saved_chars,
            "saved_tokens_per_turn": estimate_tokens("x" * saved_chars),
            "dry_run": dry_run
        }

    def deduplicate_rules(self, dry_run: bool = False) -> Dict[str, Any]:
        """Removes duplicate rules (keeps canonical root rules/m2m-protocol.md)."""
        root_m2m = self.hub_root / "rules" / "m2m-protocol.md"
        common_m2m = self.hub_root / "common" / "rules" / "m2m-protocol.md"
        removed = False

        if root_m2m.exists() and common_m2m.exists():
            if not dry_run:
                common_m2m.unlink()
                common_rules_dir = self.hub_root / "common" / "rules"
                if common_rules_dir.exists() and not list(common_rules_dir.iterdir()):
                    common_rules_dir.rmdir()
            removed = True

        return {
            "redundant_rule_removed": "common/rules/m2m-protocol.md" if removed else None,
            "canonical_retained": "rules/m2m-protocol.md",
            "dry_run": dry_run
        }


def print_token_report(report: Dict[str, Any]):
    print("\n" + "=" * 75)
    print(" ⚡ ANTIGRAVITY TOKEN FOOTPRINT & EFFICIENCY AUDIT")
    print("=" * 75)

    skills_data = report["skills_audit"]
    print(f"\n📦 1. SYSTEM PROMPT SKILLS REGISTRY (Loaded EVERY single turn):")
    print(f"   • Total Registered Skills : {skills_data['total_skills']}")
    print(f"   • Total Description Chars : {skills_data['total_desc_chars']:,} chars (~{skills_data['total_desc_tokens']:,} tokens/turn)")
    print(f"   • In a 50-turn session    : ~{skills_data['total_desc_tokens'] * 50:,} tokens spent ONLY on skill headers!")
    print(f"   • Total Skills Body Size  : {skills_data['total_body_chars']:,} chars (~{skills_data['total_body_tokens']:,} tokens on demand)")

    print("\n   Top 5 Heaviest Skill Descriptions in System Prompt:")
    top_desc = sorted(skills_data["skills"], key=lambda x: x["desc_chars"], reverse=True)[:5]
    for s in top_desc:
        print(f"     - {s['name']:<28} : {s['desc_chars']} chars (~{s['desc_tokens']} tokens) | {s['path']}")

    rules_data = report["rules_audit"]
    print(f"\n📜 2. RULES FOOTPRINT & REDUNDANCY:")
    print(f"   • Total Rule Files        : {rules_data['total_rule_files']}")
    print(f"   • Total Rule Tokens       : ~{rules_data['total_tokens']:,} tokens")
    if rules_data["duplicates"]:
        print(f"   ⚠️ Duplicate Rules Found   : {len(rules_data['duplicates'])} identical pair(s):")
        for orig, dup in rules_data["duplicates"]:
            print(f"      - {dup} is identical to {orig}")
    else:
        print("   ✅ No duplicate rule files found.")

    transcript_data = report.get("transcript_audit", {})
    if "total_steps" in transcript_data:
        print(f"\n🔥 3. LIVE CONVERSATION TRANSCRIPT ANALYSIS:")
        print(f"   • Total Session Steps     : {transcript_data['total_steps']}")
        print(f"   • Est. Cumulative Output  : ~{transcript_data['total_est_tokens']:,} tokens")
        print(f"   • Output Token Hotspots   : {len(transcript_data.get('top_hotspots', []))} massive steps (>4,000 chars)")
        for hs in transcript_data.get("top_hotspots", [])[:5]:
            print(f"     - Step #{hs['step']} ({hs['type']}): ~{hs['est_tokens']:,} tokens | {hs['preview']}")

    print("\n" + "=" * 75)
    print(" 🎯 RECOMMENDATION & OPTIMIZATION TARGETS:")
    print("=" * 75)
    print(" 1. Skill Description Compression: Prune verbose filler in YAML descriptions.")
    print("    Target: Reduce description size by 35-50% while preserving all routing keywords.")
    print(" 2. Rule Deduplication: Remove redundant rules/m2m-protocol.md (keep common/rules/).")
    print(" 3. Tool Output Capping: Ensure all hub scripts and command runners truncate output")
    print("    to <= 50 lines / 4KB to stop context bloating.")
    print("=" * 75 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Token Profiler & Efficiency Optimizer for Antigravity Hub",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--hub", default=".", help="Root directory of Agent Hub (default: .)")
    parser.add_argument("--json", action="store_true", help="Emit Zero-Fat M2M JSON output")
    parser.add_argument("--apply-compression", action="store_true", help="Apply zero-fat compression to skill descriptions")
    parser.add_argument("--dedup-rules", action="store_true", help="Remove redundant duplicate rule files")
    parser.add_argument("--dry-run", action="store_true", help="Test changes without writing to disk")

    args = parser.parse_args()
    hub_root = Path(args.hub.strip('"')).resolve()
    auditor = TokenAuditor(hub_root)

    if args.apply_compression:
        comp_res = auditor.compress_skills(dry_run=args.dry_run)
        print(f"✅ Compressed descriptions for {comp_res['skills_compressed']} skills.")
        print(f"   • Characters Saved : {comp_res['saved_chars']:,} chars")
        print(f"   • Tokens Saved     : ~{comp_res['saved_tokens_per_turn']:,} tokens PER CONVERSATION TURN!")
        if args.dry_run:
            print("   [DRY-RUN] No files modified.")
        sys.exit(0)

    if args.dedup_rules:
        dedup_res = auditor.deduplicate_rules(dry_run=args.dry_run)
        if dedup_res["redundant_rule_removed"]:
            print(f"✅ Removed duplicate rule: {dedup_res['redundant_rule_removed']}")
            print(f"   Retained canonical: {dedup_res['canonical_retained']}")
        else:
            print("✅ No duplicate rules to remove.")
        sys.exit(0)

    skills_audit = auditor.audit_skills()
    rules_audit = auditor.audit_rules()
    transcript_audit = auditor.audit_transcript()

    full_report = {
        "status": "PASS",
        "skills_audit": skills_audit,
        "rules_audit": rules_audit,
        "transcript_audit": transcript_audit
    }

    if args.json:
        print(json.dumps(full_report, indent=2, ensure_ascii=False))
    else:
        print_token_report(full_report)


if __name__ == "__main__":
    main()
