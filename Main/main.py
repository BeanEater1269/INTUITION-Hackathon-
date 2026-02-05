from pynput import keyboard
import grid_based_screenshot
import converter

def button_press(key):
    if key == keyboard.Key.esc:
        print("Escaping Program")
        return False

    try:
        if key.char == "c":
            print("Describe Webpage")
        if key.char == "b":
            print("Execute Action")
    except AttributeError:
        pass

with keyboard.Listener(on_press=button_press) as listener:
    listener.join()