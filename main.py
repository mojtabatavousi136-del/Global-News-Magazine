import feedparser
import datetime
import requests
from bs4 import BeautifulSoup
import re

def get_article_data(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # استخراج تصویر اصلی
        img_url = None
        meta_img = (soup.find("meta", property="og:image") or 
                    soup.find("meta", attrs={"name": "twitter:image"}))
        if meta_img:
            img_url = meta_img.get('content')

        # استخراج متن (۳ پاراگراف اول برای جلوگیری از طولانی شدن بیش از حد)
        for el in soup(["script", "style", "nav", "header", "footer", "aside", "button", "form"]): 
            el.decompose()
        paragraphs = soup.find_all('p')
        text_blocks = [p.get_text().strip() for p in paragraphs if len(p.get_text()) > 80]
        full_text = "\n\n".join(text_blocks[:3]) if text_blocks else "Visit the source for full coverage."
        
        return full_text, img_url
    except:
        return "Summary available at the source link.", None

def get_news():
    now = datetime.datetime.now()
    
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
        '🎬 CELEBRITY & GOSSIP': [
            ('People Magazine', 'https://people.com/celebrity/feed/'),
            ('TMZ News', 'https://www.tmz.com/rss.xml'),
            ('The Verge', 'https://www.theverge.com/rss/index.xml')
        ]
    }

    # ۱. هدر اصلی
    content = f"""
<div align="center">
    <img src="https://img.icons8.com/fluency/100/news.png" width="80" />
    <h1>MAHOOR WORLD PREMIER NEWS</h1>
    <p>📅 {now.strftime('%A, %d %B %Y')} | 🕒 Updated every 4 hours</p>
</div>

---

### 📌 QUICK NAVIGATION
<div align="center">
"""
    # ۲. ایجاد منوی دسترسی سریع خودکار
    for section, sources in FEEDS.items():
        content += f"**{section}**<br>\n"
        links = []
        for name, _ in sources:
            anchor = name.lower().replace(" ", "-").replace("(", "").replace(")", "")
            links.append(f"[{name}](#{anchor})")
        content += " | ".join(links) + "<br>\n"
    
    content += "</div>\n\n---"

    # ۳. استخراج و نمایش اخبار (۱۰ خبر برای هر منبع)
    for section, sources in FEEDS.items():
        content += f"\n<br><h2 align='center' style='background-color: #f8f9fa; padding: 10px; border-radius: 10px;'>{section}</h2>\n"
        
        for name, url in sources:
            anchor = name.lower().replace(" ", "-").replace("(", "").replace(")", "")
            content += f"<br><h3 id='{anchor}' align='center' style='color: #0056b3;'>━━━ {name} ━━━</h3>\n\n"
            
            feed = feedparser.parse(url)
            # انتخاب ۱۰ خبر اول
            entries = feed.entries[:10]
            
            for entry in entries:
                print(f"Fetching: {name} - {entry.title}")
                full_text, img_url = get_article_data(entry.link)

                content += f"<div align='center'>\n"
                content += f"<h4>{entry.title}</h4>\n"
                
                if img_url:
                    content += f"<img src='{img_url}' width='80%' style='border-radius: 10px;' />\n"
                
                content += f"</div>\n\n"
                content += f"<div align='justify' style='padding: 0 10%; font-size: 0.9em;'>\n\n{full_text}\n\n</div>\n"
                content += f"<p align='center'>🔗 <a href='{entry.link}'>Read more on {name}</a></p>\n"
                content += "<p align='center'>---</p>\n\n"
                
            content += "<p align='right'><a href='#-quick-navigation'>🔼 Back to Top</a></p>\n"
            content += "<hr width='100%'>\n"
            
    return content

if __name__ == "__main__":
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(get_news())
