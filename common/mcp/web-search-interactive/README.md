# Dual-Engine Web Search & Interactive Browser MCP

Máy chủ MCP cung cấp 2 chế độ (Dual-Engine) cho AI Agent:
1. **Fast-Path (HTTP)**: Tìm kiếm siêu tốc, đọc nội dung và bóc tách giá (0 dependency, siêu nhẹ).
2. **Interactive-Path (Playwright/Chrome)**: Duyệt web tương tác, quét form HTML, tự động điền form, click nút và chụp ảnh màn hình.

---

## 1. Danh Sách Công Cụ (Tools)

| Tool | Chế Độ | Chức Năng |
| :--- | :---: | :--- |
| `web_search` | HTTP | Tìm kiếm web realtime (DuckDuckGo/Google), trả về tiêu đề, URL và trích đoạn. |
| `fetch_web_page` | HTTP | Tải trang web, làm sạch mã rác, bóc tách văn bản, giá tiền (VNĐ/USD) và links. |
| `extract_pricing_and_products` | HTTP | Bóc tách giá và sản phẩm thương mại điện tử. |
| `browser_navigate` | Interactive | Mở URL trên trình duyệt Chromium/Chrome thật, hỗ trợ JavaScript và SPA. |
| `browser_inspect_form` | Interactive | Quét toàn bộ các trường nhập liệu (`input`, `select`, `button`) trên trang. |
| `browser_fill_form` | Interactive | Điền dữ liệu vào các ô input theo CSS selector. |
| `browser_click` | Interactive | Click nút bấm, link hoặc thẻ submit. |
| `browser_screenshot` | Interactive | Chụp ảnh màn hình lưu lại để đối soát trạng thái giao diện. |

---

## 2. Cách Cấu Hình & Chạy

Khai báo trong `~/.gemini/config/mcp_config.json`:

```json
{
  "mcpServers": {
    "web-search-interactive": {
      "command": "C:\\Users\\thanhcaotien\\.local\\bin\\python3.14.exe",
      "args": [
        "C:\\Users\\thanhcaotien\\.gemini\\config\\mcp-servers\\web-search-mcp\\server.py"
      ]
    }
  }
}
```

> **Kích hoạt tính năng Interactive**: Chạy lệnh `uv pip install playwright` hoặc `pip install playwright` và `playwright install chromium`. Nếu chưa cài, server vẫn hoạt động bình thường ở chế độ Fast-Path HTTP và thông báo gợi ý khi gọi tool tương tác.
