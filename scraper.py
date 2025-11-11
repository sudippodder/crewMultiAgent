# scraper.py
from newspaper import Article
import requests
from bs4 import BeautifulSoup
import json
from tqdm import tqdm

def scrape_with_newspaper(url):
    try:
        a = Article(url)
        a.download(); a.parse()
        return {"title": a.title, "text": a.text, "url": url}
    except Exception:
        return None

def fallback_scrape(url):
    try:
        r = requests.get(url, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")
        # naive body extraction — adapt for your site
        paragraphs = soup.find_all("p")
        text = "\n\n".join(p.get_text(strip=True) for p in paragraphs)
        title = soup.title.string if soup.title else ""
        return {"title": title, "text": text, "url": url}
    except Exception:
        return None

def scrape_urls(urls, out_file="scraped.jsonl"):
    with open(out_file, "w", encoding="utf8") as fout:
        for u in tqdm(urls):
            r = scrape_with_newspaper(u) or fallback_scrape(u)
            if r and r["text"].strip():
                fout.write(json.dumps(r, ensure_ascii=False) + "\n")

if __name__ == "__main__":
    # replace with your list
    urls = open("urls.txt").read().splitlines()
    scrape_urls(urls)
