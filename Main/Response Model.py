from typing import Any, Literal, TypeAlias



import time
import requests
import torch

from PIL import Image

from pydantic import BaseModel, Field

from transformers import AutoModelForImageTextToText, AutoProcessor

from transformers.models.qwen2_vl.image_processing_qwen2_vl import smart_resize



whole_start = time.process_time()



model_name = "Hcompany/Holo2-4B"  # or "Hcompany/Holo2-8B", "Hcompany/Holo2-30B-A3B"



# Load model and processor

print("--- Start: Loading Model to Memory ---")

model = AutoModelForImageTextToText.from_pretrained(

    model_name,

    dtype=torch.bfloat16,

    device_map="auto",

)

processor = AutoProcessor.from_pretrained(model_name)

print("--- Success: Model is ready for inference! ---")



class ClickCoordinates(BaseModel):

    x: int = Field(ge=0, le=1000, description="The x coordinate, normalized between 0 and 1000.")

    y: int = Field(ge=0, le=1000, description="The y coordinate, normalized between 0 and 1000.")



ChatMessage: TypeAlias = dict[str, Any]





def get_chat_messages(task: str, image: Image.Image) -> list[ChatMessage]:

    """Create the prompt structure for navigation task"""

    prompt = f"""Localize an element on the GUI image according to the provided target and output a click position.

     * You must output a valid JSON following the format: {ClickCoordinates.model_json_schema()}

     Your target is:"""



    return [

        {

            "role": "user",

            "content": [

                {"type": "image", "image": image},

                {"type": "text", "text": f"{prompt}\n{task}"},

            ],

        },

    ]





image_path: str = r"C:\Users\atamc\Pictures\Screenshots\Screenshot 2026-02-05 213958.png"



# Open image from local file

image = Image.open(image_path)



# Define task

task: str = "Click the FAQ button on the webpage."



print("Resizing and processing image...")

# Resize image according to model's image processor

image_processor_config = processor.image_processor

resized_height, resized_width = smart_resize(

    image.height,

    image.width,

    factor=image_processor_config.patch_size * image_processor_config.merge_size,

    min_pixels=image_processor_config.size.get("shortest_edge", None),

    max_pixels=image_processor_config.size.get("longest_edge", None),

)



processed_image: Image.Image = image.resize(size=(resized_width, resized_height), resample=Image.Resampling.LANCZOS)



# Create the prompt

messages: list[dict[str, Any]] = get_chat_messages(task, processed_image)



# Apply chat template

# Note - For localization we set thinking to False

text_prompt = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True, thinking=False)



# Process inputs

inputs = processor(

    text=[text_prompt],

    images=[processed_image],

    padding=True,

    return_tensors="pt",

).to(model.device)



print("Generating Response...")

generation_start = time.process_time()



# Generate response

generated_ids = model.generate(**inputs, max_new_tokens=32)



def parse_reasoning(generated_ids:torch.tensor)->tuple[torch.tensor,torch.tensor]:

    """Parse content from generated_ids"""

    all_ids = generated_ids[0].tolist()

    think_start_index = all_ids.index(151667)

    try:

        think_end_index = all_ids.index(151668)

    except:

        think_end_index = len(all_ids)



    thinking_content = processor.decode(all_ids[think_start_index+1:think_end_index], skip_special_tokens=True).strip("\n")

    content = processor.decode(all_ids[think_end_index+1:], skip_special_tokens=True).strip("\n")



    return content, thinking_content



content, thinking_content = parse_reasoning(generated_ids)



generation_end = time.process_time()

print("Time taken for generation:", generation_end - whole_start)



print("Content:", content)

print("Thinking:", thinking_content)



action = ClickCoordinates.model_validate_json(content)

print("action:", action)

