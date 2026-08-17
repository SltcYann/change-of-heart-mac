import threading, time, sys
from http.server import HTTPServer
sys.path.insert(0, r'E:/ai-workspace/knowledge-base/projects/p5r-save-editor')
from server import P5RWebHandler
from playwright.sync_api import sync_playwright

httpd = HTTPServer(('127.0.0.1', 8099), P5RWebHandler)
t = threading.Thread(target=httpd.serve_forever, daemon=True)
t.start()
time.sleep(1)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width': 1400, 'height': 900})
    page.goto('http://127.0.0.1:8099')
    page.wait_for_timeout(1000)
    page.click('text=HIDEOUT & INVENTORY')
    page.wait_for_timeout(1000)
    rows = page.locator('#unifiedItemListContainer > div').count()
    print('Rendered item rows:', rows)
    first_item = page.locator('#unifiedItemListContainer > div').first.inner_text() if rows > 0 else 'None'
    print('First item row text:\n', first_item)
    screenshot_path = r'C:/Users/kufis/.gemini/antigravity/brain/990d0212-226f-47f6-b6e6-12fbb696343e/item_studio_visual_test.png'
    page.screenshot(path=screenshot_path)
    print('Screenshot saved to:', screenshot_path)
    browser.close()
httpd.shutdown()
