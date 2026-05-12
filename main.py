import feedparser
import datetime
import requests
from bs4 import BeautifulSoup

def get_article_data(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=12)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # استخراج تصویر اصلی
        img_url = None
        meta_img = (soup.find("meta", property="og:image") or 
                    soup.find("meta", attrs={"name": "twitter:image"}))
        if meta_img:
            img_url = meta_img.get('content')

        # استخراج متن
        for el in soup(["script", "style", "nav", "header", "footer", "aside", "button", "form"]): 
            el.decompose()
        paragraphs = soup.find_all('p')
        text_blocks = [p.get_text().strip() for p in paragraphs if len(p.get_text()) > 80]
        full_text = "\n\n".join(text_blocks[:6]) if text_blocks else "Visit the official site for full coverage."
        
        return full_text, img_url
    except:
        return "Content is temporarily unavailable.", None

def get_news():
    now = datetime.datetime.now()
    
    # لیست کامل تمام خبرگزاری‌های درخواستی (قدیم + جدید)
    FEEDS = {
        '🌍 TOP GLOBAL AGENCIES': [
            ('BBC World', 'https://feeds.bbci.co.uk/news/world/rss.xml'),
            ('Reuters', 'https://www.reutersagency.com/feed/?best-topics=world-news&format=xml'),
            ('Associated Press', 'https://newsatme.com/en/category/world/feed/'),
            ('The Guardian', 'https://www.theguardian.com/world/rss'),
            ('NY Times', 'https://rss.nytimes.com/services/xml/rss/nyt/World.xml')
        ],
        '🇮🇷 IRAN & MIDDLE EAST': [
            ('Al Jazeera', 'https://www.aljazeera.com/xml/rss/all.xml'),
            ('Iran International', 'https://www.iranintl.com/en/rss')
        ],
        '🚀 SCIENCE & NATURE': [
            ('NASA News', 'https://www.nasa.gov/news-release/feed/'),
            ('National Geographic', 'https://www.nationalgeographic.com/rss/index.xml')
        ],
        '🎬 CELEBRITY & ENTERTAINMENT': [
            ('People Magazine', 'https://people.com/celebrity/feed/'),
            ('TMZ News', 'https://www.tmz.com/rss.xml'),
            ('The Verge (Tech)', 'https://www.theverge.com/rss/index.xml')
        ]
    }

    header = f"""
<div align="center">
    <br>
    <img src="https://img.icons8.com/fluency/100/globe-earth.png" width="80" />
    <h1 align="center">MAHOOR WORLD PREMIER NEWS</h1>
    <p align="center"><b>Comprehensive Global Coverage: From Iran to the Stars</b></p>
    <p align="center">📅 {now.strftime('%A, %d %B %Y')} | 🕒 Updated every 4 hours</p>
    <hr width="90%" size="2">
</div>\n"""

    content = header
    
    for section, sources in FEEDS.items():
        content += f"<br><br><h2 align='center' style='background-color: #f0f0f0; padding: 10px; border-radius: 10px;'>{section}</h2>\n\n"
        
        for name, url in sources:
            feed = feedparser.parse(url)
            if not feed.entries: continue
            
            # نمایش ۱ خبر از هر منبع (برای مدیریت حجم صفحه با توجه به تعداد زیاد منابع)
            entry = feed.entries[0]
            print(f"Fetching ({name}): {entry.title}")
            full_text, img_url = get_article_data(entry.link)

            content += f"<div align='center'>\n"
            content += f"<h3><span style='color: #d32f2f;'>{name}</span>: {entry.title}</h3>\n"
            
            if img_url:
                content += f"<img src='{img_url}' width='85%' style='border-radius: 15px; border: 1px solid #eee;' />\n"
            else:
                content += f"<img src='https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=800' width='85%' style='border-radius: 15px;' />\n"
            
            content += f"</div>\n\n"
            content += f"<div align='justify' style='padding: 0 8%;'>\n\n{full_text}\n\n</div>\n"
            content += f"<p align='center'>🔗 <a href='{entry.link}'>Read Full Article</a></p>\n"
            content += "<br><hr width='30%' align='center'>\n\n"
            
    return content

if __name__ == "__main__":
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(get_news())
