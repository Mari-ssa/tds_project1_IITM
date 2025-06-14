import json
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

# File to save the scraped notes
OUTPUT_DIR = Path("scraped_notes")
OUTPUT_DIR.mkdir(exist_ok=True)

# Load the list of URLs from the saved JSON file
with open("tds_urls.json", "r", encoding="utf-8") as f:
    urls = json.load(f)

def sanitize_filename(url):
    return url.split("#/")[-1].replace("/", "_") or "README"

def scrape_tds_notes():
    print("📚 Launching browser and starting to scrape TDS notes...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        for i, url in enumerate(urls):
            print(f"🔗 Scraping [{i+1}/{len(urls)}]: {url}")
            try:
                page.goto(url, timeout=60000)
                page.wait_for_selector("main", timeout=10000)
                content = page.locator("main").inner_text()

                filename = sanitize_filename(url) + ".txt"
                with open(OUTPUT_DIR / filename, "w", encoding="utf-8") as f:
                    f.write(content)

                print(f"✅ Saved: {filename}")
                time.sleep(1)

            except Exception as e:
                print(f"❌ Failed to scrape {url}: {e}")

        browser.close()
        print("🎉 Scraping complete!")

if __name__ == "__main__":
    scrape_tds_notes()
