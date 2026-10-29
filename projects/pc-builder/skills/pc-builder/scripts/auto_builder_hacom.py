#!/usr/bin/env python3
"""
HACOM Live Web PC Auto-Builder
Automates browsing https://hacom.vn/buildpc using Playwright and Google Chrome.
Clicks interactive category buttons, searches components, adds them to the build list,
and captures the resulting configuration screenshot with total price.
"""

import sys
import os
import json
import time
import argparse

if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def run_hacom_build(components: dict, output_screenshot: str = "hacom_build_result.png", headless: bool = True):
    from playwright.sync_api import sync_playwright

    pw = sync_playwright().start()
    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    launch_kwargs = {"headless": headless}
    if os.path.exists(chrome_path):
        launch_kwargs["executable_path"] = chrome_path

    browser = pw.chromium.launch(**launch_kwargs)
    page = browser.new_page(viewport={"width": 1400, "height": 950})
    
    print("[1] Đang kết nối tới HACOM Build PC (https://hacom.vn/buildpc)...")
    page.goto('https://hacom.vn/buildpc', timeout=35000)
    page.wait_for_load_state("domcontentloaded")
    time.sleep(2)

    added_items = []
    failed_items = []

    # Mapping of component types to HACOM button text
    BUTTON_MAP = {
        "cpu": "Chọn Bộ vi xử lý",
        "mainboard": "Chọn Bo mạch chủ",
        "ram": "Chọn RAM",
        "ssd": "Chọn SSD",
        "vga": "Chọn Card màn hình",
        "psu": "Chọn Nguồn",
        "case": "Chọn Vỏ case",
        "cooler": "Chọn Tản nhiệt"
    }

    for comp_type, search_term in components.items():
        btn_label = BUTTON_MAP.get(comp_type.lower())
        if not btn_label:
            continue
        try:
            print(f"[*] Đang thêm [{comp_type.upper()}]: tìm từ khóa '{search_term}'...")
            btn = page.wait_for_selector(f'button:has-text("{btn_label}")', timeout=7000)
            btn.click()

            search_input = page.wait_for_selector('input[placeholder*="Tìm kiếm sản phẩm"]', timeout=7000)
            search_input.fill("")
            search_input.fill(search_term)
            search_input.press("Enter")
            time.sleep(2)

            them_btn = page.wait_for_selector('[role="dialog"] button:has-text("Thêm")', timeout=7000)
            them_btn.click()
            time.sleep(1.5)
            added_items.append({"type": comp_type, "query": search_term, "status": "ADDED"})
            print(f"  [+] Đã thêm thành công: {search_term}")
        except Exception as e:
            failed_items.append({"type": comp_type, "query": search_term, "error": str(e)})
            print(f"  [-] Bỏ qua hoặc không tìm thấy: {search_term}")
            # Try to close dialog if still open
            try:
                close_btn = page.query_selector('[role="dialog"] button[aria-label*="Close"], [role="dialog"] button:has-text("Đóng")')
                if close_btn:
                    close_btn.click()
            except Exception:
                pass

    time.sleep(2)
    # Capture screenshot
    page.screenshot(path=output_screenshot, full_page=False)
    print(f"[2] Đã chụp ảnh màn hình cấu hình thực tế: {output_screenshot}")

    # Extract summary price
    price_info = page.evaluate("""() => {
        let total = "";
        document.querySelectorAll('*').forEach(el => {
            if (el.innerText && (el.innerText.includes('Chi phí dự tính') || el.innerText.includes('Tổng tiền:'))) {
                const lines = el.innerText.split('\\n').map(s => s.trim()).filter(Boolean);
                if (lines.length >= 2 && !total) {
                    total = lines.join(' : ');
                }
            }
        });
        return total;
    }""")

    browser.close()
    pw.stop()

    return {
        "status": "SUCCESS",
        "retailer": "HACOM",
        "url": "https://hacom.vn/buildpc",
        "added_components": added_items,
        "failed_components": failed_items,
        "screenshot_saved": output_screenshot,
        "price_summary": price_info if price_info else "Xem chi tiết trong ảnh chụp màn hình"
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Live PC Auto-Builder on HACOM")
    parser.add_argument("--cpu", type=str, default="i5 13500")
    parser.add_argument("--ram", type=str, default="32GB 3200")
    parser.add_argument("--ssd", type=str, default="Kingston 1TB")
    parser.add_argument("--vga", type=str, default="GTX 1650")
    parser.add_argument("--psu", type=str, default="550W")
    parser.add_argument("--out", type=str, default="hacom_build_result.png")
    parser.add_argument("--headed", action="store_true", help="Run with visible browser window")

    args = parser.parse_args()
    build_dict = {
        "cpu": args.cpu,
        "ram": args.ram,
        "ssd": args.ssd,
        "vga": args.vga,
        "psu": args.psu
    }
    res = run_hacom_build(build_dict, output_screenshot=args.out, headless=not args.headed)
    print(json.dumps(res, ensure_ascii=False, indent=2))
