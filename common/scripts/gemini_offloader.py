#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gemini Smart Key Pool & Dynamic Model Router (Zero-Dependency)
==============================================================================
TÍNH NĂNG CỐT LÕI:
1. Auto-Triage & Complexity Classifier: Tự động đánh giá độ phức tạp của task để chọn Model phù hợp nhất.
2. Multi-Tier Model Allocation: Tự động phân bổ công việc theo đúng hạn mức Quota từ Google AI Studio:
   - Tier Bulk / Fast: `gemini-3.5-flash-lite` (15 RPM, 500 RPD / project)
   - Tier Standard: `gemini-3.6-flash` (5 RPM, 20 RPD / project)
   - Tier Deep Reasoning: `gemini-3.8-flash` (5 RPM, 20 RPD / project)
   - Tier Ultra-Frequency: `gemma-4-26b-a4b-it` (30 RPM, 14,400 RPD / project)
3. Smart Key Pool: Xoay vòng 7 Projects độc lập (Round-Robin).
4. Real-time Telemetry & Usage Tracker: Ghi nhận chính xác số request & token đã dùng theo từng model cho từng key.
5. Cross-Model Fallback: Nếu một model chạm giới hạn 429, tự động fallback sang model dự phòng.
6. Auto-Failover on 429: Chuyển sang Project Key kế tiếp trong 0.1 giây.
==============================================================================
"""

import os
import re
import sys
import time
import json
import argparse
import urllib.request
import urllib.error
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

# Đảm bảo mã hóa UTF-8 cho Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Định nghĩa các tầng mô hình theo hạn mức Google AI Studio
MODEL_TIERS = {
    "bulk": {
        "primary": "gemini-3.5-flash-lite",
        "fallbacks": ["gemini-3.1-flash-lite", "gemini-3.6-flash", "gemma-4-26b-a4b-it"],
        "desc": "Tác vụ khối lượng lớn (Tóm tắt file dài, sinh mock data, đọc log) [500 RPD/project]"
    },
    "standard": {
        "primary": "gemini-3.6-flash",
        "fallbacks": ["gemini-3.8-flash", "gemini-3.5-flash-lite"],
        "desc": "Tác vụ tiêu chuẩn (Sinh code API, viết serializers, components UI) [20 RPD/project]"
    },
    "deep": {
        "primary": "gemini-3.8-flash",
        "fallbacks": ["gemini-3.6-flash"],
        "desc": "Suy luận sâu & Kiến trúc (Tối ưu query phức tạp, phân tích DDL, RBAC) [20 RPD/project]"
    },
    "ultra": {
        "primary": "gemma-4-26b-a4b-it",
        "fallbacks": ["gemma-4-31b-it", "gemini-3.5-flash-lite"],
        "desc": "Tần suất cực cao (Xử lý regex, phân loại văn bản, mapping cột bảng) [14,400 RPD/project]"
    }
}

# Hạn mức định lượng theo từng model trên 1 Project (Google AI Studio Free Tier)
MODEL_LIMITS_RPD = {
    "gemini-3.8-flash": 20,
    "gemini-3.6-flash": 20,
    "gemini-3.5-flash-lite": 500,
    "gemini-3.1-flash-lite": 500,
    "gemma-4-26b-a4b-it": 14400,
    "gemma-4-31b-it": 14400,
}

DEFAULT_TIER = "auto"
API_BASE = "https://generativelanguage.googleapis.com/v1beta/models"


def get_repo_root() -> Path:
    # Thư mục gốc repo D:\Thành\Agent
    return Path(__file__).resolve().parent.parent.parent


def get_state_file() -> Path:
    state_dir = get_repo_root() / "logs"
    state_dir.mkdir(parents=True, exist_ok=True)
    return state_dir / "gemini_pool_state.json"


def auto_classify_task(prompt: str, file_path: Optional[str] = None) -> Tuple[str, str]:
    """
    Tự động thẩm định độ phức tạp của nhiệm vụ để điều phối vào Tier tối ưu nhất.
    Trả về: (tier_name, reason)
    """
    p_lower = prompt.lower()
    
    # 1. Kiểm tra kích thước file đầu vào (nếu có)
    file_lines = 0
    file_bytes = 0
    if file_path and os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                lines = f.readlines()
                file_lines = len(lines)
                file_bytes = sum(len(line) for line in lines)
        except Exception:
            pass

    # Nếu file rất lớn (> 500 dòng hoặc > 20KB) -> Bulk/Fast Tier để cày dữ liệu không tốn quota
    if file_lines > 500 or file_bytes > 20480:
        return "bulk", f"Tệp đầu vào lớn ({file_lines} dòng, {file_bytes/1024:.1f}KB) -> Điều phối Tier 'bulk' (gemini-3.5-flash-lite)"

    # 2. Kiểm tra từ khóa yêu cầu suy luận kiến trúc sâu / bảo mật phức tạp
    deep_keywords = [
        "kiến trúc", "architecture", "tối ưu hóa csdl", "query optimization",
        "lỗ hổng bảo mật", "owasp", "rbac", "stored procedure", "medallion",
        "giải thuật", "algorithm", "phân tích sâu", "deep research"
    ]
    for kw in deep_keywords:
        if kw in p_lower:
            return "deep", f"Phát hiện yêu cầu suy luận/kiến trúc sâu ('{kw}') -> Điều phối Tier 'deep' (gemini-3.8-flash)"

    # 3. Kiểm tra từ khóa tác vụ lặp tần suất cao / regex / trích xuất thuần túy
    ultra_keywords = [
        "regex", "bóc tách chuỗi", "format json", "mapping cột", "chuẩn hóa chuỗi",
        "phân loại danh mục", "lọc dòng"
    ]
    for kw in ultra_keywords:
        if kw in p_lower:
            return "ultra", f"Phát hiện tác vụ tần suất cao ('{kw}') -> Điều phối Tier 'ultra' (gemma-4-26b-a4b-it)"

    # 4. Kiểm tra từ khóa tác vụ sinh code / giao diện / API tiêu chuẩn
    standard_keywords = [
        "viết api", "serializer", "viewset", "react component", "ui component",
        "unit test", "integration test", "crud", "refactor code", "viết hàm"
    ]
    for kw in standard_keywords:
        if kw in p_lower:
            return "standard", f"Phát hiện tác vụ sinh mã API/UI ('{kw}') -> Điều phối Tier 'standard' (gemini-3.6-flash)"

    # Mặc định an toàn cho tác vụ tổng hợp: bulk (Flash-Lite tốc độ cao, quota dồi dào)
    return "bulk", "Tác vụ tổng hợp -> Điều phối Tier 'bulk' (gemini-3.5-flash-lite, 3.5k req/ngày)"


def load_keys_from_env() -> List[str]:
    keys = []
    env_file = get_repo_root() / ".env"
    
    # 1. Đọc từ file .env nếu có
    if env_file.exists():
        try:
            with open(env_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("GEMINI_API_KEYS="):
                        val = line.split("=", 1)[1].strip().strip('"').strip("'")
                        keys = [k.strip() for k in val.split(",") if k.strip()]
                    elif line.startswith("GEMINI_API_KEY="):
                        val = line.split("=", 1)[1].strip().strip('"').strip("'")
                        if val and val not in keys:
                            keys.append(val)
        except Exception:
            pass

    # 2. Đọc từ biến môi trường OS
    if not keys:
        raw_keys = os.getenv("GEMINI_API_KEYS", "")
        if raw_keys:
            keys = [k.strip() for k in raw_keys.split(",") if k.strip()]
        else:
            single = os.getenv("GEMINI_API_KEY", "")
            if single:
                keys = [single]

    # 3. Đọc từ cấu hình antigravity toàn cục nếu có
    if not keys:
        global_env = Path.home() / ".gemini" / "antigravity" / ".env"
        if global_env.exists():
            try:
                with open(global_env, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.startswith("GEMINI_API_KEY="):
                            keys.append(line.split("=", 1)[1].strip().strip('"'))
            except Exception:
                pass

    return keys


class SmartKeyPool:
    def __init__(self, keys: List[str]):
        if not keys:
            raise ValueError("Không tìm thấy GEMINI_API_KEYS trong .env!")
        self.keys = keys
        self.state_file = get_state_file()

    def _read_state(self) -> Dict:
        if self.state_file.exists():
            try:
                with open(self.state_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {"current_index": 0, "cooldowns": {}, "daily_usage": {}}

    def _write_state(self, state: Dict):
        try:
            with open(self.state_file, "w", encoding="utf-8") as f:
                json.dump(state, f, indent=2)
        except Exception:
            pass

    def get_candidate_keys(self) -> List[Tuple[int, str]]:
        state = self._read_state()
        now = time.time()
        cooldowns = state.get("cooldowns", {})
        idx = state.get("current_index", 0) % len(self.keys)

        # Xoay chỉ số tiếp theo
        state["current_index"] = (idx + 1) % len(self.keys)
        self._write_state(state)

        ordered = []
        for i in range(len(self.keys)):
            k_idx = (idx + i) % len(self.keys)
            k_val = self.keys[k_idx]
            cd_until = cooldowns.get(k_val, 0)
            if now >= cd_until:
                ordered.append((k_idx + 1, k_val))

        if not ordered:
            ordered = [(i + 1, k) for i, k in enumerate(self.keys)]

        return ordered

    def mark_rate_limited(self, key: str, cooldown_seconds: int = 60):
        state = self._read_state()
        cooldowns = state.get("cooldowns", {})
        cooldowns[key] = time.time() + cooldown_seconds
        state["cooldowns"] = cooldowns
        self._write_state(state)

    def record_usage(self, key: str, model: str, prompt_tokens: int = 0, candidate_tokens: int = 0):
        """
        Ghi nhận nhật ký sử dụng chính xác cho từng Key và từng Model theo ngày.
        """
        state = self._read_state()
        today = time.strftime("%Y-%m-%d")
        daily_usage = state.setdefault("daily_usage", {})
        today_usage = daily_usage.setdefault(today, {})

        masked_key = f"{key[:10]}...{key[-6:]}" if len(key) > 16 else key
        key_stats = today_usage.setdefault(masked_key, {})
        model_stats = key_stats.setdefault(model, {
            "requests": 0,
            "prompt_tokens": 0,
            "candidate_tokens": 0,
            "total_tokens": 0
        })

        model_stats["requests"] += 1
        model_stats["prompt_tokens"] += prompt_tokens
        model_stats["candidate_tokens"] += candidate_tokens
        model_stats["total_tokens"] += (prompt_tokens + candidate_tokens)

        self._write_state(state)


def call_gemini_with_failover(
    prompt: str,
    file_path: Optional[str] = None,
    out_file: Optional[str] = None,
    tier: str = DEFAULT_TIER,
    explicit_model: Optional[str] = None,
    system_instruction: Optional[str] = None,
    temperature: float = 0.2
) -> Dict:
    keys = load_keys_from_env()
    if not keys:
        print("[STATUS: FAIL] Không tìm thấy GEMINI_API_KEYS trong file D:\\Thành\\Agent\\.env")
        sys.exit(1)

    pool = SmartKeyPool(keys)
    candidates = pool.get_candidate_keys()

    # Tự động thẩm định độ phức tạp nếu tier='auto'
    if tier.lower() == "auto":
        actual_tier, reason = auto_classify_task(prompt, file_path)
        print(f"[ROUTER] 🎯 Tự động điều phối: {reason}")
    else:
        actual_tier = tier.lower()
        print(f"[ROUTER] 🎯 Chỉ định thủ công Tier: [{actual_tier}]")

    tier_info = MODEL_TIERS.get(actual_tier, MODEL_TIERS["bulk"])
    if explicit_model:
        models_to_try = [explicit_model] + tier_info["fallbacks"]
    else:
        models_to_try = [tier_info["primary"]] + tier_info["fallbacks"]

    full_prompt = prompt
    if file_path:
        f_path = Path(file_path).resolve()
        if not f_path.exists():
            print(f"[STATUS: FAIL] Không tìm thấy tệp đầu vào: {file_path}")
            sys.exit(1)
        try:
            with open(f_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
            full_prompt = (
                f"{prompt}\n\n"
                f"--- NỘI DUNG TỆP ({f_path.name}) ---\n"
                f"{content}\n"
                f"--- HẾT NỘI DUNG TỆP ---"
            )
        except Exception as e:
            print(f"[WARN] Không thể đọc tệp {file_path}: {e}")

    last_error = ""

    for current_model in models_to_try:
        url = f"{API_BASE}/{current_model}:generateContent"

        payload = {
            "contents": [
                {
                    "parts": [{"text": full_prompt}]
                }
            ],
            "generationConfig": {
                "temperature": temperature
            }
        }

        if system_instruction:
            payload["systemInstruction"] = {
                "parts": [{"text": system_instruction}]
            }

        data_bytes = json.dumps(payload).encode("utf-8")

        for key_id, key in candidates:
            masked_key = f"{key[:10]}...{key[-6:]}"
            headers = {
                "Content-Type": "application/json",
                "x-goog-api-key": key
            }

            req = urllib.request.Request(url, data=data_bytes, headers=headers, method="POST")

            try:
                start_time = time.time()
                with urllib.request.urlopen(req, timeout=120) as resp:
                    resp_body = resp.read().decode("utf-8")
                    duration = time.time() - start_time
                    res_json = json.loads(resp_body)

                    candidates_list = res_json.get("candidates", [])
                    if not candidates_list:
                        print(f"[WARN] Key #{key_id} ({masked_key}) không trả về candidate nào.")
                        continue

                    text_out = candidates_list[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                    p_tokens = res_json.get("usageMetadata", {}).get("promptTokenCount", 0)
                    c_tokens = res_json.get("usageMetadata", {}).get("candidatesTokenCount", 0)

                    # Ghi nhận Telemetry & Quota usage vào local state
                    pool.record_usage(key, current_model, p_tokens, c_tokens)

                    print(f"[GEMINI_DISPATCH] ✅ Thành công | Model: {current_model} | Project: Key #{key_id} ({masked_key}) | Thời gian: {duration:.2f}s | Tokens: in={p_tokens}, out={c_tokens}")

                    if out_file:
                        out_path = Path(out_file).resolve()
                        out_path.parent.mkdir(parents=True, exist_ok=True)
                        
                        clean_content = text_out
                        ext = out_path.suffix.lower()
                        if ext in [".py", ".json", ".sql", ".js", ".ts", ".html", ".css", ".yaml", ".yml", ".sh", ".ps1"]:
                            code_match = re.search(r"```(?:[a-zA-Z0-9_-]+)?\s*\n(.*?)\n```", text_out, re.DOTALL)
                            if code_match:
                                clean_content = code_match.group(1).strip()

                        with open(out_path, "w", encoding="utf-8") as f:
                            f.write(clean_content)
                        print(f"[OUTPUT_SAVED] Kết quả đã lưu tại: {out_path}")
                        # Tự động thẩm định chất lượng tệp vừa lưu
                        try:
                            sys.path.insert(0, str(Path(__file__).resolve().parent))
                            from output_verifier import verify_file
                            v_res = verify_file(str(out_path))
                            if v_res["passed"]:
                                print(f"[VERIFIED: PASS] Thẩm định chất lượng tệp: {v_res['score']}/100 (Hợp lệ)")
                            else:
                                print(f"[VERIFIED: FAIL] Cảnh báo chất lượng ({v_res['score']}/100):")
                                for iss in v_res["issues"]:
                                    print(f"  ⚠️ {iss}")
                        except Exception:
                            pass
                    else:
                        print("--- KẾT QUẢ ---")
                        print(text_out)
                        print("--- HẾT ---")

                    return {
                        "success": True,
                        "key_id": key_id,
                        "model": current_model,
                        "tier": actual_tier,
                        "output": text_out,
                        "prompt_tokens": p_tokens,
                        "candidate_tokens": c_tokens
                    }

            except urllib.error.HTTPError as e:
                err_msg = e.read().decode("utf-8", errors="replace")
                last_error = f"HTTP {e.code}: {err_msg}"
                if e.code == 429:
                    print(f"[WARN] Key #{key_id} chạm ngưỡng với model {current_model}. Đang thử key/model tiếp theo...")
                    pool.mark_rate_limited(key, cooldown_seconds=60)
                    continue
                elif e.code == 404:
                    break
                else:
                    continue
            except Exception as e:
                last_error = str(e)
                continue

    print(f"[STATUS: FAIL] Toàn bộ các model trong tier [{actual_tier}] và pool {len(keys)} khóa đều tạm thời bận.")
    print(f"Chi tiết lỗi cuối: {last_error}")
    sys.exit(1)


def make_progress_bar(current: int, total: int, width: int = 10) -> str:
    """Tạo thanh tiến độ ASCII trực quan."""
    if total <= 0:
        return "[░" * width + "]"
    ratio = min(1.0, current / total)
    filled = int(round(ratio * width))
    bar = "█" * filled + "░" * (width - filled)
    pct = int(ratio * 100)
    return f"[{bar}] {pct:>3}%"


def show_pool_status(detailed_usage: bool = True):
    keys = load_keys_from_env()
    print("=" * 80)
    print(f"📊 BẢNG ĐIỀU KHIỂN & THEO DÕI HẠN MỨC GEMINI KEY POOL ({len(keys)} PROJECTS)")
    print("=" * 80)
    if not keys:
        print("[!] Không tìm thấy khóa nào trong .env!")
        return

    pool = SmartKeyPool(keys)
    state = pool._read_state()
    now = time.time()
    cooldowns = state.get("cooldowns", {})
    curr_idx = state.get("current_index", 0) % len(keys)
    today = time.strftime("%Y-%m-%d")
    daily_usage = state.get("daily_usage", {}).get(today, {})

    print(f"Ngày theo dõi: {today} | Tổng số dự án: {len(keys)} | Vị trí xoay vòng: Key #{curr_idx + 1}")
    print("-" * 80)
    print("⚡ MA TRẬN HẠN MỨC TOÀN HỆ THỐNG (7 PROJECTS KẾT HỢP):")
    print(f"  🔹 Tier 'bulk'    (gemini-3.5-flash-lite) : 105 RPM |   3,500 Requests/Ngày")
    print(f"  🔹 Tier 'standard' (gemini-3.6-flash)      :  35 RPM |     140 Requests/Ngày")
    print(f"  🔹 Tier 'deep'    (gemini-3.8-flash)      :  35 RPM |     140 Requests/Ngày")
    print(f"  🔹 Tier 'ultra'   (gemma-4-26b-a4b-it)    : 210 RPM | 100,800 Requests/Ngày")
    print(f"  🔹 Search Grounding (Google Live)        : 10,500 Lượt tìm kiếm Google / Ngày")
    print("-" * 80)
    print("TRẠNG THÁI KẾT NỐI TỪNG KEY:")
    print(f"{'STT':<5} | {'Mã Khóa (Masked)':<24} | {'Trạng Thái':<16} | {'Cooldown'}")
    print("-" * 80)

    for i, k in enumerate(keys, 1):
        masked = f"{k[:10]}...{k[-6:]}"
        cd_until = cooldowns.get(k, 0)
        remaining = int(cd_until - now)
        if remaining > 0:
            status = "🟡 COOLDOWN (429)"
            rem_str = f"Chờ {remaining}s"
        else:
            status = "🟢 SẴN SÀNG"
            rem_str = "Tối ưu 100%"
        print(f"#{i:<4} | {masked:<24} | {status:<16} | {rem_str}")

    print("-" * 80)
    print(f"📈 THỐNG KÊ SỬ DỤNG THEO MODEL & KEY HÔM NAY ({today}):")
    
    total_req_today = 0
    total_tokens_today = 0
    records_found = False

    for i, k in enumerate(keys, 1):
        masked = f"{k[:10]}...{k[-6:]}"
        k_stats = daily_usage.get(masked, {})
        if k_stats:
            records_found = True
            for model_name, m_data in k_stats.items():
                reqs = m_data.get("requests", 0)
                toks = m_data.get("total_tokens", 0)
                total_req_today += reqs
                total_tokens_today += toks
                limit_rpd = MODEL_LIMITS_RPD.get(model_name, 20)
                bar = make_progress_bar(reqs, limit_rpd)
                warn = "🟢 Bình thường" if reqs < limit_rpd * 0.8 else "🟡 Cảnh báo (>80%)"
                if reqs >= limit_rpd:
                    warn = "🔴 Chạm trần RPD"
                print(f"  Key #{i} ({masked}) | {model_name:<21} | {reqs:>3}/{limit_rpd:<5} RPD {bar} | {toks:>7,} tk | {warn}")

    if not records_found:
        print("  ℹ️ Hôm nay chưa có request nào được ghi nhận. Toàn bộ 7 Keys và các Model đều đạt 100% hạn mức sẵn có!")
        print("  💡 Định mức tối đa khả dụng hôm nay:")
        print("     • Gemini 3.8 Flash : 140 lượt suy luận sâu")
        print("     • Gemini 3.6 Flash : 140 lượt viết code")
        print("     • Gemini 3.5 Lite  : 3,500 lượt cày xới dữ liệu")
        print("     • Gemma 4 26B      : 100,800 lượt format/regex")
    else:
        print("-" * 80)
        print(f"  🔥 TỔNG CỘNG HÔM NAY: {total_req_today} requests | {total_tokens_today:,} tokens đã tiêu thụ.")

    print("=" * 80)


def main():
    parser = argparse.ArgumentParser(description="Gemini Smart Key Pool & Dynamic Model Router CLI")
    parser.add_argument("--prompt", "-p", help="Câu lệnh / prompt cần xử lý")
    parser.add_argument("--file", "-f", help="Đường dẫn file đầu vào gửi kèm (txt, md, json...)")
    parser.add_argument("--out", "-o", help="Đường dẫn file lưu kết quả đầu ra (md, json...)")
    parser.add_argument("--tier", "-t", default=DEFAULT_TIER, choices=["auto"] + list(MODEL_TIERS.keys()),
                        help="Phân tầng mô hình: auto (tự động thẩm định), bulk (3.5k req), standard (3.6), deep (3.8), ultra (gemma)")
    parser.add_argument("--model", "-m", help="Chỉ định đích danh tên model nếu không muốn dùng tier")
    parser.add_argument("--sys", "-s", help="System instruction tùy chọn")
    parser.add_argument("--temp", type=float, default=0.2, help="Temperature (0.0 - 1.0)")
    parser.add_argument("--pool-status", "--usage", action="store_true", help="Kiểm tra trạng thái các khóa và thống kê request đã dùng")

    args = parser.parse_args()

    if args.pool_status:
        show_pool_status()
        return

    if not args.prompt:
        parser.print_help()
        sys.exit(1)

    call_gemini_with_failover(
        prompt=args.prompt,
        file_path=args.file,
        out_file=args.out,
        tier=args.tier,
        explicit_model=args.model,
        system_instruction=args.sys,
        temperature=args.temp
    )


if __name__ == "__main__":
    main()
