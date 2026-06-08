import feedparser, requests, re, pytz
from bs4 import BeautifulSoup
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

FEEDS = [
    ("BBC", "http://feeds.bbci.co.uk/news/rss.xml"),
    ("Reuters", "https://feeds.reuters.com/reuters/topNews"),
    ("Al Jazeera", "https://www.aljazeera.com/xml/rss/all.xml"),
    ("AP News", "https://rsshub.app/apnews/topics/apf-topnews"),
    ("DW", "https://rss.dw.com/rdf/rss-en-all"),
]

def make_session():
    s = requests.Session()
    retry = Retry(total=3, backoff_factor=0.5)
    s.mount("https://", HTTPAdapter(max_retries=retry))
    s.mount("http://", HTTPAdapter(max_retries=retry))
    s.headers.update({"User-Agent": "Mozilla/5.0"})
    return s

SESSION = make_session()

def safe_get(url, timeout=10):
    try:
        r = SESSION.get(url, timeout=timeout)
        return r
    except Exception:
        return None

_JUNK_RE = re.compile(
    r'^[\s\d\W]+$|^(read more|click here|share|tags?|copyright|subscribe|advertisement)\b',
    re.IGNORECASE
)

def is_junk_line(line):
    line = line.strip()
    if len(line) < 15:
        return True
    if _JUNK_RE.search(line):
        return True
    return False

def extract_content(entry):
    html = ""
    if hasattr(entry, "content"):
        html = entry.content[0].value
    elif hasattr(entry, "summary"):
        html = entry.summary
    soup = BeautifulSoup(html, "lxml")
    lines = [p.get_text(" ", strip=True) for p in soup.find_all(["p", "li"])]
    lines = [l for l in lines if not is_junk_line(l)]
    return "<br><br>".join(lines) if lines else soup.get_text(" ", strip=True)[:400]

def extract_image(entry):
    if hasattr(entry, "media_content") and entry.media_content:
        return entry.media_content[0].get("url", "")
    if hasattr(entry, "enclosures") and entry.enclosures:
        return entry.enclosures[0].get("url", "")
    try:
        r = safe_get(entry.link, timeout=6)
        if r:
            soup = BeautifulSoup(r.content, "lxml")
            og = soup.find("meta", property="og:image")
            if og and og.get("content"):
                return og["content"]
    except Exception:
        pass
    return ""

def resize_img(url):
    if not url:
        return ""
    return f"https://wsrv.nl/?url={requests.utils.quote(url, safe='')}&w=600&q=75"

def fetch_feed(name_url):
    name, url = name_url
    r = safe_get(url)
    if not r:
        return []
    feed = feedparser.parse(r.content)
    results = []
    for entry in feed.entries[:8]:
        img = resize_img(extract_image(entry))
        content = extract_content(entry)
        results.append((name, entry, img, content))
    return results

def build_html(all_items):
    now = datetime.now(pytz.utc)
    date_str = now.strftime("%A, %B %d %Y - %H:%M UTC")

    cards = ""
    for name, entry, img, content in all_items:
        img_html = f"<div class='card-img'><img src='{img}' loading='lazy'></div>" if img else ""
        cards += f"""
        <div class='card'>
            {img_html}
            <div class='card-body'>
                <span class='source'>{name}</span>
                <h3><a href='{entry.link}' target='_blank'>{entry.title}</a></h3>
                <div class='content'>{content}</div>
            </div>
        </div>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>World News</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: 'Segoe UI', sans-serif; background: #0f0f0f; color: #e0e0e0;
         line-height: 1.7; }}
  header {{ background: #1a1a2e; padding: 16px 24px; display: flex;
            justify-content: space-between; align-items: center; }}
  header h1 {{ font-size: 1.4rem; color: #fff; }}
  .meta {{ font-size: 0.85rem; color: #aaa; }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(320px,1fr));
           gap: 20px; padding: 24px; }}
  .card {{ background: #1e1e2e; border-radius: 12px; overflow: hidden; }}
  .card-img img {{ width: 100%; height: 200px; object-fit: cover; }}
  .card-body {{ padding: 16px; }}
  .source {{ background: #457b9d; color: #fff; font-size: 0.75rem;
             padding: 2px 8px; border-radius: 4px; }}
  h3 {{ margin: 10px 0 8px; font-size: 1rem; }}
  h3 a {{ color: #e0e0e0; text-decoration: none; }}
  h3 a:hover {{ color: #f0a500; }}
  .content {{ font-size: 0.88rem; color: #bbb; max-height: 160px; overflow: hidden; }}
  footer {{ text-align: center; padding: 16px; color: #555; font-size: 0.8rem; }}
</style>
</head>
<body>
<header>
  <h1>🌍 World News</h1>
  <span class="meta">{date_str}</span>
</header>
<div class="grid">{cards}</div>
<footer>Auto-updated · {date_str}</footer>
</body>
</html>"""

def main():
    with ThreadPoolExecutor(max_workers=5) as ex:
        results = list(ex.map(fetch_feed, FEEDS))
    all_items = [item for sublist in results for item in sublist]
    html = build_html(all_items)
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Done. {len(all_items)} items.")

if __name__ == "__main__":
    main()
