import json
from pywinauto import Desktop

def scan_standard_chrome():
    print("\n[!] Scanning standard Chrome window via OS hooks...")
    try:
        windows = Desktop(backend="uia").windows()
        chrome = next((w for w in windows if "Google Chrome" in w.window_text()), None)
        
        if not chrome:
            print("No Chrome window found.")
            return

        elements = []
        for i, el in enumerate(chrome.descendants(control_type="Button") + 
                               chrome.descendants(control_type="Hyperlink")):
            
            if not el.is_visible(): continue
            
            rect = el.rectangle()
            elements.append({
                "id": i,
                "category": "browser" if i > 9000 else "web_element",
                "text": el.window_text() or el.element_info.name or "Unnamed",
                "x": rect.mid_point().x,
                "y": rect.mid_point().y
            })

        with open("ui_map.json", "w") as f:
            json.dump(elements, f, indent=4)
        
        print(f"Captured {len(elements)} elements using OS Accessibility Tree.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    scan_standard_chrome()