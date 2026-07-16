News Dashboard — Implementation Plan (Free-Tier Only)
1. Requirements Recap
Country tabs: India, Taiwan, China, Japan, USA + Trending International, Sports and World Politics
Summaries + source links from genuine outlets
Auto-refresh every hour
Zero cost, no automated payments
2. Architecture Options
Option A — RSS-Based (Recommended: 100% free, no API keys)
RSS Feeds → Fetch/Parse (hourly) → Summarize → Store JSON → Dashboard UI

Sources (RSS, free, genuine):
India: The Hindu, Times of India, NDTV
Taiwan: Focus Taiwan (CNA), Taipei Times
China: SCMP, Reuters China
Japan: NHK World, Japan Times
USA: Reuters US, AP, NPR
International: BBC World, Reuters Top News, Al Jazeera
No API keys, no rate-limit billing risk — RSS is open.
Option B — Free News APIs
NewsAPI.org (free dev tier: 100 req/day, no card), GNews (100/day), NewsData.io (200/day)
⚠️ Free tiers throttle; some require card later. Option A is safer for your no-payment rule.
3. Tech Stack (all free)
Layer
Choice
Why
Fetch/parse
Python + feedparser
Simple, robust RSS parsing
Summarize
RSS description field (free) OR extractive summary via sumy/newspaper3k
No LLM API cost
Scheduler
GitHub Actions cron (hourly)
Free 2,000 min/month — hourly job uses ~50 min/month
Storage
JSON file committed to repo
No database needed
Frontend
Static HTML/JS (tabs per country)
No server
Hosting
GitHub Pages
Free, auto-deploys

4. Flow
GitHub Action triggers hourly (cron: 0 * * * *)
Python script pulls ~15 RSS feeds, dedupes, takes top 8–10 per country
Extracts: title, summary (first 2–3 sentences), link, source, timestamp
Writes news.json, commits to repo
GitHub Pages dashboard reads news.json — country tabs, cards with headline/summary/"Read more" link, last-updated stamp
5. Dashboard UI
Tab bar: 🇮🇳 India | 🇹🇼 Taiwan | 🇨🇳 China | 🇯🇵 Japan | 🇺🇸 USA | 🌍 Trending
Card per story: source badge, headline, 2-line summary, timestamp, link
Auto-refresh in browser every 15 min (just re-fetches JSON)
Mobile responsive
6. Effort Estimate
Phase
Effort
Feed curation + parser script
2–3 hrs
GitHub Actions workflow
1 hr
Dashboard UI
3–4 hrs
Testing/tuning feeds
1–2 hrs
Total
~1 weekend

7. Risks & Mitigations
Feed downtime → multiple sources per country, graceful skip
Some outlets deprecate RSS → quarterly feed review
Summaries limited to RSS excerpt → acceptable; full article via link (avoids scraping/copyright issues)
GitHub Actions cron can drift ±5–10 min → fine for hourly news
8. Optional Later
AI summaries via Claude API (paid — flag: violates your no-charge rule, so skip unless you opt in)
Keyword alerts, dark mode, search
Recommendation: Option A end-to-end — zero cost, zero credentials, zero payment risk.
Approve the plan and I can build it right now: the parser script, GitHub Actions YAML, and the dashboard HTML — you'd just create the repo and paste them in. Or I can build a working single-file prototype here first so you can see the UI. Which would you prefer?

