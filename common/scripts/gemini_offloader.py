#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gemini Smart Key Pool & Task Offloader (Zero-Dependency)
==============================================================================
TÍNH NĂNG CỐT LÕI:
1. Multi-Project Key Pool: Hỗ trợ nạp N khóa API từ các Google Cloud Projects độc lập.
2. Round-Robin Load Balancing: Tự động xoay vòng khóa phân tán tải qua file trạng thái nguyên tử.
3. Auto-Failover on 429: Khi một khóa chạm ngưỡng (HTTP 429), tự động chuyển sang khóa kế tiếp.
4. Concurrency & Multi-threading: Cho phép nhiều Agent/Sub-agent gọi đồng thời đa luồng mà không nghẽn.
5. Zero-Cost: Vận hành 100% trên Free Tier (0 VNĐ), tiết kiệm triệt để quota của Antigravity.
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

DEFAULT_MODEL = "gemini-3.5-flash"
API_BASE = "https://generativelanguage.googleapis.com/v1beta/models"


def get_repo_root() -> Path:
    """Trả về thư mục gốc của Agent Hub."""
    current_dir = Path(__file__).resolve().parent
    return current_dir.parent.parent


def get_state_file() -> Path:
    """Trả về đường dẫn file lưu trạng thái luân chuyển khóa."""
    state_dir = get_repo_root() / "logs"
    state_dir.mkdir(parents=True, exist_ok=True)
    return state_dir / "gemini_pool_state.json"


