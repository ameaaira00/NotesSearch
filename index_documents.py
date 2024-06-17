"""
This script indexes processed notes from a JSON file using a GPT-2 model.
It tokenizes each section (breaks down text into meaningful units called tokens) using GPT-2's tokenizer,
generates embeddings (transforms text into numerical representations) using the GPT-2 model,
and stores these embeddings in an Annoy index for efficient similarity search.
"""

import json
import torch
from transformers import GPT2Tokenizer, GPT2Model
from annoy import AnnoyIndex


def index_notes():
    """
    Indexes processed notes from a JSON file using a GPT-2 model.
    Tokenization involves breaking down text into tokens or subwords,
    while embeddings refer to numerical representations of text.
    """
    with open("processed_notes.json", "r", encoding="utf-8") as file:
        notes = json.load(file)

    # Initialize tokenizer and model
    tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
    model = GPT2Model.from_pretrained("gpt2")

    # Initialize Annoy index
    embedding_dim = 768  # Adjust based on your model's output dimensions
    annoy_index = AnnoyIndex(embedding_dim, "angular")

    for idx, note in enumerate(notes):
        # Tokenize and encode the section
        encoded_input = tokenizer(note["section"], return_tensors="pt")

        # Generate embeddings
        with torch.no_grad():
            output = model(**encoded_input)

        # Use CLS token embedding (first token) instead of mean pooling
        cls_embedding = output.last_hidden_state[:, 0, :].numpy().flatten()

        # Add item to Annoy index
        annoy_index.add_item(idx, cls_embedding)

    # Build the Annoy index
    annoy_index.build(50)  # Increase number of trees for better accuracy
    annoy_index.save("notes_index.ann")


if __name__ == "__main__":
    index_notes()
