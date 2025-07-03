import requests
import json
from datetime import datetime

CATEGORY_ID = 34
START_DATE = datetime.strptime("2025-01-01", "%Y-%m-%d")
END_DATE = datetime.strptime("2025-04-14", "%Y-%m-%d")

def scrape_discourse_kb():
    all_posts = []
    base_url = "https://discourse.onlinedegree.iitm.ac.in"

    # Get list of topics in category 34
    topics_url = f"{base_url}/c/{CATEGORY_ID}.json"
    r = requests.get(topics_url)
    topics = r.json().get("topic_list", {}).get("topics", [])

    print(f"Found {len(topics)} topics in category {CATEGORY_ID}")

    for topic in topics:
        topic_id = topic["id"]
        topic_slug = topic["slug"]
        topic_url = f"{base_url}/t/{topic_slug}/{topic_id}.json"
        print(f"Fetching topic: {topic_url}")

        res = requests.get(topic_url)
        if res.status_code != 200:
            print(f"Failed to fetch topic {topic_id}")
            continue

        topic_data = res.json()
        for post in topic_data.get("post_stream", {}).get("posts", []):
            created_at = datetime.strptime(post["created_at"][:10], "%Y-%m-%d")
            if START_DATE <= created_at <= END_DATE:
                all_posts.append({
                    "url": f"{base_url}/t/{topic_slug}/{topic_id}/{post['post_number']}",
                    "text": post["cooked"],
                    "created_at": post["created_at"]
                })

    with open("tds_kb_posts.json", "w", encoding="utf-8") as f:
        json.dump(all_posts, f, indent=2)

    print(f"Saved {len(all_posts)} posts to tds_kb_posts.json")

if __name__ == "__main__":
    scrape_discourse_kb()
