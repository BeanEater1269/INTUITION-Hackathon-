import pyautogui
import keyboard
from PIL import Image
from datetime import datetime
import os
import time

# For Windows High-DPI scaling support
import ctypes
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

def take_screenshot(mode="full"):

    if not os.path.exists("screenshots"):
        os.makedirs("screenshots")
        
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"screenshots/screenshot_{mode}_{timestamp}.jpg"

    # return path to image
    if mode == "full":
        img = pyautogui.screenshot()
        img.convert("RGB").save(filename, "JPEG", quality = 85)
        print(f"Captured Full: {filename}")
        return filename

    elif mode == "partial":
        print("1. Move mouse to TOP-LEFT corner and press 'Ctrl'")
        keyboard.wait('ctrl')
        x1, y1 = pyautogui.position()
        
        time.sleep(0.5) 
        
        print("2. Move mouse to BOTTOM-RIGHT corner and press 'Ctrl'")
        keyboard.wait('ctrl')
        x2, y2 = pyautogui.position()

        start_x = min(x1,x2)
        start_y = min(y1,y2)
        width = abs(x2 - x1)
        height = abs(y2 - y1)
        
        if width > 0 and height > 0:
            img = pyautogui.screenshot(region=(start_x, start_y, width, height))
            img.convert("RGB").save(filename, "JPEG", quality = 85)
            print(f"Captured Partial: {filename}")
            return filename

# Hotkeys
keyboard.add_hotkey("f1", lambda: take_screenshot("full"))
keyboard.add_hotkey("f2", lambda: take_screenshot("partial"))

# keyboard.wait("esc") # Ensure your main program loop handles execution