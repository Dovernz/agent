#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gemini Task Offloader (Zero-Dependency)
Mục đích: Đẩy các tác vụ nặng (tóm tắt văn bản dài, đọc file log, sinh mock data)
sang mô hình Gemini qua API ngoài (Free Tier - 0đ) để tiết kiệm token cho Antigravity.
"""

import os
import sys
import json
import argparse
import urllib.request
import urllib.error
from pathlib import Path

# Đảm bảo mã hóa UTF-8 cho Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

DEFAULT_MODEL = "gemini-3.5-flash"
API_BASE = "https://generativelanguage.googleapis.com/v1beta/models"


def load_env_api_key() -> str:
    """Tự động đọc GEMINI_API_KEY từ file .env hoặc biến môi trường."""
    key = os.environ.get("GEMINI_API_KEY")
    if key and key.strip():
        return key.strip()

    # Tìm file .env trong thư mục cha hoặc thư mục gốc repo
    current_dir = Path(__file__).resolve().parent
    repo_root = current_dir.parent.parent
    env_paths = [
        repo_root / ".env",
        current_dir.parent / ".env",
        Path.cwd() / ".env"
    ]

    for env_file in env_paths:
        if env_file.exists():
            try:
                with open(env_file, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("GEMINI_API_KEY=") and not line.startswith("#"):
                            val = line.split("=", 1)[1].strip().strip('"').strip("'")
                            if val:
                                return val
            except Exception:
                pass

    return ""


def call_gemini(
    prompt: str,
    file_path: str = None,
    out_file: str = None,
    model: str = DEFAULT_MODEL,
    system_instruction: str = None,
    temperature: float = 0.2
) -> dict:
    """Gửi yêu cầu tới Gemini REST API và lưu kết quả."""
    api_key = load_env_api_key()
    if not api_key:
        print("[STATUS: FAIL] Không tìm thấy GEMINI_API_KEY trong .env hoặc môi trường.")
        print("Vui lòng cấu hình GEMINI_API_KEY trong D:\\Thành\\Agent\\.env")
        sys.exit(1)

    # Đọc nội dung file nếu được cung cấp
    full_prompt = prompt
    if file_path:
        f_path = Path(file_path).resolve()
        if not f_path.exists():
            print(f"[STATUS: FAIL] Không tìm thấy tệp đầu vào: {file_path}")
            sys.exit(1)
        try:
            with open(f_path, "r", encoding="utf-8", errors="replace") as f:
                file_content = f.read()
            full_prompt = (
                f"{prompt}\n\n"
                f"--- NỘI DUNG TỆP ({f_path.name}) ---\n"
                f"{file_content}\n"
                f"--- HẾT TỆP ---"
            )
        except Exception as e:
            print(f"[STATUS: FAIL] Lỗi khi đọc tệp {file_path}: {e}")
            sys.exit(1)

    url = f"{API_BASE}/{model}:generateContent?key={api_key}"

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": full_prompt}
                ]
            }
        ],
        "generationConfig": {
            "temperature": temperature
        }
    }

    if system_instruction:
        payload["system_instruction"] = {
            "parts": [{"text": system_instruction}]
        }

    data_bytes = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data_bytes,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw_response = json.loads(resp.read().decode("utf-8"))
            
            # Trích xuất văn bản trả lời
            parts = raw_response.get("candidates", [{}])[0].get("content", {}).get("parts", [])
            text_out = "".join(p.get("text", "") for p in parts).strip()
            
            # Thống kê token (nếu có từ Google)
            usage = raw_response.get("usageMetadata", {})
            prompt_tokens = usage.get("promptTokenCount", 0)
            candidate_tokens = usage.get("candidatesTokenCount", 0)

            print(f"[STATUS: PASS] Đã xử lý thành công qua Gemini ({model}).")
            print(f"[INFO] Tokens ngoài luồng: {prompt_tokens} in / {candidate_tokens} out (Hoàn toàn 0đ - Tiết kiệm quota Antigravity).")

            # Lưu vào file đầu ra hoặc in ra stdout
            if out_file:
                out_path = Path(out_file).resolve()
                out_path.parent.mkdir(parents=True, exist_ok=True)
                with open(out_path, "w", encoding="utf-8") as f:
                    f.write(text_out)
                print(f"[OUTPUT_SAVED] Kết quả đã được ghi vào: {out_path}")
            else:
                print("--- KẾT QUẢ ---")
                print(text_out)
                print("--- HẾT ---")

            return {
                "success": True,
                "output": text_out,
                "prompt_tokens": prompt_tokens,
                "candidate_tokens": candidate_tokens
            }

    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8", errors="replace")
        if e.code == 429:
            print("[STATUS: RATE_LIMITED] Đã chạm giới hạn Free Tier (15 RPM). Hệ thống bảo vệ tự động ngắt để KHÔNG BAO GIỜ bị charge phí.")
            print("Đề xuất: Vui lòng đợi 30-60 giây rồi thử lại.")
        else:
            print(f"[STATUS: FAIL] Lỗi HTTP {e.code}: {err_msg}")
        sys.exit(1)
    except Exception as e:
        print(f"[STATUS: FAIL] Lỗi kết nối mạng: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Gemini Task Offloader CLI")
    parser.add_argument("--prompt", "-p", required=True, help="Câu lệnh / prompt cần xử lý")
    parser.add_argument("--file", "-f", help="Đường dẫn file cần gửi kèm (txt, md, json, log...)")
    parser.add_argument("--out", "-o", help="Đường dẫn file để ghi kết quả (md, json, txt...)")
    parser.add_argument("--model", "-m", default=DEFAULT_MODEL, help=f"Mô hình Gemini (mặc định: {DEFAULT_MODEL})")
    parser.add_argument("--sys", "-s", help="System instruction tùy chọn")
    parser.add_argument("--temp", "-t", type=float, default=0.2, help="Temperature (0.0 - 1.0)")

    args = parser.parse_args()

    call_gemini(
        prompt=args.prompt,
        file_path=args.file,
        out_file=args.out,
        model=args.model,
        system_instruction=args.sys,
        temperature=args.temp
    )


if __name__ == "__main__":
    main()
