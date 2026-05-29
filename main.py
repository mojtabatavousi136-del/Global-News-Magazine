import feedparser
import requests
from bs4 import BeautifulSoup
import re
import jdatetime
import pytz
from datetime import datetime
from urllib.parse import urljoin
import json

# تنظیمات هدر
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
}

def get_tgju_price(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(response.content, 'html.parser')
        price_span = soup.select_one('span[data-col="info.last_trade.pc"]') or \
                     soup.select_one('.value') or \
                     soup.select_one('.price')
        return price_span.get_text().strip() if price_span else "---"
    except Exception:
        return "---"

def clean_english_content(text_list):
    """پاکسازی متون انگلیسی از عبارات زائد"""
    if not text_list: return ""
    junk_patterns = [
        r'Read more', r'Related Topics', r'Follow us on', r'Share this story',
        r'Sign up for', r'Advertisement', r'Image copyright', r'Getty Images',
        r'Reporting by', r'Editing by', r'Writing by', r'All rights reserved'
    ]
    cleaned = []
    for line in text_list:
        line = line.strip()
        if len(line) < 40: continue
        if any(re.search(p, line, re.IGNORECASE) for p in junk_patterns): continue
        if line not in cleaned: cleaned.append(line)
    return "\n\n".join(cleaned)

def get_full_content(url, source_name):
    try:
        response = requests.get(url, headers=HEADERS, timeout=20)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 1. استخراج تصویر
        img_url = None
        img_meta = soup.find("meta", property="og:image") or soup.find("meta", name="twitter:image")
        if img_meta:
            img_url = img_meta.get('content')
            if img_url:
                img_url = urljoin(url, img_url)
                img_url = f"https://wsrv.nl/?url={img_url}&w=800&q=80"

        # 2. استخراج متن (ترکیب JSON-LD و Selectors)
        full_text = ""
        # تلاش اول: JSON-LD
        json_scripts = soup.find_all('script', type='application/ld+json')
        for script in json_scripts:
            try:
                data = json.loads(script.string)
                if isinstance(data, list): data = data[0]
                content = data.get('articleBody')
                if content and len(content) > 300:
                    full_text = content
                    break
            except: continue

        # تلاش دوم: سلکتورهای CSS اگر متن پیدا نشد
        if not full_text:
            selectors = ['article', '.article__content', 'section[name="articleBody"]', '.story-body__inner', '.vjs-body']
            for s in selectors:
                area = soup.select_one(s)
                if area:
                    p_tags = area.find_all(['p', 'h2', 'h3'])
                    paragraphs = [p.get_text() for p in p_tags]
                    full_text = clean_english_content(paragraphs)
                    if len(full_text) > 200: break
        
        return img_url, full_text
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None, ""

def main():
    sources = {
        "Al Jazeera": "https://www.aljazeera.com/xml/rss/all.xml",
        "BBC World": "https://feeds.bbci.co.uk/news/world/rss.xml",
        "The Guardian": "https://www.theguardian.com/world/rss",
        "NY Times": "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
        "NASA News": "https://www.nasa.gov/news-release/feed/"
    }

    # دریافت قیمت‌ها برای هدر (طبق درخواست شما)
    gold = get_tgju_price("https://www.tgju.org/profile/geram18")
    dollar = get_tgju_price("https://www.tgju.org/profile/price_dollar_rl")
    
    # زمان‌بندی
    tehran_tz = pytz.timezone('Asia/Tehran')
    now = datetime.now(tehran_tz)
    jalali_date = jdatetime.datetime.fromgregorian(datetime=now).strftime('%Y/%m/%d')
    update_time = now.strftime('%H:%M')

    news_html_cards = ""
    
    for name, url in sources.items():
        print(f"Processing: {name}")
        feed = feedparser.parse(url)
        news_html_cards += f"<h2 class='source-title'>🌍 {name}</h2>"
        
        count = 0
        for entry in feed.entries:
            if count >= 5: break
            
            img, content = get_full_content(entry.link, name)
            if not content or len(content) < 200:
                content = re.sub('<[^<]+?>', '', entry.get('summary', ''))[:300] + "..."
            
            formatted_content = content.replace('\n\n', '<br><br>')
            
            news_html_cards += f"""
            <div class='card'>
                {f"<div class='card-img-wrap'><img src='{img}' loading='lazy'></div>" if img else ""}
                <div class='card-content'>
                    <h3>{entry.title}</h3>
                    <div class='full-text'>{formatted_content}</div>
                    <a href='{entry.link}' target='_blank' class='read-btn'>Read Full Story on {name} →</a>
                </div>
            </div>
            """
            count += 1

    full_html = f"""
    <!DOCTYPE html>
    <html lang="en" dir="ltr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Mahoor Global Magazine</title>
        <style>
            :root {{ --bg: #0d1117; --card-bg: #161b22; --text: #c9d1d9; --accent: #58a6ff; }}
            body {{ background-color: var(--bg); color: var(--text); font-family: 'Segoe UI', Tahoma, sans-serif; margin: 0; padding: 0; line-height: 1.6; }}
            .header {{ background: linear-gradient(135deg, #1f6feb 0%, #111418 100%); padding: 40px 20px; text-align: center; border-bottom: 2px solid #30363d; }}
            .stats-container {{ display: flex; flex-direction: column; align-items: center; gap: 12px; margin-top: 20px; }}
            .stats-row {{ display: flex; justify-content: center; gap: 10px; flex-wrap: wrap; }}
            .stat-box {{ background: rgba(0,0,0,0.3); padding: 6px 18px; border-radius: 20px; font-size: 0.9em; border: 1px solid var(--accent); color: #fff; }}
            .price-box {{ border-color: #f1c40f; color: #f1c40f; }}
            .container {{ width: 95%; max-width: 900px; margin: 20px auto; }}
            .source-title {{ color: var(--accent); border-left: 5px solid var(--accent); padding-left: 15px; margin: 40px 0 20px; text-transform: uppercase; letter-spacing: 1px; }}
            .card {{ background: var(--card-bg); border: 1px solid #30363d; border-radius: 12px; overflow: hidden; display: flex; flex-direction: column; margin-bottom: 40px; box-shadow: 0 4px 15px rgba(0,0,0,0.3); }}
            .card-img-wrap {{ width: 100%; max-height: 450px; overflow: hidden; }}
            .card img {{ width: 100%; height: 100%; object-fit: cover; transition: 0.3s; }}
            .card:hover img {{ transform: scale(1.02); }}
            .card-content {{ padding: 25px; }}
            .card h3 {{ margin-top: 0; color: #f0f6fc; font-size: 1.5em; line-height: 1.3; }}
            .full-text {{ font-size: 1.05em; color: #b1bac4; text-align: justify; }}
            .read-btn {{ display: inline-block; margin-top: 20px; color: var(--accent); text-decoration: none; font-weight: bold; border: 1px solid #30363d; padding: 10px 20px; border-radius: 6px; }}
            .read-btn:hover {{ background: var(--accent); color: white; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🌐 MAHOOR GLOBAL MAGAZINE</h1>
            <div class="stats-container">
                <div class="stats-row">
                    <div class="stat-box">📅 {jalali_date}</div>
                    <div class="stat-box">⏰ Last Update: {update_time} (Tehran)</div>
                </div>
                <div class="stats-row">
                    <div class="stat-box price-box">🟡 Gold: {gold}</div>
                    <div class="stat-box price-box">💵 Dollar: {dollar}</div>
                </div>
            </div>
        </div>
        <div class="container">{news_html_cards}</div>
    </body>
    </html>
    """
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(full_html)

if __name__ == "__main__":
    main()
