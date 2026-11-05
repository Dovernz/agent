import asyncio
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
from playwright.async_api import async_playwright

async def inspect_chart_and_booking():
    async with async_playwright() as p:
        browser = await p.chromium.launch(channel="msedge", headless=True)
        page = await browser.new_page()

        page.on("console", lambda m: print(f"[Console] {m.text}"))

        print(">> Navigating to Dental Chart...")
        await page.goto("http://localhost:8000/dental-chart/?customerId=1", wait_until="networkidle")
        await page.wait_for_timeout(3000)

        # Inspect teeth buttons/svgs
        html = await page.inner_html("#dental-chart-root")
        print(">> Chart Root HTML length:", len(html))
        # Print some buttons or classes found
        buttons = await page.locator("button").all_inner_texts()
        print(">> Buttons on Dental Chart:", buttons[:10])

        # Test selecting tooth & saving
        teeth = page.locator("div[role='button'], button, svg g, .cursor-pointer")
        print(">> Clickable elements on Dental Chart:", await teeth.count())

        await browser.close()

if __name__ == "__main__":
    asyncio.run(inspect_chart_and_booking())
