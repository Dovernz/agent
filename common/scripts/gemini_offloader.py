#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gemini Smart Key Pool & Dynamic Model Router (Zero-Dependency)
==============================================================================
TÍNH NĂNG CỐT LÕI:
1. Multi-Tier Model Allocation: Tự động phân bổ công việc theo đúng hạn mức Quota từ Google AI Studio:
   - Tier Bulk / Fast: `gemini-3.5-flash-lite` (15 RPM, 500 RPD / project)
   - Tier Standard: `gemini-3.6-flash` (5 RPM, 20 RPD / project)
   - Tier Deep Reasoning: `gemini-3.8-flash` (5 RPM, 20 RPD / project)
   - Tier Ultra-Frequency: `gemma-4-26b-a4b-it` (30 RPM, 14,400 RPD / project)
2. Smart Key Pool: Xoay vòng 7 Projects độc lập (Round-Robin).
3. Cross-Model Fallback: Nếu một model chạm giới hạn 429, tự động fallback sang model dự phòng.
4. Auto-Failover on 429: Chuyển sang Project Key kế tiếp trong 0.1 giây.
==============================================================================
"""

import os
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
        "fallbacks": ["gemini-3.5-flash-lite", "gemini-3-flash-preview"],
        "desc": "Tác vụ tiêu chuẩn (Viết code API, dàn layout UI, giải thích nghiệp vụ) [20 RPD/project]"
    },
    "deep": {
        "primary": "gemini-3.8-flash",
        "fallbacks": ["gemini-3.6-flash", "gemini-3.5-flash-lite"],
        "desc": "Tác vụ suy luận chuyên sâu (Kiến trúc hệ thống, fix bug phức tạp) [20 RPD/project]"
    },
    "ultra": {
        "primary": "gemma-4-26b-a4b-it",
        "fallbacks": ["gemini-3.5-flash-lite"],
        "desc": "Tác vụ siêu tần suất (Format chuỗi, trích xuất regex, lặp hàng nghìn lần) [14,400 RPD/project]"
    }
}

DEFAULT_TIER = "bulk"
API_BASE = "https://generativelanguage.googleapis.com/v1beta/models"


def get_repo_root() -> Path:
    current_dir = Path(__file__).resolve().parent
    return current_dir.parent.parent


def get_state_file() -> Path:
    state_dir = get_repo_root() / "logs"
    state_dir.mkdir(parents=True, exist_ok=True)
    return state_dir / "gemini_pool_state.json"


def load_keys_from_env() -> List[str]:
    keys: List[str] = []
    raw_env_keys = os.environ.get("GEMINI_API_KEYS") or os.environ.get("GEMINI_API_KEY")
    if raw_env_keys:
        for k in raw_env_keys.replace(";", ",").replace("\n", ",").split(","):
            cleaned = k.strip().strip('"').strip("'")
            if cleaned and cleaned not in keys:
                keys.append(cleaned)

    repo_root = get_repo_root()
    env_paths = [repo_root / ".env", Path.cwd() / ".env"]

    for env_file in env_paths:
        if env_file.exists():
            try:
                with open(env_file, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("#"):
                            continue
                        if line.startswith("GEMINI_API_KEYS=") or line.startswith("GEMINI_API_KEY="):
                            val = line.split("=", 1)[1].strip().strip('"').strip("'")
                            for k in val.replace(";", ",").split(","):
                                cleaned = k.strip().strip('"').strip("'")
                                if cleaned and cleaned not in keys:
                                    keys.append(cleaned)
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
        return {"current_index": 0, "cooldowns": {}}

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

    # Xác định danh sách model ưu tiên theo tier
    tier_info = MODEL_TIERS.get(tier.lower(), MODEL_TIERS[DEFAULT_TIER])
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
                f"--- HẾT TỆP ---"
            )
        except Exception as e:
            print(f"[STATUS: FAIL] Lỗi đọc file {file_path}: {e}")
            sys.exit(1)

    payload = {
        "contents": [{"parts": [{"text": full_prompt}]}],
        "generationConfig": {"temperature": temperature}
    }
    if system_instruction:
        payload["system_instruction"] = {"parts": [{"text": system_instruction}]}

    data_bytes = json.dumps(payload).encode("utf-8")

    last_error = ""
    # Vòng lặp thử qua các Model và các Key trong Pool
    for current_model in models_to_try:
        for key_id, key in candidates:
            url = f"{API_BASE}/{current_model}:generateContent?key={key}"
            req = urllib.request.Request(
                url,
                data=data_bytes,
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            try:
                # Với model deep reasoning thì timeout lâu hơn
                req_timeout = 35 if "3.8" in current_model else 15
                with urllib.request.urlopen(req, timeout=req_timeout) as resp:
                    res = json.loads(resp.read().decode("utf-8"))
                    parts = res.get("candidates", [{}])[0].get("content", {}).get("parts", [])
                    text_out = "".join(p.get("text", "") for p in parts).strip()

                    usage = res.get("usageMetadata", {})
                    p_tokens = usage.get("promptTokenCount", 0)
                    c_tokens = usage.get("candidatesTokenCount", 0)

                    key_masked = f"{key[:8]}...{key[-4:]}"
                    print(f"[STATUS: PASS] Hoàn thành qua Key #{key_id} ({key_masked}) | Model: {current_model} (Tier: {tier})")
                    print(f"[INFO] Tokens ngoài luồng: {p_tokens} in / {c_tokens} out (Hoàn toàn 0đ - Tiết kiệm quota Antigravity).")

                    if out_file:
                        out_path = Path(out_file).resolve()
                        out_path.parent.mkdir(parents=True, exist_ok=True)
                        with open(out_path, "w", encoding="utf-8") as f:
                            f.write(text_out)
                        print(f"[OUTPUT_SAVED] Kết quả đã lưu tại: {out_path}")
                    else:
                        print("--- KẾT QUẢ ---")
                        print(text_out)
                        print("--- HẾT ---")

                    return {
                        "success": True,
                        "key_id": key_id,
                        "model": current_model,
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
                    # Model không khả dụng, chuyển sang model tiếp theo ngay
                    break
                else:
                    continue
            except Exception as e:
                last_error = str(e)
                continue

    print(f"[STATUS: FAIL] Toàn bộ các model trong tier [{tier}] và pool {len(keys)} khóa đều tạm thời bận.")
    print(f"Chi tiết lỗi cuối: {last_error}")
    sys.exit(1)


def show_pool_status():
    keys = load_keys_from_env()
    print("=" * 70)
    print(f"📊 BẢNG ĐIỀU KHIỂN TOÀN DIỆN GEMINI SMART KEY POOL ({len(keys)} PROJECTS)")
    print("=" * 70)
    if not keys:
        print("[!] Không tìm thấy khóa nào trong .env!")
        return

    pool = SmartKeyPool(keys)
    state = pool._read_state()
    now = time.time()
    cooldowns = state.get("cooldowns", {})
    curr_idx = state.get("current_index", 0) % len(keys)

    print(f"Tổng số dự án kết nối: {len(keys)}")
    print(f"Vị trí vòng xoay tiếp theo: Key #{curr_idx + 1}")
    print("-" * 70)
    print("⚡ MA TRẬN PHÂN BỔ HẠN MỨC THEO TIER (TỔNG 7 PROJECTS):")
    print(f"  🔹 Tier 'bulk'   (gemini-3.5-flash-lite) : 105 RPM | 3,500 Requests/Ngày (Cho tác vụ nặng/tóm tắt)")
    print(f"  🔹 Tier 'standard'(gemini-3.6-flash)      :  35 RPM |   140 Requests/Ngày (Cho viết code API/UI)")
    print(f"  🔹 Tier 'deep'   (gemini-3.8-flash)      :  35 RPM |   140 Requests/Ngày (Cho suy luận kiến trúc sâu)")
    print(f"  🔹 Tier 'ultra'  (gemma-4-26b-a4b-it)    : 210 RPM | 100,800 Requests/Ngày (Cho format/regex lặp lại)")
    print(f"  🔹 Search Grounding (Tìm kiếm Google)    : 10,500 Lượt tìm kiếm Google / Ngày")
    print("-" * 70)
    print(f"{'STT':<5} | {'Mã Khóa (Masked)':<24} | {'Trạng Thái':<15} | {'Thời Gian Nghỉ'}")
    print("-" * 70)

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
        print(f"#{i:<4} | {masked:<24} | {status:<15} | {rem_str}")
    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(description="Gemini Smart Key Pool & Dynamic Model Router CLI")
    parser.add_argument("--prompt", "-p", help="Câu lệnh / prompt cần xử lý")
    parser.add_argument("--file", "-f", help="Đường dẫn file đầu vào gửi kèm (txt, md, json...)")
    parser.add_argument("--out", "-o", help="Đường dẫn file lưu kết quả đầu ra (md, json...)")
    parser.add_argument("--tier", "-t", default=DEFAULT_TIER, choices=list(MODEL_TIERS.keys()),
                        help="Phân tầng mô hình: bulk (mặc định - 3.5k req), standard (3.6), deep (3.8), ultra (gemma)")
    parser.add_argument("--model", "-m", help="Chỉ định đích danh tên model nếu không muốn dùng tier")
    parser.add_argument("--sys", "-s", help="System instruction tùy chọn")
    parser.add_argument("--temp", type=float, default=0.2, help="Temperature (0.0 - 1.0)")
    parser.add_argument("--pool-status", action="store_true", help="Kiểm tra trạng thái các khóa trong Pool")

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
