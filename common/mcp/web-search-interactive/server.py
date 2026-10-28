#!/usr/bin/env python3
"""
Dual-Engine Web Search & Interactive Browser MCP Server for Antigravity
Provides both:
1. Fast-Path (HTTP): Lightweight real-time search, HTML parsing, text/price extraction.
2. Interactive-Path (Playwright/Chrome): Live browser automation, DOM form inspection, input filling, clicking, and screenshots.
"""

import sys
import os
import json
import re
import urllib.request
import urllib.parse
from html.parser import HTMLParser

# Ensure UTF-8 standard IO
if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
if sys.stdin.encoding.lower() != 'utf-8':
    try:
        sys.stdin.reconfigure(encoding='utf-8')
    except Exception:
        pass

SERVER_NAME = "web-search-interactive-mcp"
SERVER_VERSION = "2.0.0"

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"

# ==================== ENGINE 1: FAST-PATH (HTTP / SCRAPING) ====================

class HTMLTextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.result = []
        self.links = []
        self.title = ""
        self.in_title = False
        self.skip_tags = {'script', 'style', 'noscript', 'svg', 'iframe'}
        self.current_skip = 0
        self.current_href = None
        self.current_link_text = []

    def handle_starttag(self, tag, attrs):
        tag_lower = tag.lower()
        if tag_lower in self.skip_tags:
            self.current_skip += 1
        elif tag_lower == 'title':
            self.in_title = True
        elif tag_lower == 'a':
            for name, val in attrs:
                if name.lower() == 'href' and val:
                    self.current_href = val
                    self.current_link_text = []
        elif tag_lower in {'p', 'div', 'br', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'tr'}:
            self.result.append("\n")

    def handle_endtag(self, tag):
        tag_lower = tag.lower()
        if tag_lower in self.skip_tags:
            if self.current_skip > 0:
                self.current_skip -= 1
        elif tag_lower == 'title':
            self.in_title = False
        elif tag_lower == 'a':
            if self.current_href and self.current_link_text:
                text = " ".join("".join(self.current_link_text).split())
                if text and len(text) > 2 and not text.startswith("http"):
                    self.links.append({"text": text, "url": self.current_href})
            self.current_href = None
            self.current_link_text = []

    def handle_data(self, data):
        if self.current_skip == 0:
            if self.in_title:
                self.title += data
            else:
                self.result.append(data)
                if self.current_href:
                    self.current_link_text.append(data)

    def get_text(self):
        raw = "".join(self.result)
        lines = [re.sub(r'[ \t]+', ' ', line).strip() for line in raw.split("\n")]
        filtered = []
        blank = False
        for line in lines:
            if line:
                filtered.append(line)
                blank = False
            elif not blank:
                filtered.append("")
                blank = True
        return "\n".join(filtered).strip()

def search_duckduckgo(query: str, max_results: int = 6):
    url = 'https://lite.duckduckgo.com/lite/'
    data = urllib.parse.urlencode({'q': query}).encode()
    req = urllib.request.Request(
        url,
        data=data,
        headers={"User-Agent": USER_AGENT, "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7"}
    )
    results = []
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            links = re.findall(r'<a[^>]+href="([^"]+)"[^>]+class=[\'\"]result-link[\'\"][^>]*>(.*?)</a>', html)
            snippets = re.findall(r'class=[\'\"]result-snippet[\'\"]>\s*(.*?)\s*</td>', html, re.DOTALL)
            
            for i in range(min(len(links), max_results)):
                raw_url = links[i][0]
                actual_url = raw_url
                if "uddg=" in raw_url:
                    u_match = re.search(r'uddg=([^&]+)', raw_url)
                    if u_match:
                        actual_url = urllib.parse.unquote(u_match.group(1))
                        
                title = re.sub(r'<[^>]+>', '', links[i][1]).strip()
                snippet = re.sub(r'<[^>]+>', '', snippets[i]).strip() if i < len(snippets) else ""
                
                results.append({
                    "title": title,
                    "url": actual_url,
                    "snippet": snippet
                })
    except Exception as e:
        results.append({
            "title": f"Lỗi tìm kiếm: {str(e)}",
            "url": f"https://www.google.com/search?q={urllib.parse.quote_plus(query)}",
            "snippet": f"Tìm kiếm dự phòng cho: {query}"
        })
    return results

