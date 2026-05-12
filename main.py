import feedparser
import requests
from bs4 import BeautifulSoup
import re
import time
from datetime import datetime

def get_full_content(entry, source_name):
    image_url = None
    full_text = None
    
    # 1. استخراج عکس (فید یا متاتگ)
    if 'media_content' in entry:
        image_url = entry.media_content[0]['url']
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.google.com/'
        }
        
        # وقفه برای جلوگیری از بلاک شدن
        if source_name in ["Al Jazeera", "NY Times"]:
            time.sleep(2)

        response = requests.get(entry.link, headers=headers, timeout=25)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # استخراج عکس در صورت نبودن در فید
            if not image_url:
                img_tag = soup.find("meta", property="og:image") or soup.find("meta", name="twitter:image")
                if img_tag:
                    image_url = img_tag["content"]

            # پاکسازی المان‌های مزاحم
            for junk in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'form', 'button', 'ul', 'ol']):
                junk.decompose()

            # --- موتور هوشمند تشخیص متن ---
            # ابتدا دنبال تگ‌های استاندارد مقاله می‌گردیم
            content_area = soup.find('article') or soup.find('main') or soup.find('div', class_=re.compile(r'article-body|wysiwyg|story-content|post-content'))
            
            if not content_area:
                content_area = soup # اگر پیدا نشد، کل صفحه را بگرد
            
            # تمام پاراگراف‌ها را پیدا کن
            paragraphs = content_area.find_all('p')
            
            text_parts = []
            for p in paragraphs:
                txt = p.get_text().strip()
                # فیلتر کردن متن‌های خیلی کوتاه (زیر 70 کاراکتر) یا متن‌های حاوی کلمات تبلیغاتی
                if len(txt) > 70 and not any(x in txt.lower() for x in ['subscribe', 'follow us', 'sign up', 'copyright', 'advertisement']):
                    if txt not in text_parts:
                        text_parts.append(txt)
            
            if text_parts:
                # برای الجزیره و نیویورک تایمز سقف پاراگراف را بالا بردیم
                limit = 15 if source_name in ["Al Jazeera", "NY Times"] else 10
                full_text = '\n\n'.join(text_parts[:limit])
                
    except Exception as e:
        print(f"Error extracting {source_name}: {e}")
        
    return image_url, full_text

def main():
    # منابع نهایی شده بر اساس درخواست شما
    sources = {
        "Al Jazeera": "https://www.aljazeera.com/xml/rss/all.xml",
        "BBC World": "https://feeds.bbci.co.uk/news/world/rss.xml",
        "The Guardian": "https://www.theguardian.com/world/rss",
        "NY Times": "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
        "NASA News": "https://www.nasa.gov/news-release/feed/",
        "TMZ": "https://www.tmz.com/rss.xml"
    }

    now = datetime.now()
    now_str = now.strftime('%Y/%m/%d - %H:%M')
    
    # ساخت هدر و منوی ناوبری اصلاح شده برای گیت‌هاب
    markdown = f"<div align=\"center\">\n\n# 📰 MAHOOR WORLD PREMIER NEWS\n\n**📅 Update:** `{now_str}`\n\n---\n\n### 📌 QUICK NAVIGATION\n"
    
    nav_links = [f"[{name}](#{name.lower().replace(' ', '-')})" for name in sources.keys()]
    markdown += " | ".join(nav_links) + "\n\n--- \n</div>\n\n"

    for name, url in sources.items():
        print(f"Reading from: {name}...")
        feed = feedparser.parse(url)
        # آیدی هدر برای کارکردن منوی ناوبری
        markdown += f"## {name}\n"
        
        if not feed.entries:
            markdown += "> ⚠️ *Source temporarily unavailable.*\n\n"
            continue
        
        for entry in feed.entries[:5]: # ۵ خبر برتر از هر منبع
            markdown += f"### 📰 {entry.title}\n"
            
            img, content = get_full_content(entry, name)
            
            if img:
                if img.startswith('//'): img = 'https:' + img
                markdown += f"<img src='{img}' width='100%' style='border-radius:15px;'>\n\n"
            
            markdown += "<div align='justify'>\n<font size='4'>\n\n"
            
            if content and len(content) > 200:
                markdown += f"{content}\n\n"
            else:
                # اگر استخراج متن شکست خورد، از خلاصه RSS استفاده کن (سیستم بک‌آپ)
                summary = re.sub('<[^<]+?>', '', entry.get('summary', ''))
                if not summary or len(summary) < 20: 
                    summary = entry.get('description', 'Full content is available via the link below.')
                markdown += f"*{summary}*\n\n"
            
            markdown += "</font>\n</div>\n\n"
            markdown += f" [🔗 Read Full Story on {name}]({entry.link})\n\n"
            markdown += "<p align='center'>━━━━━━━━━━━━━━━━━━━━━━━━━</p>\n\n"
        
        markdown += "\n---\n"

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(markdown)

if __name__ == "__main__":
    main()
