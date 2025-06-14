import os
import json
from pathlib import Path
from textwrap import wrap

from transformers import GPT2TokenizerFast

INPUT_DIR = Path("scraped_notes")
OUTPUT_FILE = "tds_chunks.json"

tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")

MAX_TOKENS = 500  # You can adjust this

def chunk_text(text, max_tokens=MAX_TOKENS):
    tokens = tokenizer.encode(text)
    chunks = []
    for i in range(0, len(tokens), max_tokens):
        chunk = tokenizer.decode(tokens[i:i + max_tokens])
        chunks.append(chunk)
    return chunks

all_chunks = []

for filename in os.listdir(INPUT_DIR):
    if filename.endswith(".txt"):
        path = INPUT_DIR / filename
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()

        chunks = chunk_text(text)
        for i, chunk in enumerate(chunks):
            all_chunks.append({
                "filename": filename,
                "chunk_id": f"{filename}_{i}",
                "text": chunk
            })

# Save to file
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(all_chunks, f, indent=2)

print(f"✅ Chunked {len(all_chunks)} text blocks into {OUTPUT_FILE}")
