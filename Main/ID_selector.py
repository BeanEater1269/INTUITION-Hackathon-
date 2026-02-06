import json
import torch
from sentence_transformers import SentenceTransformer, util

EmbeddingModel = SentenceTransformer('all-MiniLM-L6-v2')

def select_id_semantically(query, model , json_path="ui_map.json"):
    try:
        with open(json_path, "r") as f:
            elements = json.load(f)
    except FileNotFoundError:
        return None

    # Extract texts and IDs
    # Filter out empty labels to save time
    valid_elements = [e for e in elements if e['text'].strip()]
    labels = [e['text'] for e in valid_elements]
    ids = [e['id'] for e in valid_elements]

    # Encode the labels and the query
    label_embeddings = model.encode(labels, convert_to_tensor=True)
    query_embedding = model.encode(query, convert_to_tensor=True)

    # Compute Cosine Similarity
    cosine_scores = util.cos_sim(query_embedding, label_embeddings)[0]
    
    # Get the best match
    best_idx = torch.argmax(cosine_scores).item()
    best_score = cosine_scores[best_idx].item()

    print(f"Semantic Match: '{query}' -> '{labels[best_idx]}' (Confidence: {best_score:.2f})")

    if best_score > 0.4: 
        return ids[best_idx]
    
    return None

if __name__ == "__main__":
    print(f"Result ID: {select_id_semantically('click on Google search',EmbeddingModel)}")