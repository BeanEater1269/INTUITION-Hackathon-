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
def generate(image, processor, model, device, torch_dtype, prompt):
    
    t = time.time()
    inputs = processor(text=prompt, images=image, return_tensors="pt").to(device, torch_dtype)
    ##streamer = TextStreamer(processor.tokenizer, skip_prompt=True, skip_special_tokens=True)
    print("Loaded")
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
            desc = generate(img, processor, model, device, torch_dtype, '<MORE_DETAILED_CAPTION>')
            print(desc)
            # Thread(target=converter.textToSpeech, args=(desc['<MORE_DETAILED_CAPTION>'],)).start()
        if key.char == "g":
            print("Read Webpage")
            img = grid_based_screenshot.take_screenshot()
            # print(img)
            desc = generate(img, processor, model, device, torch_dtype, '<OCR>')
            print(desc)
            Thread(target=converter.textToSpeech, args=(desc['<OCR>'],)).start()   
        if key.char == "j":
            print("Execute Action")
    except AttributeError:
        pass
g
with keyboard.Listener(on_press=button_press) as listener:
    listener.join()
