from pynput import keyboard
import grid_based_screenshot
import converter
import extract_feature, interaction
import DescriptionModel
import os, time
from threading import Thread
import torch
from PIL import Image
from transformers import AutoProcessor, AutoModelForCausalLM

start_time = time.perf_counter()
device = "cuda:0" if torch.cuda.is_available() else "cpu"
torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

model = AutoModelForCausalLM.from_pretrained("microsoft/Florence-2-large", torch_dtype=torch_dtype, trust_remote_code=True).to(device)
processor = AutoProcessor.from_pretrained("microsoft/Florence-2-large", trust_remote_code=True)
prompt = "<MORE_DETAILED_CAPTION>"
print("Done Loading")
def button_press(key):
    if key == keyboard.Key.esc:
        print("Escaping Program")
        return False

    try:
        if key.char == "f":
            print("Describe Webpage")
            img = grid_based_screenshot.take_screenshot()
            # print(img)
            desc = DescriptionModel.generate_description(img, processor, model, device, torch_dtype)
            print(desc)
            # os.remove(image_path)
            Thread(target=converter.textToSpeech, args=(desc['<MORE_DETAILED_CAPTION>'],)).start()
            
        if key.char == "j":
            print("Execute Action")
    except AttributeError:
        pass

with keyboard.Listener(on_press=button_press) as listener:
    listener.join()
