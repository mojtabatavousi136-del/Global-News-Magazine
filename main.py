import feedparser
import datetime
import requests
from bs4 import BeautifulSoup
import re

def get_article_data(url):
    """استخراج متن و تصویر اصلی مستقیماً از صفحه خبر"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # ۱. استخراج تصویر اصلی (از متاتگ‌های OpenGraph)
        img_url = None
        meta_img = soup.find("meta", property="og:image") or soup.find("meta", attrs={"name": "twitter:image"})
        if meta_img:
            img_url = meta_img.get('content')

        # ۲. استخراج متن اصلی
        for el in soup(["script", "style", "nav", "header", "footer", "aside", "button", "form"]): 
            el.decompose()
        paragraphs = soup.find_all('p')
        text_blocks = [p.get_text().strip() for p in paragraphs if len(p.get_text()) > 80]
        full_text = "\n\n".join(text_blocks[:8]) if text_blocks else "Click the link below to read the full story on the official website."
        
        return full_text, img_url
    except:
        return "Content available at the source.", None

def get_news():
    now = datetime.datetime.now()
    # خبرگزاری‌های جدید و متنوع
    RSS_FEEDS = {
        '🌍 AL JAZEERA': 'https://www.aljazeera.com/xml/rss/all.xml',
        '🇬🇧 BBC WORLD': 'https://feeds.bbci.co.uk/news/world/rss.xml',
        '🌿 NAT GEO': 'https://www.nationalgeographic.com/rss/index.xml',
        '🚀 NASA NEWS': 'https://www.nasa.gov/news-release/feed/',
        '🗽 NY TIMES': 'https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml',
        '🏛️ REUTERS': 'https://www.reutersagency.com/feed/?best-topics=world-news&format=xml',
        '🎬 PEOPLE MAG': 'https://people.com/celebrity/feed/'
    }

    header = f"""
<div align="center">
    <img src="https://img.icons8.com/fluency/96/globe.png" width="70" />
    <h1>MAHOOR WORLD PREMIER</h1>
    <p><i>The Most Reliable News from Top Global Agencies</i></p>
    <p>📅 <b>{now.strftime('%A, %d %B %Y')}</b></p>
    <hr size="3">
</div>\n"""
    content = header
    
    for category, url in RSS_FEEDS.items():
        feed = feedparser.parse(url)
        content += f"<br><h2 align='center' style='background-color: #f8f9fa;'>✥ {category} ✥</h2>\n\n"
        
        count = 0
        for entry in feed.entries:
            if count >= 2: break # ۲ خبر برتر از هر منبع
            
            print(f"Fetching: {entry.title}")
            full_text, img_url = get_article_data(entry.link)

            content += f"<div align='center'>\n"
            content += f"<h3>{entry.title}</h3>\n"
            
            # اگر عکس پیدا شد نمایش بده، در غیر این صورت یک تصویر پیش‌فرض شیک
            if img_url:
                content += f"<img src='{img_url}' width='90%' style='border-radius: 12px; box-shadow: 0 4px 8px rgba(0,0,0,0.2);' />\n"
            else:
                content += f"<img src='https://images.unsplash.com/photo-1504711434969-e33886168f5c?auto=format&fit=crop&w=800&q=80' width='90%' style='border-radius: 12px;' />\n"
            
            content += f"</div>\n\n"
            
            content += f"{full_text}\n\n"
            content += f"<p align='right'>🔗 <i>Read on official site: <a href='{entry.link}'>Source Link</a></i></p>\n"
            content += "<hr width='60%' align='center'>\n\n"
            count += 1
            
    return content

if __name__ == "__main__":
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(get_news())
