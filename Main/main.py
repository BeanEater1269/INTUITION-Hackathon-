import tkinter as tk
from tkinter import simpledialog
from pynput import keyboard
import grid_based_screenshot
import converter
import time
import haptics
from threading import Thread
import ID_selector,interaction,extract_feature
import torch
from sentence_transformers import SentenceTransformer
from transformers import AutoProcessor, AutoModelForCausalLM

start_time = time.perf_counter()
device = "cuda:0" if torch.cuda.is_available() else "cpu"
torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32
is_busy = False
def generate(image, processor, model, device, torch_dtype, prompt):
    
    t = time.time()
    inputs = processor(text=prompt, images=image, return_tensors="pt").to(device, torch_dtype)
    print("Processing...")
    generated_ids = model.generate(
        input_ids=inputs["input_ids"],
        pixel_values=inputs["pixel_values"],
        max_new_tokens=4096,
        num_beams=3,
        do_sample=False,
    )
    generated_text = processor.batch_decode(generated_ids, skip_special_tokens=False)[0]

    parsed_answer = processor.post_process_generation(generated_text, task=prompt, image_size=(image.width, image.height))
    print(time.time()-t)
    return parsed_answer

model = AutoModelForCausalLM.from_pretrained("microsoft/Florence-2-large", torch_dtype=torch_dtype, trust_remote_code=True).to(device)
processor = AutoProcessor.from_pretrained("microsoft/Florence-2-large", trust_remote_code=True)
EmbeddingModel = SentenceTransformer('all-MiniLM-L6-v2')
print("Model Loaded")

def execute_typed_action():
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True) 
    
    user_input = simpledialog.askstring("Command", "What should I do?")

    root.destroy() 

    if user_input:
        print(f"User wants to: {user_input}")
        target_id = ID_selector.select_id_semantically(user_input,EmbeddingModel)
        
        if target_id is not None:
            interaction.smart_interact(target_id)
        else:
            print("No matching element found.")

def button_press(key):
    global is_busy
    if key == keyboard.Key.esc:
        print("Closing Program")
        return False
    try:
        if key.char == "f":
            print("Describe Webpage")
            img = grid_based_screenshot.take_screenshot()
            # print(img)
            desc = generate(img, processor, model, device, torch_dtype, '<MORE_DETAILED_CAPTION>')
            print(desc)
            Thread(target=converter.textToSpeech, args=(desc['<MORE_DETAILED_CAPTION>'],)).start()
            extract_feature.scan_standard_chrome()

        if key.char == "g":
            print("Read Webpage")
            img = grid_based_screenshot.take_screenshot()
            # print(img)
            desc = generate(img, processor, model, device, torch_dtype, '<OCR>')
            print(desc)
            Thread(target=converter.textToSpeech, args=(desc['<OCR>'],)).start() 
            extract_feature.scan_standard_chrome()

        if hasattr(key, 'char') and key.char == "j":
            if is_busy:
                print("Iris is already working, please wait...")
            else:
                is_busy = True  # Lock it immediately
                print("Execute Action triggered...")
                try:
                    text = converter.speechToText()
                    print(f"Captured: {text}")
                    if text:
                        print(f"User wants to: {text}")
                        target_id = ID_selector.select_id_semantically(text, EmbeddingModel)
                        if target_id is not None:
                            interaction.smart_interact(target_id)
                        else:
                            print("No matching element found.")
                finally:
                    is_busy = False

    except AttributeError:
        pass

haptic_thread = Thread(target=haptics.monitor_mouse, daemon=True)
haptic_thread.start()
with keyboard.Listener(on_press=button_press) as listener:
    listener.join()
