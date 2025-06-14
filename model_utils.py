import os
import requests
from dotenv import load_dotenv

load_dotenv()

AIPIPE_TOKEN = os.getenv("AIPIPE_TOKEN")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")  


def chunk_text(text, max_chunk_size=1000):
    """Split text into chunks roughly max_chunk_size characters, breaking at newlines."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + max_chunk_size
        if end < len(text):
            # try to break at last newline before end
            last_newline = text.rfind("\n", start, end)
            if last_newline != -1 and last_newline > start:
                end = last_newline
        chunks.append(text[start:end].strip())
        start = end
    return chunks


def select_relevant_chunks(question, chunks, top_k=3):
    """Select chunks with highest keyword overlap with question."""
    question_words = set(question.lower().split())
    scored = []
    for chunk in chunks:
        chunk_words = set(chunk.lower().split())
        score = len(question_words.intersection(chunk_words))
        scored.append((score, chunk))
    scored.sort(key=lambda x: x[0], reverse=True)
    relevant = [chunk for score, chunk in scored if score > 0][:top_k]
    if not relevant:
        # fallback if no overlap found
        relevant = chunks[:top_k]
    return relevant


def generate_answer(question, tds_content, model="gpt-4o-mini"):
    # Prepare full text context
    if isinstance(tds_content, list):
        full_text = "\n\n".join(item.get("text", "") for item in tds_content)
    elif isinstance(tds_content, str):
        full_text = tds_content
    else:
        full_text = str(tds_content)

    # Chunk and select relevant parts to avoid exceeding token limits
    chunks = chunk_text(full_text)
    relevant_chunks = select_relevant_chunks(question, chunks)

    context = "\n\n".join(relevant_chunks)

    prompt = f"""You are a helpful assistant for the IITM BS Degree in Data Science.

Use the following course material and discussion forum posts to answer the question.

Context:
{context}

Question:
{question}

Answer:"""

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a helpful teaching assistant."},
            {"role": "user", "content": prompt}
        ]
    }

    headers = {
        "Authorization": f"Bearer {AIPIPE_TOKEN}",
        "Content-Type": "application/json"
    }

    response = requests.post(f"{OPENAI_BASE_URL}/chat/completions", headers=headers, json=payload)

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"].strip()
    else:
        raise Exception(f"API Error {response.status_code}: {response.text}")
