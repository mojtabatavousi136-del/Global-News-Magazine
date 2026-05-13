import feedparser
import requests
from bs4 import BeautifulSoup
import re
import time
import json
from datetime import datetime
import pytz  # اضافه شد برای ساعت تهران

def get_ultra_content(entry, source_name):
    image_url = None
    full_text = None
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'}

    try:
        time.sleep(1)
        response = requests.get(entry.link, headers=headers, timeout=20)
        soup = BeautifulSoup(response.content, 'html.parser')

        # 1. Image extraction from meta tags
        img_tag = soup.find("meta", property="og:image") or soup.find("meta", name="twitter:image")
        if img_tag:
            image_url = img_tag.get("content")

        # --- Specific Fixes for English Sources ---
        if image_url:
            if source_name == "NASA News":
                match = re.search(r'(^.*?\.(jpg|jpeg|png))', image_url, re.IGNORECASE)
                if match: image_url = match.group(1)
            elif source_name == "The Guardian":
                image_url = re.sub(r'\?width=\d+&quality=\d+', '', image_url)
                if '?' in image_url and 'static.guim.co.uk' in image_url:
                    image_url = image_url.split('?')[0]
            elif source_name == "NY Times":
                image_url = f"https://wsrv.nl/?url={image_url}"

        if not image_url:
            if 'media_content' in entry: image_url = entry.media_content[0]['url']
            elif 'links' in entry:
                for link in entry.links:
                    if 'image' in link.get('type', ''): image_url = link.get('href')

        # 2. Text extraction
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
        "TMZ": "https://www.tmz.com/rss.xml",
        "NY Times": "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
        "NASA News": "https://www.nasa.gov/news-release/feed/",
    }

    # لینک‌های پروژه
    repo_url = "https://github.com/mojtabatavousi136-del/my-news-feed"
    
    # --- تنظیم زمان به وقت تهران ---
    tehran_tz = pytz.timezone('Asia/Tehran')
    now_tehran = datetime.now(tehran_tz)
    now_str = now_tehran.strftime('%Y/%m/%d - %H:%M')

    markdown = f"""<div align="center">

# 📰 MAHOOR WORLD PREMIER NEWS

**  Powered by: [Mahoor](https://github.com/mojtabatavousi136-del)**

**📅 Update (Tehran Time):** `{now_str}`

---

[**🇮🇷 مشاهده مجله خبری فارسی (Persian Version)**]({repo_url})

---

### 📌 QUICK NAVIGATION
"""
    nav_links = [f"[{name}](#{name.lower().replace(' ', '-')})" for name in sources.keys()]
    markdown += " | ".join(nav_links) + "\n\n--- \n</div>\n\n"

    for name, url in sources.items():
        feed = feedparser.parse(url)
        anchor = name.lower().replace(' ', '-')
        markdown += f"## <a name='{anchor}'></a>🌍 {name}\n"
        for entry in feed.entries[:5]:
            img, content = get_ultra_content(entry, name)
            markdown += f"### 📰 {entry.title}\n"
            
            if img:
                markdown += f"<img src='{img}' width='100%' style='border-radius:15px;' alt='{name} Image'>\n\n"
            
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

    # اضافه کردن بخش دعوت به استاره در پایان
    markdown += f"""
<div align="center">

### 🌟 Like this project?
If you find this auto-updating news feed useful, please give it a **Star**!

[⭐ Support by Starring Here]({repo_url})

</div>
"""

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(markdown)

if __name__ == "__main__":
    main()
