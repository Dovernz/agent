import asyncio
import os
import sys
import subprocess
import json

sys.stdout.reconfigure(encoding='utf-8')
from playwright.async_api import async_playwright

ARTIFACT_DIR = r"C:\Users\thanhcaotien\.gemini\antigravity\brain\e836e051-9249-4417-b718-8bbc5e0435fb"

def get_django_session_for_user(username):
    cmd = [
        "docker", "exec", "dental_backend", "python", "manage.py", "shell", "-c",
        f"from django.contrib.sessions.backends.db import SessionStore; from django.contrib.auth.models import User; u = User.objects.filter(username='{username}').first(); s = SessionStore(); s['_auth_user_id'] = str(u.id); s['_auth_user_backend'] = 'django.contrib.auth.backends.ModelBackend'; s['_auth_user_hash'] = u.get_session_auth_hash(); s.save(); print('SESSION_KEY:' + s.session_key)"
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    for line in res.stdout.splitlines():
        if "SESSION_KEY:" in line:
            return line.split("SESSION_KEY:")[1].strip()
    return None

def grant_permission_to_user(username, perm_codename):
    cmd = [
        "docker", "exec", "dental_backend", "python", "manage.py", "shell", "-c",
        f"from django.contrib.auth.models import User, Permission; u = User.objects.get(username='{username}'); p = Permission.objects.get(codename='{perm_codename}'); u.user_permissions.add(p); print('GRANTED', p.codename, 'to', u.username)"
    ]
    subprocess.run(cmd, capture_output=True, text=True)

def revoke_permission_from_user(username, perm_codename):
    cmd = [
        "docker", "exec", "dental_backend", "python", "manage.py", "shell", "-c",
        f"from django.contrib.auth.models import User, Permission; u = User.objects.get(username='{username}'); p = Permission.objects.get(codename='{perm_codename}'); u.user_permissions.remove(p); print('REVOKED', p.codename, 'from', u.username)"
    ]
    subprocess.run(cmd, capture_output=True, text=True)

async def run_dynamic_permission_suite():
    print("==================================================================")
    print("=== [QA PROTOCOL] KIỂM THỬ PHÂN QUYỀN ĐỘNG LINH HOẠT CHO TỪNG USER ===")
    print("==================================================================")

    # Đảm bảo ban đầu bác sĩ 10000000 chưa có quyền bài viết
    revoke_permission_from_user("10000000", "manage_wordpress_posts")
    revoke_permission_from_user("10000000", "add_article")
    revoke_permission_from_user("10000000", "view_article")

    async with async_playwright() as p:
        browser = await p.chromium.launch(channel="msedge", headless=True)

        # -------------------------------------------------------------
        # STEP 1: BÁC SĨ CHƯA ĐƯỢC GRANT QUYỀN BÀI VIẾT
        # -------------------------------------------------------------
        print("\n>>> [1/3] KIỂM TRA BÁC SĨ (10000000) KHI CHƯA ĐƯỢC GRANT QUYỀN BÀI VIẾT...")
        doc_session = get_django_session_for_user("10000000")
        context_doc = await browser.new_context(viewport={"width": 1400, "height": 950})
        if doc_session:
            await context_doc.add_cookies([{
                "name": "sessionid",
                "value": doc_session,
                "domain": "localhost",
                "path": "/",
                "httpOnly": True,
                "sameSite": "Lax"
            }])

        page_doc = await context_doc.new_page()
        await page_doc.goto("http://localhost:8000/admin/", wait_until="domcontentloaded")
        await page_doc.wait_for_timeout(2000)

        shot1 = os.path.join(ARTIFACT_DIR, "proof_doctor_no_perm_hidden.png")
        await page_doc.screenshot(path=shot1)
        print(f"[Captured] {shot1}")

        # Kiểm tra nội dung thanh Sidebar
        nav_text_1 = await page_doc.locator("#nav-sidebar-apps").inner_text()
        has_wp_menu_1 = "Bài viết & Blog (WordPress)" in nav_text_1 or "Quản lý Bài viết" in nav_text_1
        print(f">> Has WordPress items on sidebar before grant: {has_wp_menu_1}")
        assert not has_wp_menu_1, "WordPress items should NOT appear before permission is granted!"

        # Thử cố tình vào link SSO
        res = await page_doc.goto("http://localhost:8000/admin/sso-to-wordpress/", wait_until="domcontentloaded")
        print(f">> SSO attempt status code before grant: {res.status}")
        shot1_denied = os.path.join(ARTIFACT_DIR, "proof_doctor_sso_denied.png")
        await page_doc.screenshot(path=shot1_denied)
        print(f"[Captured] {shot1_denied}")
        assert res.status == 403, f"Expected 403, got {res.status}"

        # -------------------------------------------------------------
        # STEP 2: ADMIN GRANT QUYỀN 'manage_wordpress_posts' CHO BÁC SĨ
        # -------------------------------------------------------------
        print("\n>>> [2/3] ADMIN GRANT QUYỀN 'manage_wordpress_posts' CHO BÁC SĨ 10000000...")
        grant_permission_to_user("10000000", "manage_wordpress_posts")

        # Reload lại trang Admin của Bác sĩ
        await page_doc.goto("http://localhost:8000/admin/", wait_until="domcontentloaded")
        await page_doc.wait_for_timeout(2500)

        shot2 = os.path.join(ARTIFACT_DIR, "proof_doctor_granted_perm_sidebar.png")
        await page_doc.screenshot(path=shot2)
        print(f"[Captured] {shot2}")

        nav_text_2 = await page_doc.locator("#nav-sidebar-apps").inner_text()
        has_wp_menu_2 = "Bài viết & Blog (WordPress)" in nav_text_2 or "Quản lý Bài viết" in nav_text_2
        print(f">> Has WordPress items on sidebar after grant: {has_wp_menu_2}")
        assert has_wp_menu_2, "WordPress items MUST appear on sidebar after permission is granted!"

        # Bác sĩ bấm vào link SSO Viết Bài Mới
        print(">> Doctor accessing WordPress via SSO: /admin/sso-to-wordpress/?target=post-new.php ...")
        await page_doc.goto("http://localhost:8000/admin/sso-to-wordpress/?target=post-new.php", wait_until="domcontentloaded")
        await page_doc.wait_for_timeout(4000)

        current_url_doc = page_doc.url
        print(f">> Doctor URL after SSO: {current_url_doc}")
        shot2_sso = os.path.join(ARTIFACT_DIR, "proof_doctor_sso_wordpress_success.png")
        await page_doc.screenshot(path=shot2_sso, full_page=True)
        print(f"[Captured] {shot2_sso}")
        assert "post-new.php" in current_url_doc or "wp-admin" in current_url_doc, f"Expected wp-admin, got {current_url_doc}"

        # -------------------------------------------------------------
        # STEP 3: THU HỒI QUYỀN (REVOKE PERMISSION)
        # -------------------------------------------------------------
        print("\n>>> [3/3] ADMIN THU HỒI QUYỀN (REVOKE) CỦA BÁC SĨ 10000000...")
        revoke_permission_from_user("10000000", "manage_wordpress_posts")

        # Reload lại trang Admin của Bác sĩ
        await page_doc.goto("http://localhost:8000/admin/", wait_until="domcontentloaded")
        await page_doc.wait_for_timeout(2000)

        shot3 = os.path.join(ARTIFACT_DIR, "proof_doctor_revoked_perm_sidebar.png")
        await page_doc.screenshot(path=shot3)
        print(f"[Captured] {shot3}")

        nav_text_3 = await page_doc.locator("#nav-sidebar-apps").inner_text()
        has_wp_menu_3 = "Bài viết & Blog (WordPress)" in nav_text_3 or "Quản lý Bài viết" in nav_text_3
        print(f">> Has WordPress items on sidebar after revoke: {has_wp_menu_3}")
        assert not has_wp_menu_3, "WordPress items MUST disappear after permission is revoked!"

        print("\n==================================================================")
        print("=== [QA PROTOCOL] HOÀN TẤT 100% TEST PHÂN QUYỀN ĐỘNG LINH HOẠT ===")
        print("==================================================================")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_dynamic_permission_suite())
