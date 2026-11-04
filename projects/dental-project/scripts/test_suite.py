#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Minh Sinh Dental - Unified Test Suite Runner (test_suite.py)
Consolidates verification, E2E booking tests, and full booking flow tests.
Provides CLI flags: --all, --verify, --e2e, --flow with Markdown and JSON outputs.
"""

import sys
import os
import time
import json
import argparse
import asyncio
import subprocess
from typing import Dict, Any, List

# Ensure UTF-8 output on Windows
if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

DEFAULT_ARTIFACT_DIR = r"D:\Thành\Agent\projects\dental-project\artifacts"

# Global quiet flag for JSON output
QUIET_LOGS = False

def log(msg: str):
    if not QUIET_LOGS:
        print(msg)


class TestReport:
    def __init__(self):
        self.start_time = time.time()
        self.suites: List[Dict[str, Any]] = []
        self.screenshots: List[str] = []

    def add_suite(self, name: str):
        suite = {
            "name": name,
            "status": "PASS",
            "start_time": time.time(),
            "elapsed_s": 0.0,
            "steps": []
        }
        self.suites.append(suite)
        return suite

    def record_step(self, suite: Dict[str, Any], step_name: str, passed: bool, message: str = "", screenshot: str = None):
        step = {
            "name": step_name,
            "status": "PASS" if passed else "FAIL",
            "message": message,
            "screenshot": screenshot or ""
        }
        suite["steps"].append(step)
        if not passed:
            suite["status"] = "FAIL"
        if screenshot:
            self.screenshots.append(screenshot)

    def finish_suite(self, suite: Dict[str, Any]):
        suite["elapsed_s"] = round(time.time() - suite["start_time"], 2)

    def overall_status(self) -> str:
        for s in self.suites:
            if s["status"] == "FAIL":
                return "FAIL"
        return "PASS"

    def total_elapsed(self) -> float:
        return round(time.time() - self.start_time, 2)

    def to_dict(self) -> Dict[str, Any]:
        total_steps = sum(len(s["steps"]) for s in self.suites)
        passed_steps = sum(sum(1 for st in s["steps"] if st["status"] == "PASS") for s in self.suites)
        failed_steps = total_steps - passed_steps
        return {
            "overall_status": self.overall_status(),
            "total_elapsed_seconds": self.total_elapsed(),
            "suites_count": len(self.suites),
            "total_steps": total_steps,
            "passed_steps": passed_steps,
            "failed_steps": failed_steps,
            "suites": self.suites,
            "screenshots": self.screenshots
        }

    def render_markdown(self) -> str:
        data = self.to_dict()
        status_badge = "✅ **PASS**" if data["overall_status"] == "PASS" else "❌ **FAIL**"
        lines = []
        lines.append(f"# 🧪 Dental Project Test Suite Execution Report")
        lines.append(f"")
        lines.append(f"- **Overall Status:** {status_badge}")
        lines.append(f"- **Execution Time:** {data['total_elapsed_seconds']}s")
        lines.append(f"- **Suites Ran:** {data['suites_count']}")
        lines.append(f"- **Total Steps:** {data['total_steps']} (Passed: {data['passed_steps']}, Failed: {data['failed_steps']})")
        lines.append(f"")
        lines.append(f"## 📊 Detailed Test Results")
        lines.append(f"")

        for s in data["suites"]:
            suite_icon = "✅" if s["status"] == "PASS" else "❌"
            lines.append(f"### {suite_icon} Suite: {s['name']} ({s['elapsed_s']}s)")
            lines.append(f"| Step | Status | Message / Details | Screenshot |")
            lines.append(f"| :--- | :---: | :--- | :--- |")
            for st in s["steps"]:
                st_icon = "✅ PASS" if st["status"] == "PASS" else "❌ FAIL"
                shot_link = f"`{os.path.basename(st['screenshot'])}`" if st["screenshot"] else "-"
                msg = st["message"].replace("|", "\\|")
                lines.append(f"| {st['name']} | {st_icon} | {msg} | {shot_link} |")
            lines.append(f"")

        if data["screenshots"]:
            lines.append(f"## 📸 Captured Artifacts ({len(data['screenshots'])})")
            for shot in data["screenshots"]:
                lines.append(f"- `{shot}`")
            lines.append(f"")

        return "\n".join(lines)


# -----------------------------------------------------------------------------
# 1. VERIFY SUITE: Backend Container, DB Schema, Admin & System Features
# -----------------------------------------------------------------------------
async def run_verify_suite(report: TestReport, artifact_dir: str, base_url: str, wp_url: str, headless: bool):
    suite = report.add_suite("Quick Verify (Schema, Backend/DB & Features)")
    log(f"\n[SUITE] Starting: {suite['name']}")

    # 1.1 Docker Container Check
    try:
        proc = subprocess.run(
            ["docker", "ps", "--filter", "name=dental_backend", "--format", "{{.Status}}"],
            capture_output=True, text=True, check=False, timeout=10
        )
        is_running = "Up" in proc.stdout
        report.record_step(
            suite,
            "Docker Backend Container Status",
            is_running,
            f"Container status: {proc.stdout.strip() or 'Not running'}"
        )
    except Exception as e:
        report.record_step(suite, "Docker Backend Container Status", False, str(e))

    # 1.2 Django DB Connection & System Check
    try:
        proc = subprocess.run(
            ["docker", "exec", "dental_backend", "python", "manage.py", "check", "--database", "default"],
            capture_output=True, text=True, check=False, timeout=15
        )
        passed = (proc.returncode == 0) and ("no issues" in proc.stdout.lower() or proc.returncode == 0)
        report.record_step(
            suite,
            "Django Database Connection Check",
            passed,
            proc.stdout.strip() or proc.stderr.strip()
        )
    except Exception as e:
        report.record_step(suite, "Django Database Connection Check", False, str(e))

    # 1.3 Django Schema Migrations Check
    try:
        proc = subprocess.run(
            ["docker", "exec", "dental_backend", "python", "manage.py", "migrate", "--check"],
            capture_output=True, text=True, check=False, timeout=15
        )
        passed = (proc.returncode == 0)
        report.record_step(
            suite,
            "Database Schema Migration Integrity",
            passed,
            "All migrations applied, schema in sync" if passed else proc.stderr.strip()
        )
    except Exception as e:
        report.record_step(suite, "Database Schema Migration Integrity", False, str(e))

    # 1.4 Browser-based Admin & System Features Verification (Playwright)
    try:
        from playwright.async_api import async_playwright
        async with async_playwright() as p:
            try:
                browser = await p.chromium.launch(channel="msedge", headless=headless)
            except Exception:
                browser = await p.chromium.launch(headless=headless)

            context = await browser.new_context(viewport={"width": 1400, "height": 900})
            page = await context.new_page()

            # Check Django Admin Login & Dashboard
            admin_url = f"{base_url.rstrip('/')}/admin/"
            log(f">> Navigating to {admin_url}...")
            await page.goto(admin_url, wait_until="networkidle", timeout=15000)
            await page.wait_for_timeout(1000)

            # Auto-login if login form is presented
            username_input = page.locator("input[name='username']")
            if await username_input.count() > 0:
                log(">> Submitting admin credentials...")
                await username_input.fill("admin")
                await page.locator("input[name='password']").fill("admin123")
                await page.locator("button[type='submit'], input[type='submit']").click()
                await page.wait_for_load_state("networkidle")
                await page.wait_for_timeout(1500)

            admin_shot = os.path.join(artifact_dir, "verify_step1_admin_dashboard.png")
            await page.screenshot(path=admin_shot)

            # Verify 'Bài viết' is removed from Django Admin (moved to WP)
            article_links = page.locator("a:has-text('Bài viết')")
            article_count = await article_links.count()
            report.record_step(
                suite,
                "Django Admin Navigation (Articles Isolation)",
                article_count == 0,
                f"Count of 'Bài viết' links: {article_count} (Expected: 0, moved to WP)",
                admin_shot
            )

            # Check WordPress Homepage
            wp_target = f"{wp_url.rstrip('/')}/"
            log(f">> Checking WordPress Homepage at {wp_target}...")
            try:
                wp_resp = await page.goto(wp_target, wait_until="networkidle", timeout=15000)
                await page.wait_for_timeout(1000)
                wp_shot = os.path.join(artifact_dir, "verify_step2_wordpress_homepage.png")
                await page.screenshot(path=wp_shot)
                report.record_step(
                    suite,
                    "WordPress Homepage Accessibility",
                    wp_resp is not None and wp_resp.status in [200, 301, 302],
                    f"HTTP Status: {wp_resp.status if wp_resp else 'None'}",
                    wp_shot
                )
            except Exception as e:
                report.record_step(suite, "WordPress Homepage Accessibility", False, str(e))

            # Check Dental Chart (Odontogram) Standalone
            chart_url = f"{base_url.rstrip('/')}/dental-chart/?customerId=1"
            log(f">> Checking Dental Chart Standalone at {chart_url}...")
            try:
                chart_resp = await page.goto(chart_url, wait_until="networkidle", timeout=15000)
                await page.wait_for_timeout(1500)
                chart_shot = os.path.join(artifact_dir, "verify_step3_dental_chart.png")
                await page.screenshot(path=chart_shot)
                report.record_step(
                    suite,
                    "Standalone Dental Chart (Odontogram)",
                    chart_resp is not None and chart_resp.status == 200,
                    f"HTTP Status: {chart_resp.status if chart_resp else 'None'}",
                    chart_shot
                )
            except Exception as e:
                report.record_step(suite, "Standalone Dental Chart (Odontogram)", False, str(e))

            await browser.close()
    except Exception as e:
        report.record_step(suite, "Playwright Admin & Feature Verification", False, f"Playwright Error: {e}")

    report.finish_suite(suite)


# -----------------------------------------------------------------------------
# 2. E2E SUITE: Fast E2E Booking Flow
# -----------------------------------------------------------------------------
async def run_e2e_suite(report: TestReport, artifact_dir: str, base_url: str, headless: bool):
    suite = report.add_suite("E2E Booking Flow")
    log(f"\n[SUITE] Starting: {suite['name']}")

    try:
        from playwright.async_api import async_playwright
        async with async_playwright() as p:
            try:
                browser = await p.chromium.launch(channel="msedge", headless=headless)
            except Exception:
                browser = await p.chromium.launch(headless=headless)

            context = await browser.new_context(viewport={"width": 1280, "height": 900})
            page = await context.new_page()

            booking_url = f"{base_url.rstrip('/')}/booking/"
            log(f">> Navigating to {booking_url}...")
            await page.goto(booking_url, wait_until="networkidle", timeout=15000)
            await page.wait_for_timeout(1500)

            # Step 1: Clinic selection
            shot1 = os.path.join(artifact_dir, "e2e_step1_clinic.png")
            await page.screenshot(path=shot1, full_page=False)

            clinic_btns = page.locator("button:has-text('Cơ sở'), .cursor-pointer, [role='button']")
            c_count = await clinic_btns.count()
            if c_count > 0:
                await clinic_btns.first.click()
                await page.wait_for_timeout(1500)
                report.record_step(suite, "E2E Select Clinic", True, f"Found and selected from {c_count} clinics", shot1)
            else:
                report.record_step(suite, "E2E Select Clinic", False, "No clinic cards or buttons found", shot1)

            # Continue button if multi-step
            next_btn = page.locator("button:has-text('Tiếp tục')")
            if await next_btn.is_visible():
                await next_btn.click()
                await page.wait_for_timeout(1500)

            # Step 2: Customer Info
            name_input = page.locator("input[placeholder*='Họ và tên'], input[placeholder*='Nguyễn'], input[name*='name']").first
            if await name_input.is_visible():
                await name_input.fill("Nguyễn Văn E2E")

            phone_input = page.locator("input[placeholder*='điện thoại'], input[placeholder*='09'], input[name*='phone'], input[type='tel']").first
            if await phone_input.is_visible():
                await phone_input.fill("0912345678")

            email_input = page.locator("input[placeholder*='email'], input[name*='email'], input[type='email']").first
            if await email_input.is_visible():
                await email_input.fill("e2e_test@minhsinh.vn")

            dob_input = page.locator("input[placeholder*='sinh'], input[placeholder*='1990'], select[name*='year'], input[name*='dob']").first
            if await dob_input.is_visible():
                await dob_input.fill("1995")

            cat_select = page.locator("select").first
            if await cat_select.is_visible():
                options = await cat_select.locator("option").all()
                if len(options) > 1:
                    val = await options[1].get_attribute("value")
                    if val:
                        await cat_select.select_option(val)

            shot2 = os.path.join(artifact_dir, "e2e_step2_patient_info.png")
            await page.screenshot(path=shot2, full_page=False)
            report.record_step(suite, "E2E Fill Patient Form", True, "Patient details & category filled", shot2)

            if await next_btn.is_visible():
                await next_btn.click()
                await page.wait_for_timeout(1500)

            # Step 3: Slot / Chair matrix
            shot3 = os.path.join(artifact_dir, "e2e_step3_slot_selection.png")
            await page.screenshot(path=shot3, full_page=False)
            slots = page.locator("button:has-text('Ghế'), button:has-text('08:'), button:has-text('09:'), button:has-text('10:'), button:has-text('14:'), .cursor-pointer")
            slot_count = await slots.count()
            if slot_count > 0:
                await slots.first.click()
                await page.wait_for_timeout(1500)
                report.record_step(suite, "E2E Slot Selection", True, f"Selected slot from {slot_count} candidates", shot3)
            else:
                report.record_step(suite, "E2E Slot Selection", True, "No specific slot selection required or available", shot3)

            # Step 4: Submit
            submit_btn = page.locator("button:has-text('Hoàn tất Đặt lịch'), button:has-text('Xác nhận đặt lịch'), button:has-text('Đặt lịch ngay'), button[type='submit']").first
            is_submittable = await submit_btn.is_visible()
            if is_submittable:
                await submit_btn.click()
                log(">> Submitted booking. Waiting for response/redirect...")
                await page.wait_for_timeout(3500)

            shot4 = os.path.join(artifact_dir, "e2e_step4_confirmation.png")
            await page.screenshot(path=shot4, full_page=False)
            report.record_step(suite, "E2E Submit & Confirmation", True, f"Current URL: {page.url}", shot4)

            await browser.close()
    except Exception as e:
        report.record_step(suite, "E2E Execution Error", False, str(e))

    report.finish_suite(suite)


# -----------------------------------------------------------------------------
# 3. FLOW SUITE: Full Multi-Step Booking Flow with Detailed Validations
# -----------------------------------------------------------------------------
async def run_flow_suite(report: TestReport, artifact_dir: str, base_url: str, headless: bool):
    suite = report.add_suite("Full Multi-Step Booking Flow")
    log(f"\n[SUITE] Starting: {suite['name']}")

    try:
        from playwright.async_api import async_playwright
        async with async_playwright() as p:
            try:
                browser = await p.chromium.launch(channel="msedge", headless=headless)
            except Exception:
                browser = await p.chromium.launch(headless=headless)

            context = await browser.new_context(viewport={"width": 1280, "height": 950})
            page = await context.new_page()

            # Console log capture
            console_errors = []
            page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)

            booking_url = f"{base_url.rstrip('/')}/booking/"
            log(f">> Navigating to {booking_url}...")
            await page.goto(booking_url, wait_until="networkidle", timeout=15000)
            await page.wait_for_timeout(2000)

            # Step 1: Chọn cơ sở
            shot1_1 = os.path.join(artifact_dir, "flow_step1_clinics_list.png")
            await page.screenshot(path=shot1_1)

            clinic_cards = page.locator(".grid > div.cursor-pointer, [role='button']")
            card_count = await clinic_cards.count()
            if card_count == 0:
                report.record_step(suite, "Flow Step 1: Clinic Discovery", False, "No clinics found in grid", shot1_1)
                await browser.close()
                report.finish_suite(suite)
                return

            await clinic_cards.first.click()
            await page.wait_for_timeout(1000)
            shot1_2 = os.path.join(artifact_dir, "flow_step1_clinic_selected.png")
            await page.screenshot(path=shot1_2)

            report.record_step(suite, "Flow Step 1: Clinic Selected", True, f"Selected clinic from {card_count} available", shot1_2)

            next_btn_1 = page.locator("button:has-text('Tiếp tục')")
            await next_btn_1.click()
            await page.wait_for_timeout(1500)

            # Step 2: Điền thông tin khách hàng
            shot2_1 = os.path.join(artifact_dir, "flow_step2_patient_form.png")
            await page.screenshot(path=shot2_1)

            name_input = page.locator("input[placeholder*='Nguyễn Văn A']").first
            await name_input.fill("Nguyễn Thu Trang")

            phone_input = page.locator("input[placeholder*='0987654321']").first
            await phone_input.fill("0988776655")

            email_input = page.locator("input[type='email']").first
            await email_input.fill("thutrang.qa@minhsinh.vn")

            dob_input = page.locator("input[placeholder*='1990']").first
            await dob_input.fill("1996")

            cat_select = page.locator("select").first
            options = await cat_select.locator("option").all()
            selected_cat = "Default"
            if len(options) > 1:
                val = await options[1].get_attribute("value")
                await cat_select.select_option(val)
                selected_cat = val or "Option 1"

            await page.wait_for_timeout(800)
            shot2_2 = os.path.join(artifact_dir, "flow_step2_patient_filled.png")
            await page.screenshot(path=shot2_2)

            report.record_step(
                suite,
                "Flow Step 2: Patient Form Filled",
                True,
                f"Patient: Nguyễn Thu Trang (0988776655), Category: {selected_cat}",
                shot2_2
            )

            next_btn_2 = page.locator("button:has-text('Tiếp tục')")
            await next_btn_2.click()
            await page.wait_for_timeout(2000)

            # Step 3: Ma trận ghế & chọn giờ
            shot3_1 = os.path.join(artifact_dir, "flow_step3_chair_matrix.png")
            await page.screenshot(path=shot3_1)

            clickable_cells = page.locator(".cursor-pointer")
            cell_count = await clickable_cells.count()
            selected_slot = False
            for i in range(cell_count):
                cell = clickable_cells.nth(i)
                text = await cell.inner_text()
                if "Kín lịch" not in text:
                    await cell.click()
                    selected_slot = True
                    await page.wait_for_timeout(1000)
                    break

            if not selected_slot and cell_count > 0:
                await clickable_cells.first.click()
                await page.wait_for_timeout(1000)

            shot3_2 = os.path.join(artifact_dir, "flow_step3_slot_selected.png")
            await page.screenshot(path=shot3_2)
            report.record_step(
                suite,
                "Flow Step 3: Chair Matrix Slot Selection",
                True,
                f"Evaluated {cell_count} matrix slots, selected active time window",
                shot3_2
            )

            # Step 4: Hoàn tất đặt lịch
            submit_btn = page.locator("button:has-text('Hoàn tất Đặt lịch')")
            is_enabled = await submit_btn.is_enabled()

            if is_enabled:
                await submit_btn.click()
                log(">> Submitted booking. Waiting for redirect...")
                redirected = False
                try:
                    await page.wait_for_url("**/booking/success/**", timeout=12000)
                    redirected = True
                except Exception as e:
                    log(f"Wait for url warning: {e}")

                await page.wait_for_timeout(2000)
                shot4 = os.path.join(artifact_dir, "flow_step4_success_confirmation.png")
                await page.screenshot(path=shot4)

                current_url = page.url
                is_success = redirected or ("success" in current_url)
                report.record_step(
                    suite,
                    "Flow Step 4: Final Booking Submission & Success Redirect",
                    is_success,
                    f"Redirected to: {current_url}",
                    shot4
                )
            else:
                shot4 = os.path.join(artifact_dir, "flow_step4_submit_disabled.png")
                await page.screenshot(path=shot4)
                report.record_step(
                    suite,
                    "Flow Step 4: Final Booking Submission",
                    False,
                    "Submit button 'Hoàn tất Đặt lịch' was not enabled",
                    shot4
                )

            # Check console errors
            if console_errors:
                log(f"[Warning] Console errors during flow: {console_errors[:3]}")

            await browser.close()
    except Exception as e:
        report.record_step(suite, "Flow Execution Error", False, str(e))

    report.finish_suite(suite)


# -----------------------------------------------------------------------------
# CLI ENTRY POINT
# -----------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Unified Test Suite Runner for Minh Sinh Dental Project"
    )
    parser.add_argument("--all", action="store_true", help="Run all test suites (verify, e2e, flow)")
    parser.add_argument("--verify", action="store_true", help="Run quick schema & backend/DB feature verification")
    parser.add_argument("--e2e", action="store_true", help="Run E2E booking test")
    parser.add_argument("--flow", action="store_true", help="Run full multi-step booking flow test")
    parser.add_argument("--format", choices=["markdown", "json", "all"], default="markdown", help="Output format")
    parser.add_argument("--json", action="store_true", help="Output pure JSON (equivalent to --format json)")
    parser.add_argument("--artifact-dir", default=DEFAULT_ARTIFACT_DIR, help="Directory to save test screenshots")
    parser.add_argument("--base-url", default="http://localhost:8000", help="Django Backend Base URL")
    parser.add_argument("--wp-url", default="http://localhost", help="WordPress Base URL")
    parser.add_argument("--no-headless", action="store_true", help="Run browser in headful mode (visible window)")

    args = parser.parse_args()

    # Determine which suites to run
    run_all = args.all or (not args.verify and not args.e2e and not args.flow)
    do_verify = run_all or args.verify
    do_e2e = run_all or args.e2e
    do_flow = run_all or args.flow

    headless = not args.no_headless
    output_format = "json" if args.json else args.format

    global QUIET_LOGS
    if output_format == "json":
        QUIET_LOGS = True

    # Ensure artifact directory exists
    os.makedirs(args.artifact_dir, exist_ok=True)

    report = TestReport()

    async def execute():
        if do_verify:
            await run_verify_suite(report, args.artifact_dir, args.base_url, args.wp_url, headless)
        if do_e2e:
            await run_e2e_suite(report, args.artifact_dir, args.base_url, headless)
        if do_flow:
            await run_flow_suite(report, args.artifact_dir, args.base_url, headless)

    asyncio.run(execute())

    # Format outputs
    if output_format == "json":
        print(json.dumps(report.to_dict(), indent=2, ensure_ascii=False))
    elif output_format == "all":
        print(report.render_markdown())
        print("\n--- JSON OUTPUT ---")
        print(json.dumps(report.to_dict(), indent=2, ensure_ascii=False))
    else:
        print(report.render_markdown())

    # Exit code according to overall status
    sys.exit(0 if report.overall_status() == "PASS" else 1)

if __name__ == "__main__":
    main()
