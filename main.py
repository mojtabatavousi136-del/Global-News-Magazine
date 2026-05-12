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
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'}

    try:
        time.sleep(1)
        response = requests.get(entry.link, headers=headers, timeout=20)
        soup = BeautifulSoup(response.content, 'html.parser')

        # --- ۱. استخراج و اصلاح عکس (فوق هوشمند) ---
        img_tag = soup.find("meta", property="og:image") or soup.find("meta", name="twitter:image")
        if img_tag:
            image_url = img_tag.get("content")

        # اصلاح اختصاصی برای ناسا (حذف پسوندهای اضافه بعد از .jpeg یا .jpg)
        if source_name == "NASA News" and image_url:
            image_url = re.sub(r'(\.jp[e]?g)/.*$', r'\1', image_url)

        # اصلاح اختصاصی برای گاردین (بالا بردن کیفیت)
        if source_name == "The Guardian" and image_url:
            image_url = image_url.split('?')[0] # حذف پارامترهای فشرده‌سازی

        # رفع مشکل نمایش نیویورک تایمز در گیت‌هاب (استفاده از سیستم Image Proxy)
        if source_name == "NY Times" and image_url:
            image_url = f"https://wsrv.nl/?url={image_url}"

        # بک‌آپ از فید اگر عکسی پیدا نشد
        if not image_url:
            if 'media_content' in entry: image_url = entry.media_content[0]['url']
            elif 'links' in entry:
                for link in entry.links:
                    if 'image' in link.get('type', ''): image_url = link.get('href')

        # --- ۲. استخراج متن ---
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
            for junk in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'figcaption']):
                junk.decompose()
            selectors = ['div.article__content', 'section[name="articleBody"]', 'div.wysiwyg', 'article']
            for s in selectors:
                area = soup.select_one(s)
                if area:
                    paragraphs = area.find_all('p')
                    text_parts = [p.get_text().strip() for p in paragraphs if len(p.get_text().strip()) > 70]
                    if text_parts:
                        full_text = '\n\n'.join(text_parts[:10])
                        break
    except: pass

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
            if img:
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
