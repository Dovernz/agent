import asyncio
import os
import sys

# Force utf-8 stdout
sys.stdout.reconfigure(encoding='utf-8')

from playwright.async_api import async_playwright

ARTIFACT_DIR = r"C:\Users\thanhcaotien\.gemini\antigravity\brain\e836e051-9249-4417-b718-8bbc5e0435fb"

async def test_booking_flow():
    print("=== [QA START] Automated E2E Booking Flow ===")
    async with async_playwright() as p:
        browser = await p.chromium.launch(channel="msedge", headless=True)
        context = await browser.new_context(viewport={"width": 1280, "height": 950})
        page = await context.new_page()

        # Capture console messages
        page.on("console", lambda msg: print(f"[Browser Console] {msg.text}"))

        # Navigate to booking page
        print(">> Navigating to http://localhost:8000/booking/...")
        await page.goto("http://localhost:8000/booking/", wait_until="networkidle")
        await page.wait_for_timeout(2500)

        # ---------------- STEP 1: CHỌN CƠ SỞ ----------------
        shot1_1 = os.path.join(ARTIFACT_DIR, "step1_clinic_list.png")
        await page.screenshot(path=shot1_1)
        print(f"[Captured] {shot1_1}")

        clinic_cards = page.locator(".grid > div.cursor-pointer")
        card_count = await clinic_cards.count()
        print(f">> Found {card_count} clinics.")
        if card_count == 0:
            print("ERROR: No clinics found!")
            await browser.close()
            return False

        # Click first clinic card
        await clinic_cards.first.click()
        await page.wait_for_timeout(1500)

        shot1_2 = os.path.join(ARTIFACT_DIR, "step1_clinic_selected.png")
        await page.screenshot(path=shot1_2)
        print(f"[Captured] {shot1_2}")

        # Click "Tiếp tục"
        next_btn_1 = page.locator("button:has-text('Tiếp tục')")
        await next_btn_1.click()
        await page.wait_for_timeout(1500)

        # ---------------- STEP 2: THÔNG TIN KHÁCH HÀNG ----------------
        shot2_1 = os.path.join(ARTIFACT_DIR, "step2_patient_form.png")
        await page.screenshot(path=shot2_1)
        print(f"[Captured] {shot2_1}")

        # Fill Patient Info
        name_input = page.locator("input[placeholder*='Nguyễn Văn A']").first
        await name_input.fill("Nguyễn Thu Trang")

        phone_input = page.locator("input[placeholder*='0987654321']").first
        await phone_input.fill("0988776655")

        email_input = page.locator("input[type='email']").first
        await email_input.fill("thutrang.qa@minhsinh.vn")

        dob_input = page.locator("input[placeholder*='1990']").first
        await dob_input.fill("1996")

        # Select service category
        cat_select = page.locator("select").first
        options = await cat_select.locator("option").all()
        print(f">> Found {len(options)} service options.")
        if len(options) > 1:
            val = await options[1].get_attribute("value")
            await cat_select.select_option(val)
            print(f">> Selected category value: {val}")

        await page.wait_for_timeout(1000)

        shot2_2 = os.path.join(ARTIFACT_DIR, "step2_patient_filled.png")
        await page.screenshot(path=shot2_2)
        print(f"[Captured] {shot2_2}")

        # Click "Tiếp tục" to Step 3
        next_btn_2 = page.locator("button:has-text('Tiếp tục')")
        await next_btn_2.click()
        await page.wait_for_timeout(2500)

        # ---------------- STEP 3: MA TRẬN GHẾ & CHỌN GIỜ ----------------
        shot3_1 = os.path.join(ARTIFACT_DIR, "step3_chair_matrix.png")
        await page.screenshot(path=shot3_1)
        print(f"[Captured] {shot3_1}")

        # Click on an available time row in the matrix
        clickable_cells = page.locator(".cursor-pointer")
        cell_count = await clickable_cells.count()
        print(f">> Found {cell_count} clickable slots in matrix.")

        selected_slot = False
        for i in range(cell_count):
            cell = clickable_cells.nth(i)
            text = await cell.inner_text()
            if "Kín lịch" not in text:
                print(f">> Clicking slot index {i}")
                await cell.click()
                selected_slot = True
                await page.wait_for_timeout(1500)
                break

        if not selected_slot and cell_count > 0:
            await clickable_cells.first.click()
            await page.wait_for_timeout(1500)

        shot3_2 = os.path.join(ARTIFACT_DIR, "step3_chair_selected.png")
        await page.screenshot(path=shot3_2)
        print(f"[Captured] {shot3_2}")

        # ---------------- STEP 4: HOÀN TẤT ĐẶT LỊCH ----------------
        submit_btn = page.locator("button:has-text('Hoàn tất Đặt lịch')")
        is_enabled = await submit_btn.is_enabled()
        print(f">> Submit button enabled: {is_enabled}")

        if is_enabled:
            print(">> Submitting booking...")
            async with page.expect_response(lambda r: "/api/bookings/" in r.url, timeout=15000) as response_info:
                await submit_btn.click()
            
            response = await response_info.value
            status = response.status
            body = await response.text()
            print(f">> API /api/bookings/ HTTP Status: {status}")
            print(f">> API Response: {body}")

            await page.wait_for_timeout(4000)

            shot4 = os.path.join(ARTIFACT_DIR, "step4_booking_confirmation.png")
            await page.screenshot(path=shot4)
            print(f"[Captured] {shot4}")

            print("=== [QA DONE] Booking test finished successfully! ===")
            await browser.close()
            return True
        else:
            print("ERROR: Submit button was not enabled.")
            await browser.close()
            return False

if __name__ == "__main__":
    success = asyncio.run(test_booking_flow())
    sys.exit(0 if success else 1)
