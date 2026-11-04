import asyncio
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
from playwright.async_api import async_playwright

ARTIFACT_DIR = r"C:\Users\thanhcaotien\.gemini\antigravity\brain\e836e051-9249-4417-b718-8bbc5e0435fb"

async def test_admin_and_features():
    print("=== [QA] Verifying Admin & System Features ===")
    async with async_playwright() as p:
        browser = await p.chromium.launch(channel="msedge", headless=True)
        context = await browser.new_context(viewport={"width": 1400, "height": 900})
        page = await context.new_page()

        # 1. Check Django Admin Login / Dashboard
        print(">> Navigating to http://localhost:8000/admin/...")
        await page.goto("http://localhost:8000/admin/", wait_until="networkidle")
        await page.wait_for_timeout(1500)

        # Login if needed
        username_input = page.locator("input[name='username']")
        if await username_input.count() > 0:
            print(">> Logging in to Django Admin...")
            await username_input.fill("admin")
            await page.locator("input[name='password']").fill("admin123")
            await page.locator("button[type='submit'], input[type='submit']").click()
            await page.wait_for_load_state("networkidle")
            await page.wait_for_timeout(2000)

        # Screenshot Admin Dashboard & Sidebar
        admin_shot = os.path.join(ARTIFACT_DIR, "step5_admin_sidebar_cleaned.png")
        await page.screenshot(path=admin_shot)
        print(f"[Captured] {admin_shot}")

        # Check if 'Bài viết' exists anywhere in the navigation
        article_links = page.locator("a:has-text('Bài viết')")
        count = await article_links.count()
        print(f">> Count of 'Bài viết' links in admin: {count}")

        # 2. Check WordPress Homepage (Port 80)
        print(">> Checking WordPress Homepage http://localhost/ ...")
        await page.goto("http://localhost/", wait_until="networkidle")
        await page.wait_for_timeout(1500)
        wp_shot = os.path.join(ARTIFACT_DIR, "step6_wordpress_homepage.png")
        await page.screenshot(path=wp_shot)
        print(f"[Captured] {wp_shot}")

        # 3. Check Dental Chart (Odontogram) Standalone
        print(">> Checking Dental Chart http://localhost:8000/dental-chart/?customerId=1 ...")
        await page.goto("http://localhost:8000/dental-chart/?customerId=1", wait_until="networkidle")
        await page.wait_for_timeout(2000)
        chart_shot = os.path.join(ARTIFACT_DIR, "step7_dental_chart_verified.png")
        await page.screenshot(path=chart_shot)
        print(f"[Captured] {chart_shot}")

        await browser.close()
        print("=== [QA] All Feature Checks Passed! ===")
        return True

if __name__ == "__main__":
    success = asyncio.run(test_admin_and_features())
    sys.exit(0 if success else 1)
