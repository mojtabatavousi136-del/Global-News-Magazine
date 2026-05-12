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
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://www.google.com/',
        'DNT': '1'
    }

    try:
        time.sleep(2) # وقفه برای جلوگیری از حساسیت سرور
        response = requests.get(entry.link, headers=headers, timeout=25)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # ۱. استخراج عکس با کیفیت بالا (مخصوص گاردین و بقیه)
            img_meta = soup.find("meta", property="og:image") or soup.find("meta", name="twitter:image")
            if img_meta:
                image_url = img_meta.get("content")

            # ۲. استخراج متن از داده‌های ساختاریافته (JSON-LD) - لایه امنیتی جدید
            # این بخش متن را از جایی می‌کشد که معمولاً مسدود نمی‌شود
            json_scripts = soup.find_all('script', type='application/ld+json')
            for script in json_scripts:
                try:
                    data = json.loads(script.string)
                    if isinstance(data, dict):
                        # جستجو در ساختارهای مختلف JSON خبری
                        content = data.get('articleBody') or data.get('description')
                        if content and len(content) > 300:
                            full_text = content
                            break
                except: continue

            # ۳. اگر روش بالا جواب نداد، از روش استخراج مستقیم با کلاس‌های جدید استفاده کن
            if not full_text:
                # پاکسازی هوشمند
                for junk in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'form', 'button', 'figcaption']):
                    junk.decompose()
                
                # کلاس‌های بسیار خاص برای الجزیره و نیویورک تایمز
                selectors = [
                    'div.article__content', 'div.wysiwyg--all-content', # Al Jazeera
                    'section[name="articleBody"]', 'div.StoryBodyCompanionColumn', # NYT
                    'div.article-body-commercial-selector', # Guardian
                    'article', 'main'
                ]
                
                for selector in selectors:
                    content_area = soup.select_one(selector)
                    if content_area:
                        paragraphs = content_area.find_all('p')
                        text_parts = [p.get_text().strip() for p in paragraphs if len(p.get_text().strip()) > 70]
                        if text_parts:
                            full_text = '\n\n'.join(text_parts[:15])
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

    now = datetime.now()
    markdown = f"<div align=\"center\">\n\n# 📰 MAHOOR WORLD PREMIER NEWS\n\n**📅 Update:** `{now.strftime('%Y/%m/%d - %H:%M')}`\n\n---\n\n### 📌 QUICK NAVIGATION\n"
    nav_links = [f"[{name}](#{name.lower().replace(' ', '-')})" for name in sources.keys()]
    markdown += " | ".join(nav_links) + "\n\n--- \n</div>\n\n"

    for name, url in sources.items():
        print(f"Processing {name}...")
        feed = feedparser.parse(url)
        markdown += f"## {name}\n"
        
        for entry in feed.entries[:5]:
            img, content = get_ultra_content(entry, name)
            
            markdown += f"### 📰 {entry.title}\n"
            
            # نمایش عکس با اطمینان از کیفیت
            if img:
                if img.startswith('//'): img = 'https:' + img
                markdown += f"<img src='{img}' width='100%' style='border-radius:15px;'>\n\n"
            
            markdown += "<div align='justify'>\n<font size='4'>\n\n"
            
            if content and len(content) > 100:
                # پاکسازی متن از کاراکترهای اضافی
                clean_text = content.replace('Advertisement', '').strip()
                markdown += f"{clean_text}\n\n"
            else:
                # آخرین تلاش: استفاده از دیسکریپشن فید بدون زدن برچسب محدودیت
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
