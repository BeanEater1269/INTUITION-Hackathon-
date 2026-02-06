import json
import winsound
import pyautogui
import time

# Sound Frequencies (Hz)
EDGE_SOUND = 1000   # High pitch
BROWSER_SOUND = 600 # Mid pitch
WEB_SOUND = 400     # Low pitch

def play_haptic(freq):
    # Short duration (50ms) makes it feel like a "tick"
    winsound.Beep(freq, 50)

def monitor_mouse():
    last_id = -1
    screen_w, screen_h = pyautogui.size()
    
    print("Haptic feedback active...")
    
    while True:
        try:
            x, y = pyautogui.position()
            
            # 1. Edge Detection
            if x <= 0 or x >= screen_w - 1 or y <= 0 or y >= screen_h - 1:
                play_haptic(EDGE_SOUND)
                time.sleep(0.1)
                continue

            # 2. Button Detection (via ui_map.json)
            with open("ui_map.json", "r") as f:
                elements = json.load(f)
            
            found_button = False
            for e in elements:
                # Check if mouse is within 20 pixels of a button center
                # You can adjust this 'hitbox' based on button size
                dist = ((x - e['x'])**2 + (y - e['y'])**2)**0.5
                if dist < 25:
                    if e['id'] != last_id: # Only beep once per entry
                        if e['id'] >= 9000:
                            play_haptic(BROWSER_SOUND)
                        else:
                            play_haptic(WEB_SOUND)
                        last_id = e['id']
                    found_button = True
                    break
            
            if not found_button:
                last_id = -1 # Reset if we moved off a button

        except Exception:
            pass
        
        time.sleep(0.05) # 20Hz refresh rate is plenty
        