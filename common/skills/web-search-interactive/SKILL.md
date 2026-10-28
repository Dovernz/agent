---
name: web-search-interactive
description: >-
  Universal dual-mode web search, content scraping, and browser automation skill.
  Supports both fast HTTP data extraction and live interactive browser operations
  (form inspection, input typing, clicking, and screenshots).
---

# Universal Web Search & Interactive Browser Automation Skill

Kỹ năng toàn cục giúp Agent thực hiện cả 2 luồng:
1. **Tìm kiếm & Thu thập thông tin nhanh (Fast-Path HTTP)**: Tra cứu tin tức, tài liệu kỹ thuật, so sánh giá thương mại điện tử.
2. **Tương tác trình duyệt thực tế (Interactive Browser Automation)**: Khởi chạy trình duyệt thật, quét form, điền thông tin đăng ký/đăng nhập, click nút và chụp ảnh màn hình xác nhận.

---

## 1. Quy Trình Quyết Định Chế Độ (Decision Tree)

```
                       [Yêu cầu Web của User]
                                  │
         ┌────────────────────────┴────────────────────────┐
         ▼                                                 ▼
[Chỉ cần đọc thông tin]                         [Cần thao tác trên trang]
(Tìm kiếm, cào text, đọc giá)                  (Đăng ký tài khoản, bấm nút, điền form)
         │                                                 │
         ▼                                                 ▼
  [Fast-Path HTTP]                              [Interactive Browser Path]
  - web_search(...)                             - browser_navigate(url, headless=False/True)
  - fetch_web_page(...)                         - browser_inspect_form() -> Tìm trường input
  - extract_pricing_and_products(...)           - browser_fill_form([{selector, value}, ...])
                                                - browser_click(selector="button[type=submit]")
                                                - browser_screenshot(output_path="...")
```

---

## 2. Hướng Dẫn Tương Tác Form / Đăng Ký Tài Khoản

Khi người dùng yêu cầu đăng ký hoặc thao tác trên form:
1. **Mở trang**: Gọi `browser_navigate(url="https://example.com/register", headless=True)`.
2. **Khảo sát form**: Gọi `browser_inspect_form()`. Kết quả sẽ trả về danh sách các trường `input` (id, name, type, placeholder).
3. **Điền thông tin**: Gọi `browser_fill_form(fields=[{"selector": "#email", "value": "user@domain.com"}, ...])`.
4. **Bấm gửi**: Gọi `browser_click(selector="button[type='submit']")`.
5. **Chụp ảnh kết quả**: Gọi `browser_screenshot()` để xác nhận trạng thái thành công hoặc báo lỗi.

> [!WARNING]
> Nếu trang web có **CAPTCHA** hoặc **Mã xác thực SMS/Email (OTP)**:
> 1. Thiết lập `headless=False` khi gọi `browser_navigate` để hiển thị cửa sổ Chrome.
> 2. Điền sẵn các trường thông tin cơ bản.
> 3. Thông báo cho người dùng hỗ trợ giải CAPTCHA hoặc nhập mã OTP trên màn hình.
