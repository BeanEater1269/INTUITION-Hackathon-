import json
import asyncio
from playwright.async_api import async_playwright
from pywinauto import Desktop

async def scan_header_chrome():
    print("\n[!] Scanning Chrome Header via OS hooks...")
    try:
        windows = Desktop(backend="uia").windows()
        chrome = next((w for w in windows if "Google Chrome" in w.window_text()), None)
        
        if not chrome:
            print("No Chrome window found.")
            return None

        # Fix: Get the actual window top coordinate
        window_rect = chrome.rectangle()
        window_top = window_rect.top
        
        # 180-200 is usually enough for tabs + address bar + bookmarks
        # Anything below this is likely the sidebar or webpage
        HEADER_HEIGHT_LIMIT = 200 
        
        elements = []
        # Get buttons and links
        all_descendants = chrome.descendants(control_type="Button") + \
                          chrome.descendants(control_type="Hyperlink")

        for i, el in enumerate(all_descendants):
            if not el.is_visible(): continue
            
            rect = el.rectangle()
            mid_y = rect.mid_point().y
            
            # --- THE FILTER ---
            # If the button is too low, it's probably the sidebar or a browser extension pane
            if mid_y > (window_top + HEADER_HEIGHT_LIMIT):
                continue

            elements.append({
                "id": 9000 + i, # IDs start at 9000 to avoid clash with web elements
                "category": "browser",
                "text": el.window_text() or el.element_info.name or "Unnamed",
                "x": rect.mid_point().x,
                "y": mid_y
            })
        
        print(f"Captured {len(elements)} browser-level elements.")
        return elements

    except Exception as e:
        print(f"Pywinauto Error: {e}")
        return None

async def scan_existing_page():
    async with async_playwright() as p:
        # Connect to Chrome debug port
        try:
            browser = await p.chromium.connect_over_cdp("http://localhost:9222")
        except Exception as e:
            print("Could not connect to Chrome. Ensure it's open with --remote-debugging-port=9222")
            return

        if len(browser.contexts) == 0:
            print("No active browser context found.")
            return
            
        context = browser.contexts[0]
        page = context.pages[0] 

        active_title = await page.title()
        print(f"Scanning current page: {await page.title()}")

        # Extract elements with Category Distinguishers
        elements = await page.evaluate("""() => {
            const interactables = Array.from(document.querySelectorAll('button, a, input, [role="button"], [role="link"]'));
            return interactables.map((el, index) => {
                const rect = el.getBoundingClientRect();
                
                // Distinguishers logic
                const isLink = el.tagName === 'A' || el.getAttribute('role') === 'link';
                const isInput = el.tagName === 'INPUT';
                const hasPopup = el.getAttribute('aria-haspopup'); 
                const href = el.getAttribute('href'); 
                const type = el.getAttribute('type'); 

                let category = "action";
                if (isLink) category = "link";
                if (isInput) category = "input";
                if (hasPopup) category = "menu/sidebar";
                if (type === 'submit' || el.innerText.toLowerCase().includes('search')) category = "search";

                return {
                    id: index,
                    tag: el.tagName,
                    category: category,
                    text: (el.innerText || el.getAttribute('aria-label') || el.value || "No Label").trim(),
                    destination: href ? href : "internal",
                    x: Math.round(rect.left + rect.width / 2),
                    y: Math.round(rect.top + rect.height / 2),
                    visible: rect.width > 0 && rect.height > 0
                };
            }).filter(e => e.visible && e.text !== "");
        }""")

        MANUAL_HEADER = [
            {"id": 9001, "category": "browser", "text": "Back Button", "x": 30, "y": 55},
            {"id": 9002, "category": "browser", "text": "Forward Button", "x": 70, "y": 55},
            {"id": 9003, "category": "browser", "text": "Refresh", "x": 110, "y": 55},
            {"id": 9004, "category": "browser", "text": "Address Bar", "x": 500, "y": 55},
        ]

        CHROME_HEADER = await scan_header_chrome()
        if not CHROME_HEADER:
            CHROME_HEADER = MANUAL_HEADER

        all_elements = elements + CHROME_HEADER

        with open("ui_map.json", "w") as f:
            json.dump(all_elements, f, indent=4)
        
        print(f"Success! Captured {len(elements)} elements to ui_map.json")

if __name__ == "__main__":
    asyncio.run(scan_existing_page())