def load_keys_from_env() -> List[str]:
    """Tự động đọc danh sách khóa API từ file .env hoặc biến môi trường."""
    keys: List[str] = []

    # 1. Kiểm tra biến môi trường trực tiếp
    raw_env_keys = os.environ.get("GEMINI_API_KEYS") or os.environ.get("GEMINI_API_KEY")
    if raw_env_keys:
        for k in raw_env_keys.replace(";", ",").replace("\n", ",").split(","):
            cleaned = k.strip().strip('"').strip("'")
            if cleaned and cleaned not in keys:
                keys.append(cleaned)

    # 2. Tìm file .env trong các thư mục cấu hình
    repo_root = get_repo_root()
    env_paths = [
        repo_root / ".env",
        Path.cwd() / ".env"
    ]

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
    """Quản trị viên luân chuyển và điều phối danh sách API Keys."""

    def __init__(self, keys: List[str]):
        if not keys:
            raise ValueError("Không tìm thấy bất kỳ GEMINI_API_KEY nào trong .env!")
        self.keys = keys
        self.state_file = get_state_file()

    def _read_state(self) -> Dict:
        """Đọc trạng thái pool (chỉ số vòng lặp và danh sách cooldown)."""
        if self.state_file.exists():
            try:
                with open(self.state_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {"current_index": 0, "cooldowns": {}}

    def _write_state(self, state: Dict):
        """Ghi trạng thái an toàn."""
        try:
            with open(self.state_file, "w", encoding="utf-8") as f:
                json.dump(state, f, indent=2)
        except Exception:
            pass

    def get_candidate_keys(self) -> List[Tuple[int, str]]:
        """Trả về danh sách các key hợp lệ, sắp xếp theo thứ tự Round-Robin."""
        state = self._read_state()
        now = time.time()
        cooldowns = state.get("cooldowns", {})
        idx = state.get("current_index", 0) % len(self.keys)

        # Cập nhật index cho tiến trình tiếp theo
        state["current_index"] = (idx + 1) % len(self.keys)
        self._write_state(state)

        # Xếp thứ tự bắt đầu từ index hiện tại
        ordered = []
        for i in range(len(self.keys)):
            k_idx = (idx + i) % len(self.keys)
            k_val = self.keys[k_idx]
            # Kiểm tra xem key có đang bị cooldown do 429 không
            cd_until = cooldowns.get(k_val, 0)
            if now >= cd_until:
                ordered.append((k_idx + 1, k_val))

        # Nếu tất cả đều cooldown, trả về toàn bộ theo thứ tự ban đầu để thử
        if not ordered:
            ordered = [(i + 1, k) for i, k in enumerate(self.keys)]

        return ordered

    def mark_rate_limited(self, key: str, cooldown_seconds: int = 60):
        """Đánh dấu một key bị 429 và cho tạm nghỉ."""
        state = self._read_state()
        cooldowns = state.get("cooldowns", {})
        cooldowns[key] = time.time() + cooldown_seconds
        state["cooldowns"] = cooldowns
        self._write_state(state)


def call_gemini_with_failover(
    prompt: str,
    file_path: Optional[str] = None,
    out_file: Optional[str] = None,
    model: str = DEFAULT_MODEL,
    system_instruction: Optional[str] = None,
    temperature: float = 0.2
) -> Dict:
    """Thực thi gọi Gemini API với cơ chế tự động chuyển khóa (Auto-Failover)."""
    keys = load_keys_from_env()
    if not keys:
        print("[STATUS: FAIL] Không tìm thấy GEMINI_API_KEYS trong file D:\\Thành\\Agent\\.env")
        sys.exit(1)

    pool = SmartKeyPool(keys)
    candidates = pool.get_candidate_keys()

    # Chuẩn bị payload câu hỏi
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
    # Thử lần lượt các key trong pool
    for key_id, key in candidates:
        url = f"{API_BASE}/{model}:generateContent?key={key}"
        req = urllib.request.Request(
            url,
            data=data_bytes,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                res = json.loads(resp.read().decode("utf-8"))
                parts = res.get("candidates", [{}])[0].get("content", {}).get("parts", [])
                text_out = "".join(p.get("text", "") for p in parts).strip()

                usage = res.get("usageMetadata", {})
                p_tokens = usage.get("promptTokenCount", 0)
                c_tokens = usage.get("candidatesTokenCount", 0)

                key_masked = f"{key[:8]}...{key[-4:]}"
                print(f"[STATUS: PASS] Hoàn thành qua Key #{key_id} ({key_masked}) | Model: {model}")
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
                    "output": text_out,
                    "prompt_tokens": p_tokens,
                    "candidate_tokens": c_tokens
                }

        except urllib.error.HTTPError as e:
            err_msg = e.read().decode("utf-8", errors="replace")
            last_error = f"HTTP {e.code}: {err_msg}"
            if e.code == 429:
                print(f"[WARN] Key #{key_id} chạm ngưỡng 15 RPM. Đang tự động chuyển sang Key kế tiếp...")
                pool.mark_rate_limited(key, cooldown_seconds=60)
                continue
            else:
                print(f"[WARN] Key #{key_id} gặp lỗi {e.code}. Đang thử key dự phòng tiếp theo...")
                continue
        except Exception as e:
            last_error = str(e)
            print(f"[WARN] Key #{key_id} gặp lỗi mạng ({e}). Đang thử key tiếp theo...")
            continue

    print(f"[STATUS: FAIL] Toàn bộ {len(keys)} khóa trong Pool đều tạm thời bận hoặc gặp lỗi.")
    print(f"Chi tiết lỗi cuối: {last_error}")
    sys.exit(1)


def show_pool_status():
    """Hiển thị bảng tình trạng của toàn bộ Pool Keys."""
    keys = load_keys_from_env()
    print("=" * 65)
    print(f"📊 BẢNG ĐIỀU KHIỂN GEMINI SMART KEY POOL ({len(keys)} PROJECTS)")
    print("=" * 65)
    if not keys:
        print("[!] Không tìm thấy khóa nào trong .env!")
        return

    pool = SmartKeyPool(keys)
    state = pool._read_state()
    now = time.time()
    cooldowns = state.get("cooldowns", {})
    curr_idx = state.get("current_index", 0) % len(keys)

    print(f"Tổng số dự án kết nối: {len(keys)}")
    print(f"Tổng hạn mức toàn hệ thống: {len(keys) * 15} Requests/Phút (RPM) | {len(keys) * 1500} Requests/Ngày (RPD)")
    print(f"Vị trí vòng xoay tiếp theo: Key #{curr_idx + 1}")
    print("-" * 65)
    print(f"{'STT':<5} | {'Mã Khóa (Masked)':<24} | {'Trạng Thái':<15} | {'Thời Gian Nghỉ'}")
    print("-" * 65)

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
    print("=" * 65)


def run_batch_parallel(tasks: List[Dict], max_workers: int = 5):
    """Chạy đa luồng nhiều tác vụ cùng lúc, phân bổ cho các key trong pool."""
    print(f"[*] Bắt đầu thực thi đa luồng {len(tasks)} tác vụ với {max_workers} workers song song...")
    start_time = time.time()
    results = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(
                call_gemini_with_failover,
                prompt=t["prompt"],
                file_path=t.get("file"),
                out_file=t.get("out"),
                model=t.get("model", DEFAULT_MODEL)
            ): t for t in tasks
        }

        for fut in as_completed(futures):
            t_info = futures[fut]
            try:
                res = fut.result()
                results.append(res)
            except Exception as e:
                print(f"[!] Lỗi tác vụ {t_info.get('prompt')[:30]}: {e}")

    total_time = round(time.time() - start_time, 2)
    print(f"[STATUS: PASS] Đã hoàn thành {len(results)}/{len(tasks)} tác vụ đa luồng trong {total_time} giây!")


def main():
    parser = argparse.ArgumentParser(description="Gemini Smart Key Pool & Offloader CLI")
    parser.add_argument("--prompt", "-p", help="Câu lệnh / prompt cần xử lý")
    parser.add_argument("--file", "-f", help="Đường dẫn file đầu vào gửi kèm (txt, md, json...)")
    parser.add_argument("--out", "-o", help="Đường dẫn file lưu kết quả đầu ra (md, json...)")
    parser.add_argument("--model", "-m", default=DEFAULT_MODEL, help=f"Mô hình Gemini (mặc định: {DEFAULT_MODEL})")
    parser.add_argument("--sys", "-s", help="System instruction tùy chọn")
    parser.add_argument("--temp", "-t", type=float, default=0.2, help="Temperature (0.0 - 1.0)")
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
        model=args.model,
        system_instruction=args.sys,
        temperature=args.temp
    )


if __name__ == "__main__":
    main()
