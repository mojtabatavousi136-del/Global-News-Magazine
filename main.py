import feedparser
import requests
from bs4 import BeautifulSoup
import re
import jdatetime
import pytz
from datetime import datetime
from urllib.parse import urljoin

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'}

def get_tgju_price(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(response.content, 'html.parser')
        price_span = soup.select_one('span[data-col="info.last_trade.pc"]')
        return price_span.get_text().strip() if price_span else "---"
    except: return "---"

def get_full_content(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=20)
        soup = BeautifulSoup(response.text, 'html.parser')
        img_meta = soup.find("meta", property="og:image") or soup.find("meta", name="twitter:image")
        img_url = urljoin(url, img_meta.get('content')) if img_meta else None
        
        # تلاش برای استخراج متن کامل از تگ‌های اصلی خبر
        content_area = soup.select_one('article, section[class*="body"], div[class*="content"]')
        if content_area:
            p_tags = content_area.find_all(['p', 'h2'])
            text = "\n\n".join([p.get_text().strip() for p in p_tags if len(p.get_text()) > 40])
            return img_url, text
        return img_url, ""
    except: return None, ""

def main():
    sources = {
        "Al Jazeera": "https://www.aljazeera.com/xml/rss/all.xml",
        "BBC World": "https://feeds.bbci.co.uk/news/world/rss.xml",
        "NASA News": "https://www.nasa.gov/news-release/feed/"
    }
    
    gold = get_tgju_price("https://www.tgju.org/profile/geram18")
    dollar = get_tgju_price("https://www.tgju.org/profile/price_dollar_rl")
    tehran_tz = pytz.timezone('Asia/Tehran')
    now = datetime.now(tehran_tz)
    jalali_date = jdatetime.datetime.fromgregorian(datetime=now).strftime('%Y/%m/%d')
    update_time = now.strftime('%H:%M')

    news_cards = ""
    for name, url in sources.items():
        feed = feedparser.parse(url)
        news_cards += f"<h2 class='source-title'>🌍 {name}</h2>"
        for entry in feed.entries[:5]:
            img, content = get_full_content(entry.link)
            if not content: content = entry.get('summary', '')[:300]
            formatted_content = content.replace('\n\n', '<br><br>')
            
            news_cards += f"""
            <div class='card'>
                {f"<div class='card-img-wrap'><img src='{img}'></div>" if img else ""}
                <div class='card-content'>
                    <h3>{entry.title}</h3>
                    <div class='full-text'>{formatted_content}</div>
                    <a href='{entry.link}' target='_blank' class='read-btn'>Read on {name} →</a>
                </div>
            </div>"""

    full_html = f"""
    <!DOCTYPE html>
    <html lang="en" dir="ltr">
    <head>
        <meta charset="UTF-8">
        <style>
            :root {{ --bg: #0d1117; --card: #161b22; --text: #c9d1d9; --accent: #58a6ff; }}
            body {{ background: var(--bg); color: var(--text); font-family: 'Segoe UI', sans-serif; margin: 0; }}
            .header {{ background: linear-gradient(135deg, #1f6feb, #111418); padding: 30px; text-align: center; border-bottom: 2px solid #30363d; }}
            .stats-container {{ display: flex; flex-direction: column; align-items: center; gap: 10px; margin-top: 15px; }}
            .stats-row {{ display: flex; gap: 10px; flex-wrap: wrap; justify-content: center; }}
            .stat-box {{ background: rgba(0,0,0,0.3); padding: 5px 15px; border-radius: 20px; border: 1px solid var(--accent); font-size: 0.9em; }}
            .price-box {{ border-color: #f1c40f; color: #f1c40f; }}
            .switch-btn {{ background: #c0392b; color: white; text-decoration: none; padding: 6px 18px; border-radius: 20px; font-weight: bold; border: 1px solid rgba(255,255,255,0.2); }}
            .container {{ width: 90%; max-width: 800px; margin: 20px auto; }}
            .source-title {{ color: var(--accent); border-left: 5px solid var(--accent); padding-left: 15px; margin-top: 40px; }}
            .card {{ background: var(--card); border: 1px solid #30363d; border-radius: 12px; margin-bottom: 30px; overflow: hidden; }}
            .card-img-wrap img {{ width: 100%; max-height: 400px; object-fit: cover; }}
            .card-content {{ padding: 20px; }}
            .full-text {{ text-align: justify; line-height: 1.6; color: #b1bac4; }}
            .read-btn {{ display: inline-block; margin-top: 15px; color: var(--accent); text-decoration: none; border: 1px solid #30363d; padding: 8px 15px; border-radius: 6px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🌐 MAHOOR GLOBAL</h1>
            <div class="stats-container">
                <div class="stats-row">
                    <a href="index.html" class="switch-btn">🇮🇷 Persian Version (فارسی)</a>
                    <div class="stat-box">📅 {jalali_date}</div>
                    <div class="stat-box">⏰ {update_time} (Tehran)</div>
                </div>
                <div class="stats-row">
                    <div class="stat-box price-box">🟡 Gold: {gold}</div>
                    <div class="stat-box price-box">💵 Dollar: {dollar}</div>
                </div>
            </div>
        </div>
        <div class="container">{news_cards}</div>
    </body>
    </html>"""
    with open("global.html", "w", encoding="utf-8") as f: f.write(full_html)

if __name__ == "__main__": main()
