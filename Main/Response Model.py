import json
import torch
import outlines
import time
from thefuzz import process

# 1. LOAD MODEL CORRECTLY
MODEL_PATH = "Qwen/Qwen2.5-0.5B-Instruct"
# Check if GPU is actually available to avoid the 'cpu' slowness
device = "cuda" if torch.cuda.is_available() else "cpu"

print(f"--- Loading Outlines Model on {device} ---")

# FIX: Use the full path to the transformers loader
# Also, we explicitly pass the tokenizer to avoid 'module' callable issues
model = outlines.models.transformers(
    MODEL_PATH, 
    device=device,
    model_kwargs={"torch_dtype": torch.float16 if device == "cuda" else torch.float32}
)

def select_id_with_grammar(query, json_path="ui_map.json"):
    try:
        with open(json_path, "r") as f:
            elements = json.load(f)
    except FileNotFoundError:
        return None

    # --- STEP A: PRE-FILTER (Essential for Outlines Performance) ---
    choices_map = {e['text']: str(e['id']) for e in elements if e['text']}
    top_matches = process.extract(query, choices_map.keys(), limit=15)
    filtered_ids = [choices_map[text] for text, score in top_matches]
    
    # Always include browser buttons
    for e in elements:
        if e.get('category') == 'browser' and str(e['id']) not in filtered_ids:
            filtered_ids.append(str(e['id']))

    # --- STEP B: FORMAT PROMPT ---
    # Vertical lists are easier for Qwen to "scan"
    context_str = "\n".join([f"{eid}: {next(e['text'] for e in elements if str(e['id']) == eid)}" for eid in filtered_ids])
    
    prompt = f"""<|im_start|>system
You are a UI router. Respond only with an ID number from the list.<|im_end|>
<|im_start|>user
Elements:
{context_str}

Target: {query}
Selected ID:<|im_end|>
<|im_start|>assistant
"""

    # --- STEP C: CONSTRAINED GENERATION ---
    # This 'choice' generator restricts the LLM's vocabulary to ONLY the IDs in filtered_ids
    # 
    generator = outlines.generate.choice(model, filtered_ids)
    
    start_time = time.time()
    selected_id = generator(prompt)
    print(f"Inference Time: {time.time() - start_time:.4f}s")
    
    return int(selected_id)

if __name__ == "__main__":
    # Test
    res = select_id_with_grammar("go back")
    print(f"AI Selected ID: {res}")