def fetch_url(url: str, max_chars: int = 6000):
    req = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT, "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7"}
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            content_type = resp.headers.get('Content-Type', '')
            charset = 'utf-8'
            if 'charset=' in content_type:
                charset = content_type.split('charset=')[-1].split(';')[0].strip()
            raw_bytes = resp.read()
            html_text = raw_bytes.decode(charset, errors='ignore')
            
            parser = HTMLTextExtractor()
            parser.feed(html_text)
            text = parser.get_text()
            
            price_regex = re.compile(r'(\b\d{1,3}(?:[.,]\d{3})+\s*(?:₫|đ|vnđ|vnd|đồng|\$))\b', re.IGNORECASE)
            detected_prices = list(dict.fromkeys(price_regex.findall(text)))[:10]
            
            truncated_text = text[:max_chars]
            if len(text) > max_chars:
                truncated_text += f"\n\n[...Đã cắt bớt nội dung. Tổng độ dài: {len(text)} ký tự...]"
                
            return {
                "status": resp.status,
                "url": url,
                "title": parser.title.strip(),
                "detected_prices": detected_prices,
                "relevant_links": parser.links[:15],
                "content": truncated_text
            }
    except Exception as e:
        return {
            "status": "ERROR",
            "url": url,
            "error": str(e)
        }

# ==================== ENGINE 2: INTERACTIVE BROWSER (PLAYWRIGHT) ====================

_browser_session = {
    "playwright": None,
    "browser": None,
    "page": None,
    "active_url": None
}

def get_playwright_installed():
    try:
        import playwright
        return True
    except ImportError:
        return False

def init_browser_page(headless: bool = True):
    global _browser_session
    if not get_playwright_installed():
        return False, "Playwright chưa được cài đặt. Để kích hoạt tính năng tương tác trình duyệt thực tế, vui lòng cài đặt: 'uv pip install playwright' hoặc 'pip install playwright' và 'playwright install chromium'."
    
    from playwright.sync_api import sync_playwright
    if _browser_session["page"] is None:
        pw = sync_playwright().start()
        # Prefer system Google Chrome if available, otherwise chromium
        chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        launch_kwargs = {"headless": headless}
        if os.path.exists(chrome_path):
            launch_kwargs["executable_path"] = chrome_path
            
        browser = pw.chromium.launch(**launch_kwargs)
        page = browser.new_page(user_agent=USER_AGENT)
        _browser_session["playwright"] = pw
        _browser_session["browser"] = browser
        _browser_session["page"] = page
    return True, _browser_session["page"]

def browser_navigate(url: str, headless: bool = True):
    ok, page_or_err = init_browser_page(headless=headless)
    if not ok:
        return {"status": "FAIL", "message": page_or_err}
    page = page_or_err
    try:
        resp = page.goto(url, wait_until="domcontentloaded", timeout=30000)
        _browser_session["active_url"] = url
        return {
            "status": "SUCCESS",
            "url": url,
            "title": page.title(),
            "http_status": resp.status if resp else None
        }
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}

