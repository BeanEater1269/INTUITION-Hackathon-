import requests
import time

import torch
from PIL import Image
from transformers import AutoProcessor, AutoModelForCausalLM, TextStreamer

start_time = time.perf_counter()
device = "cuda:0" if torch.cuda.is_available() else "cpu"
torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

model = AutoModelForCausalLM.from_pretrained("microsoft/Florence-2-large", torch_dtype=torch_dtype, trust_remote_code=True).to(device)
processor = AutoProcessor.from_pretrained("microsoft/Florence-2-large", trust_remote_code=True)

prompt = "<MORE_DETAILED_CAPTION>"

image_path = "test-image.jpeg"
image = Image.open(image_path).convert("RGB")

inputs = processor(text=prompt, images=image, return_tensors="pt").to(device, torch_dtype)
##streamer = TextStreamer(processor.tokenizer, skip_prompt=True, skip_special_tokens=True)

generated_ids = model.generate(
    input_ids=inputs["input_ids"],
    pixel_values=inputs["pixel_values"],
    max_new_tokens=4096,
    num_beams=3,
    do_sample=False,
)
generated_text = processor.batch_decode(generated_ids, skip_special_tokens=False)[0]

parsed_answer = processor.post_process_generation(generated_text, task="<MORE_DETAILED_CAPTION>", image_size=(image.width, image.height))

print(parsed_answer)
end_time = time.perf_counter()
print(f"Elapsed time: {end_time - start_time:.6f} seconds")