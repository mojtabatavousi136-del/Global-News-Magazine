import feedparser
import datetime
import requests
from bs4 import BeautifulSoup
import time
import re

def get_article_image(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            meta_img = (soup.find("meta", property="og:image") or 
                        soup.find("meta", attrs={"name": "twitter:image"}))
            if meta_img:
                return meta_img.get('content')
    except:
        pass
    return None

def clean_html(raw_html):
    """پاکسازی تگ‌های HTML از داخل توضیحات"""
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext[:300] + "..." if len(cleantext) > 300 else cleantext

def get_news():
    now = datetime.datetime.now()
    
    FEEDS = {
        '🇮🇷 IRAN & MIDDLE EAST': [
            ('Iran International', 'https://www.iranintl.com/en/rss'),
            ('Al Jazeera', 'https://www.aljazeera.com/xml/rss/all.xml')
        ],
        '🌍 TOP GLOBAL AGENCIES': [
            ('BBC World', 'https://feeds.bbci.co.uk/news/world/rss.xml'),
            ('Reuters', 'https://www.reutersagency.com/feed/?best-topics=world-news&format=xml'),
            ('The Guardian', 'https://www.theguardian.com/world/rss'),
            ('NY Times', 'https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml'),
            ('Associated Press', 'https://newsatme.com/en/category/world/feed/')
        ],
        '🚀 SCIENCE & NATURE': [
            ('NASA News', 'https://www.nasa.gov/news-release/feed/'),
            ('National Geographic', 'https://www.nationalgeographic.com/rss/index.xml')
        ],
        '🎬 CELEBRITY & GOSSIP': [
            ('People Magazine', 'https://people.com/celebrity/feed/'),
            ('TMZ News', 'https://www.tmz.com/rss.xml'),
            ('The Verge', 'https://www.theverge.com/rss/index.xml')
        ]
    }

    content = f"<div align='center'>\n<h1 id='top'>MAHOOR WORLD PREMIER NEWS</h1>\n"
    content += f"<p>📅 {now.strftime('%A, %d %B %Y')} | 🕒 Updated every 4 hours</p>\n</div>\n\n---\n\n"

    # منوی دسترسی سریع
    content += "### 📌 QUICK NAVIGATION\n<div align='center'>\n"
    for section, sources in FEEDS.items():
        content += f"**{section}**<br>\n"
        links = [f"<a href='#{name.replace(' ', '_')}'>{name}</a>" for name, _ in sources]
        content += " | ".join(links) + "<br>\n"
    content += "</div>\n\n---\n"

    for section, sources in FEEDS.items():
        content += f"\n<br><h2 align='center' style='background-color: #f0f0f0; border-radius: 8px; padding: 10px;'>{section}</h2>\n"
        
        for name, url in sources:
            content += f"<a name='{name.replace(' ', '_')}'></a>\n"
            content += f"<br><h3 align='center' style='color: #0d47a1;'>● {name} ●</h3>\n\n"
            
            try:
                feed = feedparser.parse(url)
                for entry in feed.entries[:8]: # نمایش ۸ خبر از هر منبع
                    img_url = get_article_image(entry.link)
                    # استخراج توضیحات (خلاصه)
                    description = clean_html(entry.get('summary', ''))
                    
                    content += f"<div align='center'>\n"
                    content += f"<h4>{entry.title}</h4>\n"
                    if img_url:
                        content += f"<img src='{img_url}' width='85%' style='border-radius: 12px;' />\n"
                    
                    if description:
                        content += f"<p style='color: #555; font-size: 14px;'>{description}</p>\n"
                    
                    content += f"<p>🔗 <a href='{entry.link}'>Read Full Story on {name}</a></p>\n"
                    content += "<p>───</p>\n"
                    content += f"</div>\n\n"
                
                time.sleep(1) # وقفه برای امنیت
            except Exception as e:
                print(f"Error fetching {name}: {e}")
                
            content += f"<p align='right'><a href='#top'>🔼 Back to Top</a></p>\n<hr>\n"
            
    return content

if __name__ == "__main__":
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(get_news())
