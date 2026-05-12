import feedparser
import requests
from bs4 import BeautifulSoup
import re
import time
import json
from datetime import datetime

def get_ultra_content(entry, source_name):
    image_url = None
    full_text = None
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
    }

    try:
        time.sleep(1.5)
        response = requests.get(entry.link, headers=headers, timeout=25)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # --- استخراج فوق حرفه‌ای عکس ---
            # اولویت ۱: جستجوی متاتگ‌های اصلی
            img_tag = soup.find("meta", property="og:image") or \
                      soup.find("meta", name="twitter:image")
            
            if img_tag:
                image_url = img_tag.get("content")

            # اولویت ۲: اصلاح اختصاصی برای NY Times (اگر عکس پیدا نشد یا کوچک بود)
            if source_name == "NY Times":
                # پیدا کردن بزرگترین عکس در ساختار اسکریپت NYT
                scripts = soup.find_all('script')
                for s in scripts:
                    if s.string and 'url' in s.string and '.jpg' in s.string:
                        match = re.search(r'(https://static01.nyt.com/images/[^"\? ]+)', s.string)
                        if match:
                            image_url = match.group(1)
                            break

            # اولویت ۳: اصلاح برای NASA (برداشتن لینک مستقیم از فید اگر در صفحه نبود)
            if not image_url and source_name == "NASA News":
                if 'links' in entry:
                    for link in entry.links:
                        if 'image' in link.get('type', '') or '.jpg' in link.get('href', ''):
                            image_url = link.get('href')

            # --- استخراج متن ---
            json_scripts = soup.find_all('script', type='application/ld+json')
            for script in json_scripts:
                try:
                    data = json.loads(script.string)
                    if isinstance(data, list): data = data[0]
                    content = data.get('articleBody') or data.get('description')
                    if content and len(content) > 300:
                        full_text = content
                        break
                except: continue

            if not full_text:
                for junk in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'form', 'button', 'figcaption']):
                    junk.decompose()
                selectors = ['div.article__content', 'section[name="articleBody"]', 'article', 'main']
                for selector in selectors:
                    content_area = soup.select_one(selector)
                    if content_area:
                        paragraphs = content_area.find_all('p')
                        text_parts = [p.get_text().strip() for p in paragraphs if len(p.get_text().strip()) > 70]
                        if text_parts:
                            full_text = '\n\n'.join(text_parts[:12])
                            break

    except Exception as e:
        print(f"Error: {e}")
        
    return image_url, full_text

def main():
    sources = {
        "Al Jazeera": "https://www.aljazeera.com/xml/rss/all.xml",
        "BBC World": "https://feeds.bbci.co.uk/news/world/rss.xml",
        "The Guardian": "https://www.theguardian.com/world/rss",
        "NY Times": "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
        "NASA News": "https://www.nasa.gov/news-release/feed/",
        "TMZ": "https://www.tmz.com/rss.xml"
    }

    now_str = datetime.now().strftime('%Y/%m/%d - %H:%M')
    markdown = f"<div align=\"center\">\n\n# 📰 MAHOOR WORLD PREMIER NEWS\n\n**📅 Update:** `{now_str}`\n\n---\n\n### 📌 QUICK NAVIGATION\n"
    nav_links = [f"[{name}](#{name.lower().replace(' ', '-')})" for name in sources.keys()]
    markdown += " | ".join(nav_links) + "\n\n--- \n</div>\n\n"

    for name, url in sources.items():
        feed = feedparser.parse(url)
        markdown += f"## {name}\n"
        
        for entry in feed.entries[:5]:
            img, content = get_ultra_content(entry, name)
            markdown += f"### 📰 {entry.title}\n"
            
            # اصلاح نهایی لینک عکس قبل از قرارگیری در Markdown
            if img:
                if img.startswith('//'): img = 'https:' + img
                # حذف پارامترهای محدودکننده اندازه در NYT برای نمایش با کیفیت
                img = img.split('?')[0] 
                markdown += f"<img src='{img}' width='100%' style='border-radius:15px;'>\n\n"
            
            markdown += "<div align='justify'>\n<font size='4'>\n\n"
            if content and len(content) > 150:
                markdown += f"{content}\n\n"
            else:
                summary = re.sub('<[^<]+?>', '', entry.get('summary', ''))
                markdown += f"{summary}\n\n"
            
            markdown += "</font>\n</div>\n\n"
            markdown += f" [🔗 Read Full Story on {name}]({entry.link})\n\n"
            markdown += "<p align='center'>━━━━━━━━━━━━━━━━━━━━━━━━━</p>\n\n"
        markdown += "\n---\n"

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(markdown)

if __name__ == "__main__":
    main()
