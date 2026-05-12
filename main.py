import feedparser
import requests
from bs4 import BeautifulSoup
import re
import time
from datetime import datetime

def get_full_content(entry, source_name):
    image_url = None
    full_text = None
    
    # 1. استخراج تصویر
    if 'media_content' in entry:
        image_url = entry.media_content[0]['url']
    elif 'links' in entry:
        for link in entry.links:
            if 'image' in link.get('type', ''):
                image_url = link.href
                break

    # 2. تلاش برای استخراج متن
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9'
        }
        
        # برای الجزیره ابتدا تلاش می‌کنیم اگر نشد از متد کمکی استفاده می‌کنیم
        response = requests.get(entry.link, headers=headers, timeout=15)
        
        # اگر بلاک شدیم (کد 403)، از خلاصه RSS استفاده می‌کنیم تا خالی نماند
        if response.status_code != 200:
            return image_url, None

        soup = BeautifulSoup(response.content, 'html.parser')
        
        # پیدا کردن عکس در صورت نبودن در RSS
        if not image_url:
            img_tag = soup.find("meta", property="og:image")
            if img_tag: image_url = img_tag["content"]

        # تمیز کردن صفحه
        for junk in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'form', 'button']):
            junk.decompose()

        # یافتن بدنه اصلی خبر (مخصوص الجزیره و بقیه)
        # الجزیره از کلاس 'wysiwyg' یا 'article-body' استفاده می‌کند
        content_div = soup.find('div', class_=re.compile(r'wysiwyg|article-body|all-content|main-content'))
        if not content_div:
            content_div = soup.find('article')

        if content_div:
            paragraphs = content_div.find_all('p')
            text_parts = []
            for p in paragraphs:
                txt = p.get_text().strip()
                if len(txt) > 60: # پاراگراف‌های واقعی
                    text_parts.append(txt)
            
            if text_parts:
                full_text = '\n\n'.join(text_parts[:12]) # نمایش 12 پاراگراف

    except Exception as e:
        print(f"Scraping failed for {source_name}: {e}")
        
    return image_url, full_text

def main():
    sources = {
        "Al Jazeera": "https://www.aljazeera.com/xml/rss/all.xml",
        "BBC World": "https://feeds.bbci.co.uk/news/world/rss.xml",
        "The Guardian": "https://www.theguardian.com/world/rss",
        "NY Times": "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
        "Associated Press": "https://newsatme.com/en/category/world/feed/",
        "NASA News": "https://www.nasa.gov/news-release/feed/",
        "TMZ": "https://www.tmz.com/rss.xml",
        "The Verge": "https://www.theverge.com/rss/index.xml"
    }

    now = datetime.now()
    now_str = now.strftime('%Y/%m/%d - %H:%M')
    
    # ساختار هدر و منوی ناوبری
    markdown = f"<div align=\"center\">\n\n# 📰 MAHOOR WORLD PREMIER NEWS\n\n**📅 Update:** `{now_str}`\n\n---\n\n### 📌 QUICK NAVIGATION\n"
    
    nav_links = []
    for name in sources.keys():
        anchor = name.lower().replace(" ", "-")
        nav_links.append(f"[{name}](#{anchor})")
    
    markdown += " | ".join(nav_links) + "\n\n--- \n</div>\n\n"

    for name, url in sources.items():
        print(f"Processing: {name}")
        feed = feedparser.parse(url)
        
        # آیدی هدر برای کارکردن منوی ناوبری
        markdown += f"## {name}\n"
        
        if not feed.entries:
            markdown += "> ⚠️ *Currently unavailable.*\n\n"
            continue
            
        for entry in feed.entries[:5]:
            markdown += f"### 📰 {entry.title}\n"
            
            img, content = get_full_content(entry, name)
            
            if img:
                markdown += f"<img src='{img}' width='100%' style='border-radius:15px;'>\n\n"
            
            markdown += "<div align='justify'>\n<font size='4'>\n\n"
            
            if content:
                markdown += f"{content}\n\n"
            else:
                # جایگزین در صورت شکست استخراج متن: استفاده از خلاصه فید RSS
                summary = re.sub('<[^<]+?>', '', entry.get('summary', ''))
                if not summary: summary = entry.get('description', 'No description available.')
                markdown += f"*{summary}*\n\n"
            
            markdown += "</font>\n</div>\n\n"
            markdown += f" [🔗 Read Full Story on {name}]({entry.link})\n\n"
            markdown += "<p align='center'>━━━━━━━━━━━━━━━━━━━━━━━━━</p>\n\n"
        
        markdown += "\n---\n"

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(markdown)

if __name__ == "__main__":
    main()
