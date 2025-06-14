import json
import numpy as np
from typing import List, Tuple
import requests
import os
from dotenv import load_dotenv
load_dotenv()

# Load API key and base URL
API_KEY = os.getenv("OPENAI_API_KEY")
BASE_URL = os.getenv("OPENAI_BASE_URL")

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Load embeddings from file
def load_embeddings(filepath: str):
    embeddings = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            record = json.loads(line)
            embeddings.append({
                "chunk_id": record["chunk_id"],
                "text": record["text"],
                "embedding": np.array(record["embedding"], dtype=np.float32)
            })
    return embeddings

# Generate embedding for the query
def get_query_embedding(query: str) -> np.ndarray:
    payload = {
        "input": query,
        "model": "text-embedding-ada-002"
    }
    response = requests.post(f"{BASE_URL}/embeddings", headers=HEADERS, json=payload)
    response.raise_for_status()
    return np.array(response.json()["data"][0]["embedding"], dtype=np.float32)

# Compute cosine similarity
def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# Get top N matching chunks
def search_similar_chunks(query: str, embeddings, top_k: int = 5) -> List[Tuple[str, float]]:
    query_embedding = get_query_embedding(query)
    similarities = []

    for item in embeddings:
        sim = cosine_similarity(query_embedding, item["embedding"])
        similarities.append((item["text"], sim))

    # Sort by similarity
    similarities.sort(key=lambda x: x[1], reverse=True)
    return similarities[:top_k]

if __name__ == "__main__":
    data = load_embeddings("tds_embeddings.jsonl")
    query = input("Enter your query: ")
    top_results = search_similar_chunks(query, data)

    print("\n🔍 Top matching chunks:")
    for i, (text, score) in enumerate(top_results, 1):
        print(f"\n#{i} (score: {score:.4f})\n{text}")