def browser_inspect_form():
    page = _browser_session.get("page")
    if not page:
        return {"status": "FAIL", "message": "Chưa có trang web nào được mở bằng browser_navigate."}
    
    try:
        # Extract all input fields, buttons, and form tags for agent awareness
        form_data = page.evaluate("""() => {
            const inputs = Array.from(document.querySelectorAll('input, select, textarea')).map(el => ({
                tag: el.tagName.toLowerCase(),
                type: el.type || '',
                id: el.id || '',
                name: el.name || '',
                placeholder: el.placeholder || '',
                ariaLabel: el.getAttribute('aria-label') || '',
                isVisible: el.offsetParent !== null,
                currentValue: el.value || ''
            }));
            const buttons = Array.from(document.querySelectorAll('button, input[type="submit"], a.btn, a.button')).map(el => ({
                text: el.innerText.trim(),
                id: el.id || '',
                type: el.type || '',
                isVisible: el.offsetParent !== null
            }));
            return { inputs: inputs.filter(i => i.isVisible), buttons: buttons.filter(b => b.isVisible) };
        }""")
        return {
            "status": "SUCCESS",
            "url": page.url,
            "title": page.title(),
            "form_fields": form_data["inputs"],
            "action_buttons": form_data["buttons"]
        }
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}

def browser_fill_form(fields: list):
    page = _browser_session.get("page")
    if not page:
        return {"status": "FAIL", "message": "Chưa có trang web nào được mở bằng browser_navigate."}
    
    filled_results = []
    try:
        for field in fields:
            selector = field.get("selector")
            value = str(field.get("value", ""))
            if selector:
                page.wait_for_selector(selector, timeout=5000)
                page.fill(selector, value)
                filled_results.append({"selector": selector, "status": "FILLED"})
        return {"status": "SUCCESS", "filled_count": len(filled_results), "details": filled_results}
    except Exception as e:
        return {"status": "ERROR", "message": str(e), "filled_so_far": filled_results}

def browser_click_element(selector: str):
    page = _browser_session.get("page")
    if not page:
        return {"status": "FAIL", "message": "Chưa có trang web nào được mở bằng browser_navigate."}
    
    try:
        page.wait_for_selector(selector, timeout=5000)
        page.click(selector)
        page.wait_for_load_state("domcontentloaded", timeout=10000)
        return {
            "status": "SUCCESS",
            "clicked": selector,
            "new_url": page.url,
            "title": page.title()
        }
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}

def browser_take_screenshot(output_path: str = None):
    page = _browser_session.get("page")
    if not page:
        return {"status": "FAIL", "message": "Chưa có trang web nào được mở bằng browser_navigate."}
    
    if not output_path:
        output_path = os.path.join(os.getcwd(), "browser_screenshot.png")
    try:
        page.screenshot(path=output_path, full_page=False)
        return {"status": "SUCCESS", "saved_to": output_path}
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}

# ==================== MCP PROTOCOL INTERFACE ====================

TOOLS = [
    # Fast HTTP Tools
    {
        "name": "web_search",
        "description": "[Fast-Path HTTP] Performs real-time web search across search engines, returning page titles, direct URLs, and snippets.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query terms"},
                "num_results": {"type": "integer", "description": "Number of results (default 5)", "default": 5}
            },
            "required": ["query"]
        }
    },
    {
        "name": "fetch_web_page",
        "description": "[Fast-Path HTTP] Fetches webpage HTML, strips tags, returns clean readable text, page title, detected prices, and key links.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "Target website URL"},
                "max_chars": {"type": "integer", "description": "Max text characters to return", "default": 5000}
            },
            "required": ["url"]
        }
    },
    {
        "name": "extract_pricing_and_products",
        "description": "[Fast-Path HTTP] Extracts product pricing and specifications from a given webpage.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "Product or catalog URL"}
            },
            "required": ["url"]
        }
    },
    # Interactive Browser Tools
    {
        "name": "browser_navigate",
        "description": "[Interactive Browser] Launches Chrome/Chromium and navigates to a URL. Supports JavaScript execution and SPA pages.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "URL to open in the interactive browser"},
                "headless": {"type": "boolean", "description": "Run in headless mode (default: true). Set false to show browser UI for user interaction/captcha", "default": True}
            },
            "required": ["url"]
        }
    },
    {
        "name": "browser_inspect_form",
        "description": "[Interactive Browser] Inspects all interactive elements (input, select, textarea, button) on the active page to discover form fields.",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "browser_fill_form",
        "description": "[Interactive Browser] Fills one or multiple form input fields using CSS selectors.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "fields": {
                    "type": "array",
                    "description": "List of {selector, value} objects to fill into the active page",
                    "items": {
                        "type": "object",
                        "properties": {
                            "selector": {"type": "string", "description": "CSS selector, e.g. '#email', 'input[name=\"password\"]'"},
                            "value": {"type": "string", "description": "Value to type"}
                        },
                        "required": ["selector", "value"]
                    }
                }
            },
            "required": ["fields"]
        }
    },
    {
        "name": "browser_click",
        "description": "[Interactive Browser] Clicks a button, link, or element by CSS selector on the active page.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "selector": {"type": "string", "description": "CSS selector to click, e.g. 'button[type=\"submit\"]', '#btn-register'"}
            },
            "required": ["selector"]
        }
    },
    {
        "name": "browser_screenshot",
        "description": "[Interactive Browser] Captures a screenshot of the current page to inspect visual state or verify form completion.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "output_path": {"type": "string", "description": "Absolute path to save PNG screenshot (optional)"}
            }
        }
    }
]

