import feedparser
import datetime
import requests
from bs4 import BeautifulSoup

def get_article_data(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # استخراج تصویر با اولویت بالا
        img_url = None
        meta_img = (soup.find("meta", property="og:image") or 
                    soup.find("meta", attrs={"name": "twitter:image"}) or
                    soup.find("meta", property="og:image:secure_url"))
        
        if meta_img:
            img_url = meta_img.get('content')

        # استخراج متن - بهینه‌شده برای خبرگزاری‌های سخت‌گیر مثل NYT
        for el in soup(["script", "style", "nav", "header", "footer", "aside", "button", "form", "meta"]): 
            el.decompose()
            
        paragraphs = soup.find_all('p')
        text_blocks = [p.get_text().strip() for p in paragraphs if len(p.get_text()) > 70]
        full_text = "\n\n".join(text_blocks[:4]) if text_blocks else "Click 'Read Full Article' to view the content on the original website."
        
        return full_text, img_url
    except Exception as e:
        return "Content preview is currently unavailable for this article.", None

def get_news():
    now = datetime.datetime.now()
    
    FEEDS = {
        '🌍 GLOBAL AGENCIES': [
            ('BBC World', 'https://feeds.bbci.co.uk/news/world/rss.xml'),
            ('Reuters', 'https://www.reutersagency.com/feed/?best-topics=world-news&format=xml'),
            ('The Guardian', 'https://www.theguardian.com/world/rss'),
            ('NY Times', 'https://rss.nytimes.com/services/xml/rss/nyt/World.xml'),
            ('Associated Press', 'https://newsatme.com/en/category/world/feed/')
        ],
        '🇮🇷 IRAN & MIDDLE EAST': [
            ('Al Jazeera', 'https://www.aljazeera.com/xml/rss/all.xml'),
            ('Iran International', 'https://www.iranintl.com/en/rss')
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

    # هدر اصلی
    content = f"<div align='center'>\n<h1 id='top'>MAHOOR WORLD PREMIER NEWS</h1>\n"
    content += f"<p>📅 {now.strftime('%A, %d %B %Y')} | 🕒 Updated every 4 hours</p>\n</div>\n\n---\n\n"

    # منوی دسترسی سریع (اصلاح شده با تگ A)
    content += "### 📌 QUICK NAVIGATION\n<div align='center'>\n"
    for section, sources in FEEDS.items():
        content += f"**{section}**<br>\n"
        links = [f"<a href='#{name.replace(' ', '_')}'>{name}</a>" for name, _ in sources]
        content += " | ".join(links) + "<br>\n"
    content += "</div>\n\n---\n"

    # بدنه اصلی اخبار
    for section, sources in FEEDS.items():
        content += f"\n<br><h2 align='center' style='background-color: #f0f0f0; border-radius: 8px;'>{section}</h2>\n"
        
        for name, url in sources:
            # ایجاد لنگرگاه برای منو
            content += f"<a name='{name.replace(' ', '_')}'></a>\n"
            content += f"<br><h3 align='center' style='color: #0d47a1;'>● {name} ●</h3>\n\n"
            
            feed = feedparser.parse(url)
            for entry in feed.entries[:10]:
                full_text, img_url = get_article_data(entry.link)
                
                content += f"<div align='center'>\n"
                content += f"<h4>{entry.title}</h4>\n"
                if img_url:
                    content += f"<img src='{img_url}' width='85%' style='border-radius: 12px;' />\n"
                content += f"</div>\n\n"
                
                content += f"<div align='justify' style='padding: 0 8%;'>\n\n{full_text}\n\n</div>\n"
                content += f"<p align='center'>🔗 <a href='{entry.link}'>Read Full Article</a></p>\n"
                content += "<p align='center'>───</p>\n\n"
                
            content += f"<p align='right'><a href='#top'>🔼 Back to Navigation</a></p>\n<hr>\n"
            
    return content

if __name__ == "__main__":
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(get_news())
