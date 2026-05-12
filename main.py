import feedparser
import requests
from bs4 import BeautifulSoup
import re
import time
import json
from datetime import datetime

def get_best_image(entry, soup, source_name):
    """استخراج بهترین و سازگارترین عکس برای گیت‌هاب"""
    image_url = None
    
    # اولویت ۱: جستجو در فید RSS (مطمئن‌ترین راه برای گاردین و ناسا)
    if 'media_content' in entry and len(entry.media_content) > 0:
        image_url = entry.media_content[0]['url']
    elif 'links' in entry:
        for link in entry.links:
            if 'image' in link.get('type', '') or '.jpg' in link.get('href', ''):
                image_url = link.get('href')
                break

    # اولویت ۲: اگر در فید نبود، جستجو در متاتگ‌های HTML
    if not image_url and soup:
        # برای نیویورک تایمز و بقیه، متاتگ og:image معمولاً بهترین است
        tag = soup.find("meta", property="og:image") or soup.find("meta", name="twitter:image")
        if tag:
            image_url = tag.get("content")

    # اصلاحات نهایی برای سازگاری با گیت‌هاب
    if image_url:
        if image_url.startswith('//'):
            image_url = 'https:' + image_url
        
        # برای گاردین و NYT پارامترها را حذف نمی‌کنیم، اما اگر آدرس شامل فضا باشد اصلاح می‌کنیم
        image_url = image_url.replace(' ', '%20')
        
    return image_url

def get_ultra_content(entry, source_name):
    full_text = None
    image_url = None
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }

    try:
        time.sleep(1) # وقفه کوتاه
        response = requests.get(entry.link, headers=headers, timeout=20)
        soup = None
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # ۱. استخراج عکس با متد جدید
            image_url = get_best_image(entry, soup, source_name)

            # ۲. استخراج متن (متد قبلی که برای الجزیره خوب عمل می‌کرد)
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
                for junk in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
                    junk.decompose()
                selectors = ['div.article__content', 'section[name="articleBody"]', 'div.wysiwyg', 'article']
                for selector in selectors:
                    area = soup.select_one(selector)
                    if area:
                        paragraphs = area.find_all('p')
                        text_parts = [p.get_text().strip() for p in paragraphs if len(p.get_text().strip()) > 70]
                        if text_parts:
                            full_text = '\n\n'.join(text_parts[:10])
                            break
    except:
        # اگر لود نشد، حداقل عکس را از فید بگیر
        image_url = get_best_image(entry, None, source_name)

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
        print(f"Processing {name}...")
        feed = feedparser.parse(url)
        markdown += f"## {name}\n"
        
        for entry in feed.entries[:5]:
            img, content = get_ultra_content(entry, name)
            markdown += f"### 📰 {entry.title}\n"
            
            if img:
                # استفاده از تگ img استاندارد برای اطمینان از نمایش
                markdown += f"<img src='{img}' width='100%' style='border-radius:15px;' alt='News Image'>\n\n"
            
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
