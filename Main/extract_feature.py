import json
import asyncio
from playwright.async_api import async_playwright

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

        with open("ui_map.json", "w") as f:
            json.dump(elements, f, indent=4)
        
        print(f"Success! Captured {len(elements)} elements to ui_map.json")

if __name__ == "__main__":
    asyncio.run(scan_existing_page())