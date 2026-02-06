import json
import asyncio
import pyautogui
from playwright.async_api import async_playwright
from thefuzz import process

async def smart_interact(target_id):
    try:
        with open("ui_map.json", "r") as f:
            elements = json.load(f)
        target_data = next((e for e in elements if e['id'] == target_id), None)
        if not target_data:
            print(f"ID {target_id} not found.")
            return
    except FileNotFoundError:
        print("Run scan first!")
        return

    async with async_playwright() as p:
        try:
            browser = await p.chromium.connect_over_cdp("http://localhost:9222")
            page = browser.contexts[0].pages[0]
        except:
            print("Connection failed. Is Chrome in debug mode?")
            return

        target_text = target_data['text']
        category = target_data.get('category', 'action')
        print(f"Targeting ID {target_id} ({category}): '{target_text}'")
        locator = page.get_by_text(target_text, exact=False).first
        
        try:
            if await locator.is_visible():
                print("Clicking via Playwright...")
                await locator.click(timeout=3000)
                return f"Success: Clicked {target_text}"
        except Exception as e:
            print(f"Playwright attempt failed: {e}")

        # FALLBACK: PYAUTOGUI
        print("Falling back to Coordinate Click...")
        OFFSET = 240 
        
        if target_data['y'] < 0:
            print("Element is above viewport. Scrolling up...")
            pyautogui.scroll(1500)
            await asyncio.sleep(0.5)

        if target_data['category'] == "browser":
            # Pywinauto gives ABSOLUTE screen coordinates. No offset needed!
            pyautogui.moveTo(target_data['x'], target_data['y'])
            pyautogui.click(target_data['x'], target_data['y'])
        else:
            pyautogui.moveTo(target_data['x'], target_data['y'] + OFFSET, duration=0.8)
            pyautogui.click()
            
        return f"Clicked via coordinates at {target_data['x']}, {target_data['y'] + OFFSET}"

if __name__ == "__main__":
    tid = int(input("Enter ID: "))
    asyncio.run(smart_interact(tid))