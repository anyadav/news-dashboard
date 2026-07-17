#!/usr/bin/env python3
"""
fetch_news.py

Fetches the latest headlines from a curated set of official RSS feeds,
grouped by country/region, deduplicates similar stories, keeps the top
10 items per category, and writes the result to docs/news.json.

Free-tier only: no paid APIs, no API keys required. Uses the feedparser
library to read publicly available RSS feeds.
"""

import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path

import feedparser

# Map of category -> list of (source_name, rss_url)
FEEDS = {
    "India": [
        ("The Hindu", "https://www.thehindu.com/news/national/feeder/default.rss"),
        ("Times of India", "https://timesofindia.indiatimes.com/rssfeedstopstories.cms"),
        ("NDTV", "https://feeds.feedburner.com/ndtvnews-top-stories"),
    ],
"Nepal": [
("The Kathmandu Post", "https://kathmandupost.com/rss"),
],
"Bhutan": [
("Kuensel", "https://kuenselonline.com/feed/posts"),
],
"Bangladesh": [
("The Daily Star", "https://www.thedailystar.net/rss.xml"),
],
"Myanmar": [
("Myanmar Now", "https://myanmar-now.org/en/feed/"),
],
"Pakistan": [
("Dawn", "https://www.dawn.com/feeds/home"),
],
"Afghanistan": [
("Khaama Press", "https://www.khaama.com/feed/"),
],
    "Taiwan": [
        ("Focus Taiwan", "https://focustaiwan.tw/rss/news.xml"),
        ("Taipei Times", "https://www.taipeitimes.com/xml/index.rss"),
    ],
    "China": [
        ("SCMP", "https://www.scmp.com/rss/91/feed"),
    ],
    "Japan": [
        ("NHK World", "https://www3.nhk.or.jp/rss/news/cat0.xml"),
        ("Japan Times", "https://www.japantimes.co.jp/feed/"),
    ],
    "USA": [
        ("Reuters", "https://feeds.reuters.com/reuters/topNews"),
        ("AP News", "https://apnews.com/apf-topnews?format=rss"),
        ("NPR", "https://feeds.npr.org/1001/rss.xml"),
    ],
    "International": [
        ("BBC World", "http://feeds.bbci.co.uk/news/world/rss.xml"),
        ("Al Jazeera", "https://www.aljazeera.com/xml/rss/all.xml"),
    ],
    "Sports": [
        ("BBC Sport", "http://feeds.bbci.co.uk/sport/rss.xml"),
        ("ESPN", "https://www.espn.com/espn/rss/news"),
        ("Sky Sports", "https://www.skysports.com/rss/12040"),
    ],
    "World Politics": [
        ("The Guardian World", "https://www.theguardian.com/world/rss"),
        ("Politico", "https://www.politico.com/rss/politicopicks.xml"),
        ("DW World", "https://rss.dw.com/rdf/rss-en-world"),
    ],
}

TOP_N_PER_CATEGORY = 10
OUTPUT_PATH = Path(__file__).resolve().parent / "docs" / "news.json"


def clean_summary(raw_summary: str, max_len: int = 280) -> str:
    """Strip HTML-ish leftovers and trim summary text."""
    import re

    text = re.sub(r"<[^>]+>", "", raw_summary or "").strip()
    text = " ".join(text.split())
    if len(text) > max_len:
        text = text[:max_len].rsplit(" ", 1)[0] + "…"
    return text


def entry_timestamp(entry) -> str:
    """Return an ISO 8601 UTC timestamp for a feed entry, best effort."""
    for key in ("published_parsed", "updated_parsed"):
        value = getattr(entry, key, None)
        if value:
            return datetime(*value[:6], tzinfo=timezone.utc).isoformat()
    return datetime.now(timezone.utc).isoformat()


def dedupe_key(title: str, link: str) -> str:
    """Build a fingerprint used to drop near-duplicate stories."""
    normalized = "".join(ch.lower() for ch in title if ch.isalnum())
    return hashlib.sha1((normalized or link).encode("utf-8")).hexdigest()


def fetch_category(sources):
    items = []
    seen = set()

    for source_name, url in sources:
        try:
            parsed = feedparser.parse(url)
        except Exception as exc:  # network/parse errors shouldn't stop the run
            print(f"  [warn] failed to fetch {source_name}: {exc}")
            continue

        if getattr(parsed, "bozo", False) and not parsed.entries:
            print(f"  [warn] no entries parsed for {source_name}")
            continue

        for entry in parsed.entries:
            title = getattr(entry, "title", "").strip()
            link = getattr(entry, "link", "").strip()
            if not title or not link:
                continue

            key = dedupe_key(title, link)
            if key in seen:
                continue
            seen.add(key)

            summary = clean_summary(getattr(entry, "summary", ""))
            items.append(
                {
                    "title": title,
                    "summary": summary,
                    "link": link,
                    "source": source_name,
                    "timestamp": entry_timestamp(entry),
                }
            )

    items.sort(key=lambda item: item["timestamp"], reverse=True)
    return items[:TOP_N_PER_CATEGORY]


def main():
    print("Fetching news...")
    result = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "categories": {},
    }

    for category, sources in FEEDS.items():
        print(f"- {category}")
        result["categories"][category] = fetch_category(sources)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"Wrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
