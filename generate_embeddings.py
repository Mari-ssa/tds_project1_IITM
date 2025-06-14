import json
import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")
BASE_URL = os.getenv("OPENAI_BASE_URL")

print("Loaded API_KEY:", API_KEY[:10], "...")
print("Loaded BASE_URL:", BASE_URL)

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

with open("tds_chunks.json", "r", encoding="utf-8") as f:
    chunks = json.load(f)

output_file = open("tds_embeddings.jsonl", "w", encoding="utf-8")

for i, chunk in enumerate(chunks):
    print(f"🔢 Generating embedding for chunk {i + 1}/{len(chunks)}")
    
    payload = {
        "input": chunk["text"],
        "model": "text-embedding-ada-002"
    }

    try:
        res = requests.post(f"{BASE_URL}/embeddings", headers=HEADERS, json=payload, timeout=30)
        res.raise_for_status()
        embedding = res.json()["data"][0]["embedding"]

        output_file.write(json.dumps({
            "chunk_id": chunk["chunk_id"],
            "text": chunk["text"],
            "embedding": embedding 
        }) + "\n")

    except Exception as e:
        print(f"❌ Failed for chunk {chunk['chunk_id']}: {e}")

output_file.close()
print("✅ All embeddings generated and saved to tds_embeddings.jsonl")
