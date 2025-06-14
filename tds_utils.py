import json

def load_tds_content():
    with open("tds_chunks.json", "r", encoding="utf-8") as f:
        return json.load(f)
