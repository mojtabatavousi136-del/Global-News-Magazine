import feedparser
import datetime
import requests
from bs4 import BeautifulSoup
import time

def get_full_article_content(url):
    """استخراج مستقیم متن کامل و عکس از سایت خبرگزاری"""
    result = {'image': None, 'text': ''}
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=12)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # ۱. استخراج عکس شاخص
            meta_img = (soup.find("meta", property="og:image") or 
                        soup.find("meta", attrs={"name": "twitter:image"}))
            if meta_img:
                result['image'] = meta_img.get('content')

            # ۲. استخراج متن اصلی خبر
            # حذف موارد اضافه برای رسیدن به متن خالص
            for s in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'button']):
                s.decompose()
            
            paragraphs = soup.find_all('p')
            content_list = []
            for p in paragraphs:
                txt = p.get_text().strip()
                # فیلتر جملات بسیار کوتاه یا تبلیغاتی
                if len(txt) > 70:
                    content_list.append(txt)
            
            # ترکیب پاراگراف‌ها (محدود به ۸ پاراگراف اول برای جلوگیری از سنگینی بیش از حد)
            full_text = "\n\n".join(content_list[:8])
            result['text'] = full_text
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
    content += f"<p>📅 {now.strftime('%A, %d %B %Y')} | 🕒 Full Text Edition</p>\n</div>\n\n---\n\n"

    # منوی دسترسی سریع
    content += "### 📌 QUICK NAVIGATION\n<div align='center'>\n"
    for section, sources in FEEDS.items():
        content += f"**{section}**<br>\n"
        links = [f"<a href='#{name.replace(' ', '_')}'>{name}</a>" for name, _ in sources]
        content += " | ".join(links) + "<br>\n"
    content += "</div>\n\n---\n"

    for section, sources in FEEDS.items():
        content += f"\n<br><h2 align='center' style='background-color: #f8f9fa; border-bottom: 2px solid #0d47a1; padding: 10px;'>{section}</h2>\n"
        
        for name, url in sources:
            content += f"<a name='{name.replace(' ', '_')}'></a>\n"
            content += f"<br><h3 align='center' style='color: #d32f2f;'>● {name} ●</h3>\n\n"
            
            try:
                feed = feedparser.parse(url)
                for entry in feed.entries[:5]: # ۵ خبر برتر
                    data = get_full_article_content(entry.link)
                    
                    content += f"<div align='center'>\n"
                    content += f"<h3>{entry.title}</h3>\n"
                    
                    if data['image']:
                        content += f"<img src='{data['image']}' width='85%' style='border-radius: 12px; margin-bottom: 15px;' />\n"
                    
                    # نمایش مستقیم متن کامل
                    if data['text']:
                        content += f"<div align='justify' style='line-height: 1.6; color: #333; padding: 0 15px;'>\n\n{data['text']}\n\n</div>\n"
                    else:
                        # جایگزین در صورت عدم دسترسی به متن اصلی
                        content += f"<p align='justify'>{entry.get('summary', '')}</p>\n"
                    
                    content += f"<p>🔗 <a href='{entry.link}'>Source: {name}</a></p>\n"
                    content += "<p>━━━━━━━━━━━━━━━━━━━━━━━━━</p>\n"
                    content += f"</div>\n\n"
                
                time.sleep(2)
            except:
                continue
                
            content += f"<p align='right'><a href='#top'>🔼 Back to Top</a></p>\n<hr>\n"
            
    return content

if __name__ == "__main__":
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(get_news())
