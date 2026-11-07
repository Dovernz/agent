import urllib.request
import json
import sys

sys.stdout.reconfigure(encoding="utf-8")

def test_pool_status():
    url = "http://localhost:8090/api/pool-status"
    req = urllib.request.Request(url)
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            if resp.status != 200:
                print(f"[FAIL] Pool status HTTP {resp.status}")
                return False
            data = json.loads(resp.read().decode("utf-8"))
            total_keys = data.get("total_keys", 0)
            if total_keys != 7:
                print(f"[FAIL] Expected 7 keys, got {total_keys}")
                return False
            print(f"[PASS] Key pool healthy: {total_keys} keys active")
            return True
    except Exception as e:
        print(f"[FAIL] Could not connect to {url}: {e}")
        return False

def test_translation():
    url = "http://localhost:8090/api/translate"
    payload = json.dumps({"text": "Hello world", "stream": False}).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            if resp.status != 200:
                print(f"[FAIL] Translate HTTP {resp.status}")
                return False
            data = json.loads(resp.read().decode("utf-8"))
            translated = data.get("translated_text", "")
            if not translated:
                print("[FAIL] Empty translation output")
                return False
            print(f"[PASS] Translation successful: '{translated}'")
            return True
    except Exception as e:
        print(f"[FAIL] Translation request failed: {e}")
        return False

if __name__ == "__main__":
    p_ok = test_pool_status()
    t_ok = test_translation()
    if p_ok and t_ok:
        print("\nALL BASELINE TESTS PASSED (100/100)")
        sys.exit(0)
    else:
        print("\nBASELINE TESTS FAILED")
        sys.exit(1)
