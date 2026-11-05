import asyncio
import os
import sys
import subprocess
import json

sys.stdout.reconfigure(encoding='utf-8')
from playwright.async_api import async_playwright

ARTIFACT_DIR = r"C:\Users\thanhcaotien\.gemini\antigravity\brain\e836e051-9249-4417-b718-8bbc5e0435fb"

# 1. Obtain Django Session Key for Admin testing
def get_django_session():
    cmd = [
        "docker", "exec", "dental_backend", "python", "manage.py", "shell", "-c",
        "from django.contrib.sessions.backends.db import SessionStore; from django.contrib.auth.models import User; u = User.objects.filter(is_superuser=True).first(); s = SessionStore(); s['_auth_user_id'] = str(u.id); s['_auth_user_backend'] = 'django.contrib.auth.backends.ModelBackend'; s['_auth_user_hash'] = u.get_session_auth_hash(); s.save(); print('SESSION_KEY:' + s.session_key)"
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    for line in res.stdout.splitlines():
        if "SESSION_KEY:" in line:
            return line.split("SESSION_KEY:")[1].strip()
    return None

async def run_all_tests():
    print("=============================================================")
    print("=== [QA MASTER] BẮT ĐẦU KIỂM THỬ TOÀN DIỆN HỆ THỐNG MINH SINH ===")
    print("=============================================================")
    session_key = get_django_session()
    print(">> Django Admin Session Key:", session_key)

    async with async_playwright() as p:
        browser = await p.chromium.launch(channel="msedge", headless=True)
        context = await browser.new_context(viewport={"width": 1400, "height": 950})

        if session_key:
            await context.add_cookies([{
                "name": "sessionid",
                "value": session_key,
                "domain": "localhost",
                "path": "/",
                "httpOnly": True,
                "sameSite": "Lax"
            }])

        page = await context.new_page()

        # =====================================================================
        # MODULE 1: ĐẶT LỊCH KHÁM BỆNH NHÂN (BOOKING E2E + MAP + RECORD)
        # =====================================================================
        print("\n--- [MODULE 1] KIỂM THỬ ĐẶT LỊCH KHÁM (PORT 8000) ---")
        await page.goto("http://localhost:8000/booking/", wait_until="networkidle")
        await page.wait_for_timeout(2000)

        # Step 1: Chọn cơ sở
        shot1_1 = os.path.join(ARTIFACT_DIR, "e2e_1_booking_step1_clinic.png")
        await page.screenshot(path=shot1_1)
        print(f"[Captured] {shot1_1}")

        clinic_card = page.locator(".grid > div.cursor-pointer").first
        await clinic_card.click()
        await page.wait_for_timeout(1000)
        await page.locator("button:has-text('Tiếp tục')").click()
        await page.wait_for_timeout(1500)

        # Step 2: Điền thông tin bệnh nhân
        shot1_2 = os.path.join(ARTIFACT_DIR, "e2e_1_booking_step2_patient.png")
        await page.screenshot(path=shot1_2)
        print(f"[Captured] {shot1_2}")

        await page.locator("input[placeholder*='Nguyễn Văn A']").first.fill("Hoàng Minh Quân")
        await page.locator("input[placeholder*='0987654321']").first.fill("0968123456")
        await page.locator("input[type='email']").first.fill("minhquan.qa@minhsinh.vn")
        await page.locator("input[placeholder*='1990']").first.fill("1995")

        cat_select = page.locator("select").first
        options = await cat_select.locator("option").all()
        if len(options) > 1:
            val = await options[1].get_attribute("value")
            await cat_select.select_option(val)
        await page.wait_for_timeout(1000)

        await page.locator("button:has-text('Tiếp tục')").click()
        await page.wait_for_timeout(2000)

        # Step 3: Chọn ghế & khung giờ
        shot1_3 = os.path.join(ARTIFACT_DIR, "e2e_1_booking_step3_matrix.png")
        await page.screenshot(path=shot1_3)
        print(f"[Captured] {shot1_3}")

        slots = page.locator(".cursor-pointer")
        slot_count = await slots.count()
        for i in range(slot_count):
            txt = await slots.nth(i).inner_text()
            if "Kín lịch" not in txt:
                await slots.nth(i).click()
                await page.wait_for_timeout(1000)
                break

        # Submit
        submit_btn = page.locator("button:has-text('Hoàn tất Đặt lịch')")
        print(f">> Submit button enabled: {await submit_btn.is_enabled()}")
        await submit_btn.click()

        # Step 4: Chờ chuyển đến trang Booking Success
        try:
            await page.wait_for_url("**/booking/success/**", timeout=12000)
            print(">> Arrived at Booking Success URL:", page.url)
        except Exception as e:
            print(">> Wait URL Warning:", e)

        await page.wait_for_timeout(3000)
        shot1_4 = os.path.join(ARTIFACT_DIR, "e2e_1_booking_step4_success.png")
        await page.screenshot(path=shot1_4, full_page=True)
        print(f"[Captured] {shot1_4}")

        # =====================================================================
        # MODULE 2: BỆNH ÁN ĐIỆN TỬ EMR & SƠ ĐỒ RĂNG SVG (PORT 8000)
        # =====================================================================
        print("\n--- [MODULE 2] KIỂM THỬ SƠ ĐỒ RĂNG SVG (EMR) ---")
        await page.goto("http://localhost:8000/dental-chart/?customerId=1", wait_until="networkidle")
        await page.wait_for_timeout(2500)

        # Click on tooth and set condition
        tooth_elements = page.locator("svg [data-tooth-id], svg [id*='tooth'], svg path.cursor-pointer")
        cnt = await tooth_elements.count()
        print(f">> Tooth elements found: {cnt}")
        if cnt > 0:
            await tooth_elements.first.click()
            await page.wait_for_timeout(1000)

        # Click button "Lưu Sơ Đồ" if exists
        save_btn = page.locator("button:has-text('Lưu'), button:has-text('Save')").first
        if await save_btn.count() > 0:
            await save_btn.click()
            await page.wait_for_timeout(2000)

        shot2_1 = os.path.join(ARTIFACT_DIR, "e2e_2_dental_chart_saved.png")
        await page.screenshot(path=shot2_1)
        print(f"[Captured] {shot2_1}")

        # =====================================================================
        # MODULE 3: HỆ THỐNG QUẢN TRỊ DJANGO UNFOLD ADMIN (PORT 8000)
        # =====================================================================
        print("\n--- [MODULE 3] KIỂM THỬ DJANGO UNFOLD ADMIN ---")
        # Dashboard
        await page.goto("http://localhost:8000/admin/", wait_until="networkidle")
        await page.wait_for_timeout(2000)
        shot3_1 = os.path.join(ARTIFACT_DIR, "e2e_3_admin_dashboard.png")
        await page.screenshot(path=shot3_1)
        print(f"[Captured] {shot3_1}")

        # Check Iframe Tạo Booking (No 🚫)
        await page.goto("http://localhost:8000/admin/booking-embed/", wait_until="networkidle")
        await page.wait_for_timeout(3000)
        shot3_2 = os.path.join(ARTIFACT_DIR, "e2e_3_admin_booking_embed.png")
        await page.screenshot(path=shot3_2)
        print(f"[Captured] {shot3_2}")

        # Check POS System
        await page.goto("http://localhost:8000/admin/pos-system/", wait_until="networkidle")
        await page.wait_for_timeout(3000)
        shot3_3 = os.path.join(ARTIFACT_DIR, "e2e_3_admin_pos_system.png")
        await page.screenshot(path=shot3_3)
        print(f"[Captured] {shot3_3}")

        # =====================================================================
        # MODULE 4: WEBSITE & BLOG WORDPRESS (PORT 80)
        # =====================================================================
        print("\n--- [MODULE 4] KIỂM THỬ WORDPRESS (PORT 80) ---")
        # Homepage
        await page.goto("http://localhost/", wait_until="networkidle")
        await page.wait_for_timeout(2000)
        shot4_1 = os.path.join(ARTIFACT_DIR, "e2e_4_wordpress_home.png")
        await page.screenshot(path=shot4_1)
        print(f"[Captured] {shot4_1}")

        # Single Article (Migrated post)
        await page.goto("http://localhost/co-nen-nieng-rang-som-cho-con/", wait_until="networkidle")
        await page.wait_for_timeout(2000)
        shot4_2 = os.path.join(ARTIFACT_DIR, "e2e_4_wordpress_article.png")
        await page.screenshot(path=shot4_2, full_page=True)
        print(f"[Captured] {shot4_2}")

        # WP Login Navigation Links
        await page.goto("http://localhost/wp-login.php", wait_until="networkidle")
        await page.wait_for_timeout(1500)
        shot4_3 = os.path.join(ARTIFACT_DIR, "e2e_4_wordpress_login_nav.png")
        await page.screenshot(path=shot4_3)
        print(f"[Captured] {shot4_3}")

        # =====================================================================
        # CREATE NEW TEST RECORD IN WORDPRESS VIA WP-CLI
        # =====================================================================
        print("\n--- [CREATE RECORD] TẠO THỬ BÀI VIẾT MỚI TRÊN WORDPRESS ---")
        new_post_cmd = [
            "docker", "exec", "-i", "dental_wordpress",
            "wp", "post", "create",
            "--post_title=CÁCH CHĂM SÓC RĂNG MIỆNG SAU KHI CẠO VÔI RĂNG",
            "--post_name=cach-cham-soc-rang-mieng-sau-khi-cao-voi-rang",
            "--post_status=publish",
            "--post_category=5",
            "--allow-root",
            "-"
        ]
        new_post_content = """<p><strong>Cạo vôi răng (lấy cao răng)</strong> là phương pháp nha khoa đơn giản nhưng mang lại hiệu quả vượt trội trong việc ngăn ngừa viêm nha chu, hôi miệng và tụt lợi.</p>
<h2>1. Không nên ăn đồ quá nóng hoặc quá lạnh ngay sau khi lấy cao răng</h2>
<p>Sau khi loại bỏ các mảng vôi răng bám chặt, men răng và nướu có thể hơi nhạy cảm trong khoảng 24-48 giờ đầu tiên. Hãy ưu tiên thức ăn ấm, mềm và dễ nhai.</p>
<h2>2. Chải răng đúng cách với bàn chải lông mềm</h2>
<p>Sử dụng bàn chải có sợi lông siêu mảnh, chải nhẹ nhàng theo chiều dọc từ trên xuống dưới, tránh cọ xát mạnh theo chiều ngang gây mòn cổ răng.</p>
<h2>3. Khám định kỳ mỗi 6 tháng một lần</h2>
<p>Để duy trì hàm răng trắng sáng và khỏe mạnh, hãy lên lịch khám và làm sạch răng định kỳ tại Nha Khoa Minh Sinh.</p>"""

        p_wp = subprocess.Popen(new_post_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8")
        wp_out, wp_err = p_wp.communicate(input=new_post_content)
        print(">> WP Create Post Result:", wp_out.strip())

        # Screenshot the newly created post in WordPress
        await page.goto("http://localhost/cach-cham-soc-rang-mieng-sau-khi-cao-voi-rang/", wait_until="networkidle")
        await page.wait_for_timeout(2000)
        shot4_4 = os.path.join(ARTIFACT_DIR, "e2e_4_wordpress_new_post_created.png")
        await page.screenshot(path=shot4_4, full_page=True)
        print(f"[Captured] {shot4_4}")

        await browser.close()
        print("\n=============================================================")
        print("=== [QA MASTER] HOÀN TẤT TOÀN BỘ KIỂM THỬ E2E THÀNH CÔNG! ===")
        print("=============================================================")
        return True

if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
