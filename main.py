import feedparser
import datetime
import requests
from bs4 import BeautifulSoup
import time

def get_full_article_content(url):
    """ورود به سایت و استخراج تمام پاراگراف‌های متن اصلی خبر"""
    result = {'image': None, 'text': ''}
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # ۱. استخراج عکس شاخص
            meta_img = (soup.find("meta", property="og:image") or 
                        soup.find("meta", attrs={"name": "twitter:image"}))
            if meta_img:
                result['image'] = meta_img.get('content')

            # ۲. استخراج تمامی پاراگراف‌های محتوایی
            # حذف تگ‌های مزاحم مثل اسکریپت‌ها و تبلیغات
            for s in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
                s.decompose()
            
            paragraphs = soup.find_all('p')
            cleaned_paragraphs = []
            for p in paragraphs:
                txt = p.get_text().strip()
                # فیلتر کردن جملات کوتاه تبلیغاتی یا منوها
                if len(txt) > 60 and not txt.startswith("©"):
                    cleaned_paragraphs.append(txt)
            
            # اتصال پاراگراف‌ها با دو خط فاصله
            result['text'] = "\n\n".join(cleaned_paragraphs)
    except:
        pass
    return result

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
    content += f"<p>📅 {now.strftime('%A, %d %B %Y')} | 🕒 Full Coverage Mode</p>\n</div>\n\n---\n\n"

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
                for entry in feed.entries[:5]: # ۵ خبر برتر از هر منبع با متن کامل
                    article_data = get_full_article_content(entry.link)
                    
                    content += f"<div align='center'>\n"
                    content += f"<h3>{entry.title}</h3>\n"
                    
                    if article_data['image']:
                        content += f"<img src='{article_data['image']}' width='85%' style='border-radius: 12px;' />\n"
                    
                    # بخش متن کامل به صورت تاشو
                    if article_data['text']:
                        content += f"\n<details>\n<summary><b>📖 Click to read FULL ARTICLE</b></summary>\n"
                        content += f"<div align='justify' style='padding: 15px; background-color: #f9f9f9; border-radius: 10px; color: #222;'>\n\n"
                        content += f"{article_data['text']}\n\n"
                        content += f"</div>\n</details>\n"
                    else:
                        # اگر متن کامل استخراج نشد، همان خلاصه RSS را نشان بده
                        summary = entry.get('summary', '')
                        content += f"<p align='justify'>{summary}</p>\n"
                    
                    content += f"<p>🔗 <a href='{entry.link}'>Source: {name}</a></p>\n"
                    content += "<p>───</p>\n"
                    content += f"</div>\n\n"
                
                time.sleep(2) # وقفه بیشتر برای جلوگیری از بلاک شدن به دلیل استخراج متن سنگین
            except:
                continue
                
            content += f"<p align='right'><a href='#top'>🔼 Back to Top</a></p>\n<hr>\n"
            
    return content

if __name__ == "__main__":
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(get_news())