def handle_request(req):
    req_id = req.get("id")
    method = req.get("method")
    params = req.get("params", {})

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION}
            }
        }
    elif method == "notifications/initialized":
        return None
    elif method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {"tools": TOOLS}
        }
    elif method == "tools/call":
        tool_name = params.get("name")
        args = params.get("arguments", {})
        try:
            # Fast-path tools
            if tool_name == "web_search":
                res = search_duckduckgo(args.get("query", ""), min(args.get("num_results", 5), 10))
                text_out = json.dumps({"query": args.get("query", ""), "results": res}, ensure_ascii=False, indent=2)
            elif tool_name == "fetch_web_page":
                res = fetch_url(args.get("url", ""), args.get("max_chars", 5000))
                text_out = json.dumps(res, ensure_ascii=False, indent=2)
            elif tool_name == "extract_pricing_and_products":
                res = fetch_url(args.get("url", ""), 4000)
                extracted = {
                    "url": args.get("url", ""),
                    "title": res.get("title", ""),
                    "detected_prices": res.get("detected_prices", []),
                    "relevant_links": res.get("relevant_links", [])[:10]
                }
                text_out = json.dumps(extracted, ensure_ascii=False, indent=2)
            # Interactive browser tools
            elif tool_name == "browser_navigate":
                res = browser_navigate(args.get("url", ""), args.get("headless", True))
                text_out = json.dumps(res, ensure_ascii=False, indent=2)
            elif tool_name == "browser_inspect_form":
                res = browser_inspect_form()
                text_out = json.dumps(res, ensure_ascii=False, indent=2)
            elif tool_name == "browser_fill_form":
                res = browser_fill_form(args.get("fields", []))
                text_out = json.dumps(res, ensure_ascii=False, indent=2)
            elif tool_name == "browser_click":
                res = browser_click_element(args.get("selector", ""))
                text_out = json.dumps(res, ensure_ascii=False, indent=2)
            elif tool_name == "browser_screenshot":
                res = browser_take_screenshot(args.get("output_path"))
                text_out = json.dumps(res, ensure_ascii=False, indent=2)
            else:
                text_out = f"Tool '{tool_name}' không tồn tại."
                
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"content": [{"type": "text", "text": text_out}]}
            }
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32603, "message": str(e)}
            }
    else:
        if req_id is not None:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32601, "message": f"Method {method} not found"}
            }
        return None

def run_server():
    while True:
        line = sys.stdin.readline()
        if not line:
            break
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except Exception:
            continue
        resp = handle_request(req)
        if resp:
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()

if __name__ == "__main__":
    run_server()
