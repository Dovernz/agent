import asyncio
import os
from playwright.async_api import async_playwright

ARTIFACT_DIR = r"C:\Users\thanhcaotien\.gemini\antigravity\brain\e836e051-9249-4417-b718-8bbc5e0435fb"

async def run_e2e():
    async with async_playwright() as p:
        browser = await p.chromium.launch(channel="msedge", headless=True)
        context = await browser.new_context(viewport={"width": 1280, "height": 900})
        page = await context.new_page()

        print("[QA Step 1] Navigating to http://localhost:8000/booking/...")
        await page.goto("http://localhost:8000/booking/", wait_until="networkidle")
        await page.wait_for_timeout(2000)

        # Step 1: Screenshot initial form (Select Clinic)
        shot1 = os.path.join(ARTIFACT_DIR, "booking_step1_clinic.png")
        await page.screenshot(path=shot1, full_page=False)
        print(f"✓ Step 1 captured: {shot1}")

        # Check clinics rendered
        clinic_btns = page.locator("button:has-text('Cơ sở')")
        count = await clinic_btns.count()
        print(f"Found {count} clinic buttons.")

        # Click first clinic
        if count > 0:
            await clinic_btns.first.click()
            await page.wait_for_timeout(2000)
        else:
            # Maybe clinics are cards with click listener
            cards = page.locator(".cursor-pointer, [role='button']")
            if await cards.count() > 0:
                await cards.first.click()
                await page.wait_for_timeout(2000)

        # Step 2: Screenshot seat matrix / date selection
        shot2 = os.path.join(ARTIFACT_DIR, "booking_step2_chair_matrix.png")
        await page.screenshot(path=shot2, full_page=False)
        print(f"✓ Step 2 captured: {shot2}")

        # Find available slot / chair button
        slot_btns = page.locator("button:has-text('Ghế'), button:has-text('08:'), button:has-text('09:'), button:has-text('10:'), button:has-text('14:')")
        slot_count = await slot_btns.count()
        print(f"Found {slot_count} slot buttons.")

        if slot_count > 0:
            await slot_btns.first.click()
            await page.wait_for_timeout(1500)

        # Step 3: Screenshot customer info inputs
        shot3 = os.path.join(ARTIFACT_DIR, "booking_step3_patient_info.png")
        await page.screenshot(path=shot3, full_page=False)
        print(f"✓ Step 3 captured: {shot3}")

        # Fill inputs
        # Full name
        name_input = page.locator("input[placeholder*='Họ và tên'], input[name*='name'], input[placeholder*='Tên']").first
        if await name_input.is_visible():
            await name_input.fill("Nguyễn Văn QA")

        # Phone
        phone_input = page.locator("input[placeholder*='điện thoại'], input[name*='phone'], input[type='tel']").first
        if await phone_input.is_visible():
            await phone_input.fill("0912345678")

        # Email
        email_input = page.locator("input[placeholder*='email'], input[name*='email'], input[type='email']").first
        if await email_input.is_visible():
            await email_input.fill("qa_test@minhsinh.vn")

        # Year of birth
        yob_input = page.locator("input[placeholder*='sinh'], select[name*='year'], input[name*='dob']").first
        if await yob_input.is_visible():
            await yob_input.fill("1995")

        # Select service category dropdown if visible
        cat_select = page.locator("select").first
        if await cat_select.is_visible():
            options = await cat_select.locator("option").all()
            if len(options) > 1:
                val = await options[1].get_attribute("value")
                if val:
                    await cat_select.select_option(val)

        await page.wait_for_timeout(1000)

        # Screenshot filled form
        shot3_filled = os.path.join(ARTIFACT_DIR, "booking_step3_filled.png")
        await page.screenshot(path=shot3_filled, full_page=False)
        print(f"✓ Step 3 filled captured: {shot3_filled}")

        # Submit button
        submit_btn = page.locator("button:has-text('Xác nhận đặt lịch'), button:has-text('Đặt lịch ngay'), button[type='submit']")
        print(f"Submit button visible: {await submit_btn.first.is_visible()}")
        if await submit_btn.first.is_visible():
            await submit_btn.first.click()
            print("Clicked submit button! Waiting for response...")
            await page.wait_for_timeout(4000)

        # Step 4: Screenshot booking result / confirmation
        shot4 = os.path.join(ARTIFACT_DIR, "booking_step4_result.png")
        await page.screenshot(path=shot4, full_page=False)
        print(f"✓ Step 4 captured: {shot4}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_e2e())
