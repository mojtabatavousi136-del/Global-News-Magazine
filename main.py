import feedparser, requests, jdatetime, pytz
from bs4 import BeautifulSoup
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

SOURCES = {
    "Al Jazeera": "https://www.aljazeera.com/xml/rss/all.xml",
    "BBC World": "https://feeds.bbci.co.uk/news/world/rss.xml",
    "The Guardian": "https://www.theguardian.com/world/rss",
    "New York Times": "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
    "NASA": "https://www.nasa.gov/rss/dyn/breaking_news.rss",
}

def get_tgju_price(url):
    try:
        r = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(r.text, "html.parser")
        for sel in [".info-price span", ".price-value", ".market-price", "strong"]:
            val = soup.select_one(sel)
            if val and val.text.strip():
                return val.text.strip()
        return "N/A"
    except:
        return "N/A"

def fetch_feed(name, url):
    try:
        feed = feedparser.parse(url)
        articles = []
        for e in feed.entries[:8]:
            img = ""
            if hasattr(e, "media_thumbnail"):
                img = e.media_thumbnail[0].get("url", "")
            elif hasattr(e, "media_content"):
                img = e.media_content[0].get("url", "")
            # full summary, no truncation
            summary = e.get("summary", "")
            soup = BeautifulSoup(summary, "html.parser")
            summary = soup.get_text(separator=" ").strip()
            articles.append({
                "source": name,
                "title": e.get("title", ""),
                "link": e.get("link", ""),
                "summary": summary,
                "image": img,
            })
        return articles
    except:
        return []

def build_card(a):
    img_html = f'<img src="{a["image"]}" onerror="this.style.display=\'none\'">' if a["image"] else ""
    return f"""
<div class="card">
  {img_html}
  <div class="card-body">
    <span class="badge">{a["source"]}</span>
    <h3><a href="{a["link"]}" target="_blank">{a["title"]}</a></h3>
    <p>{a["summary"]}</p>
  </div>
</div>"""

def main():
    now_utc = datetime.now(pytz.utc)
    now_tehran = now_utc.astimezone(pytz.timezone("Asia/Tehran"))
    jalali = jdatetime.datetime.fromgregorian(datetime=now_tehran)
    timestamp = f"{jalali.strftime('%Y/%m/%d')} | {now_tehran.strftime('%Y-%m-%d %H:%M')} Tehran"

    with ThreadPoolExecutor() as ex:
        futures = {name: ex.submit(fetch_feed, name, url) for name, url in SOURCES.items()}
        gold_f = ex.submit(get_tgju_price, "https://www.tgju.org/profile/geram18")
        dollar_f = ex.submit(get_tgju_price, "https://www.tgju.org/profile/price_dollar_rl")

    all_articles = []
    for name, f in futures.items():
        all_articles.extend(f.result())

    gold = gold_f.result()
    dollar = dollar_f.result()
    cards = "\n".join(build_card(a) for a in all_articles)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Global News Magazine</title>
<style>
  body {{ font-family: Arial, sans-serif; background: #f4f4f4; margin: 0; }}
  header {{
    background: #1a1a2e; color: white; padding: 16px 24px;
    display: grid; grid-template-columns: 1fr auto 1fr; align-items: center; gap: 8px;
  }}
  .header-left {{ display: flex; justify-content: flex-start; }}
  .header-center {{ text-align: center; font-size: 1.5rem; font-weight: bold; white-space: nowrap; }}
  .header-right {{ display: flex; justify-content: flex-end; align-items: center; gap: 8px; font-size: 0.85rem; color: #aaa; }}
  .header-right a {{ color: #aad4f5; text-decoration: none; }}
  .ticker {{ background: #16213e; color: #f5c518; padding: 8px 24px; font-size: 0.9rem; }}
  .feed {{ display: flex; flex-direction: column; gap: 16px; padding: 24px; max-width: 860px; margin: auto; }}
  .card {{ background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 6px rgba(0,0,0,.1); display: flex; gap: 16px; }}
  .card img {{ width: 220px; min-width: 220px; height: 150px; object-fit: cover; }}
  .card-body {{ padding: 14px; flex: 1; }}
  .badge {{ background: #1a1a2e; color: white; font-size: 0.7rem; padding: 2px 8px; border-radius: 12px; }}
  h3 {{ font-size: 1rem; margin: 8px 0; }}
  h3 a {{ color: #1a1a2e; text-decoration: none; }}
  h3 a:hover {{ text-decoration: underline; }}
  p {{ font-size: 0.88rem; color: #444; margin: 0; line-height: 1.6; }}
  footer {{ text-align: center; padding: 16px; font-size: 0.8rem; color: #888; }}
  @media(max-width: 600px) {{
    .card {{ flex-direction: column; }}
    .card img {{ width: 100%; height: 180px; min-width: unset; }}
    header {{ grid-template-columns: 1fr; text-align: center; }}
    .header-left, .header-right {{ justify-content: center; }}
  }}
</style>
</head>
<body>
<header>
  <div class="header-left"></div>
  <div class="header-center">🌍 Global News Magazine</div>
  <div class="header-right">
    <a href="https://mojtabatavousi136-del.github.io/my-news-feed/" target="_blank">🇮🇷 Persian Edition</a>
    <span>| {timestamp}</span>
  </div>
</header>
<div class="ticker">💵 Dollar: {dollar} IRR &nbsp;|&nbsp; 🥇 Gold (18K): {gold} IRR</div>
<div class="feed">
{cards}
</div>
<footer>Auto-updated via GitHub Actions</footer>
</body>
</html>"""

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("index.html generated.")

if __name__ == "__main__":
    main()
