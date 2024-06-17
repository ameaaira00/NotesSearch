"""
This Flask application provides a web interface for searching through indexed notes using a GPT-2 model.
It loads an Annoy index and processed notes from JSON files, initializes a GPT-2 tokenizer and model,
and defines routes for rendering search interface, handling search queries, and displaying results.
"""

from flask import Flask, render_template, request
import json
import torch
from transformers import GPT2Tokenizer, GPT2Model
from annoy import AnnoyIndex
import numpy as np

app = Flask(__name__)

# Load Annoy index and processed notes
annoy_index = AnnoyIndex(768, "angular")
annoy_index.load("notes_index.ann")

with open("processed_notes.json", "r", encoding="utf-8") as file:
    notes = json.load(file)

# Initialize tokenizer and model
tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
model = GPT2Model.from_pretrained("gpt2")


# Function to calculate cosine similarity
def cosine_similarity(v1, v2):
    """
    Calculates the cosine similarity between two vectors.

    Args:
        v1 (np.array): Vector 1.
        v2 (np.array): Vector 2.

    Returns:
        float: Cosine similarity score between v1 and v2.
    """
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))


@app.route("/")
def index():
    """
    Renders the index.html template for the main search page.

    Returns:
        flask.render_template: Rendered HTML template.
    """
    return render_template("index.html")


@app.route("/search", methods=["POST"])
def search():
    """
    Handles POST requests to /search route to process search queries.

    Returns:
        flask.render_template: Rendered HTML template with search results.
    """
    query = request.form["query"]

    # Encode query using tokenizer
    encoded_query = tokenizer(query, return_tensors="pt")

    # Generate embedding for the query
    with torch.no_grad():
        query_embedding = (
            model(**encoded_query).last_hidden_state[:, 0, :].numpy().flatten()
        )

    # Search in Annoy index
    search_results = annoy_index.get_nns_by_vector(query_embedding, 2)

    # Calculate similarity scores and rank results
    results = []
    for idx in search_results:
        note = notes[idx]
        section = note["section"]
        encoded_section = tokenizer(section, return_tensors="pt")
        with torch.no_grad():
            section_embedding = (
                model(**encoded_section).last_hidden_state[:, 0, :].numpy().flatten()
            )
        similarity_score = cosine_similarity(query_embedding, section_embedding)
        results.append(
            {
                "file": note["file"],
                "section": section,
                "similarity_score": similarity_score,
            }
        )

    # Sort results by similarity score (descending)
    results = sorted(results, key=lambda x: x["similarity_score"], reverse=True)

    return render_template("results.html", results=results)


if __name__ == "__main__":
    app.run(debug=True)
