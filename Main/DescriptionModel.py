import torch
from PIL import Image
from transformers import AutoProcessor, AutoModelForCausalLM
import time
# device = "cuda:0" if torch.cuda.is_available() else "cpu"
# torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

# model = AutoModelForCausalLM.from_pretrained("microsoft/Florence-2-large", torch_dtype=torch_dtype, trust_remote_code=True).to(device)
# processor = AutoProcessor.from_pretrained("microsoft/Florence-2-large", trust_remote_code=True)

prompt = "<MORE_DETAILED_CAPTION>"

image_path = "test-image.jpeg"
def generate_description(image, processor, model, device, torch_dtype):
    
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

    parsed_answer = processor.post_process_generation(generated_text, task="<MORE_DETAILED_CAPTION>", image_size=(image.width, image.height))
    print(time.time()-t)
    return parsed_answer