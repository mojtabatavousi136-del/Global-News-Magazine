import feedparser
import datetime
import requests
from bs4 import BeautifulSoup
import re

def get_full_text(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        for el in soup(["script", "style", "nav", "header", "footer", "aside", "button", "form"]): el.decompose()
        paragraphs = soup.find_all('p')
        text_blocks = [p.get_text().strip() for p in paragraphs if len(p.get_text()) > 80]
        return "\n\n".join(text_blocks[:8]) if text_blocks else "Content available at source link."
    except:
        return "Visit source for full story."

def extract_image(entry):
    # روش اول: جستجو در تگ‌های مدیا
    if 'media_content' in entry:
        return entry.media_content[0]['url']
    if 'media_thumbnail' in entry:
        return entry.media_thumbnail[0]['url']
    
    # روش دوم: جستجوی عمیق در توضیحات HTML
    desc = entry.get('summary', '') or entry.get('description', '')
    if desc:
        img_match = re.search(r'<img.+?src=["\'](.+?)["\']', desc)
        if img_match:
            return img_match.group(1)
            
    # روش سوم: جستجو در لینک‌های پیوست
    if 'links' in entry:
        for link in entry.links:
            if 'image' in link.get('type', ''):
                return link.get('href')
    return None

def get_news():
    now = datetime.datetime.now()
    RSS_FEEDS = {
        '🌍 AL JAZEERA': ('https://www.aljazeera.com/xml/rss/all.xml', 'https://www.aljazeera.com/wp-content/uploads/2020/12/AJ-Logo-English-Vertical.jpg'),
        '🇺🇸 CNN NEWS': ('http://rss.cnn.com/rss/edition.rss', 'https://upload.wikimedia.org/wikipedia/commons/b/b1/CNN.svg'),
        '🗽 NY TIMES': ('https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml', 'https://1000logos.net/wp-content/uploads/2017/04/Symbol-New-York-Times.png'),
        '🏛️ REUTERS': ('https://www.reutersagency.com/feed/?best-topics=world-news&format=xml', 'https://www.reuters.com/pf/resources/images/reuters/logo-vertical-default.png'),
        '🎬 CELEBRITY': ('https://people.com/celebrity/feed/', 'https://people.com/thmb/m_U5_XpZ-Z6l_H1bO4o3YqN6b4o=/1500x0/filters:no_upscale():max_bytes(150000):strip_icc()/people-logo-red-background-7d0e4e5e4d5d4d3d8d3d2d1d0d9d8d7.jpg')
    }

    header = f"""
<div align="center">
    <h1>🌍 GLOBAL NEWS MAGAZINE</h1>
    <p><i>Daily Updates from World's Best Agencies</i></p>
    <p>📅 <b>{now.strftime('%A, %d %B %Y')}</b></p>
    <hr>
</div>\n"""
    content = header
    
    for category, (url, fallback_img) in RSS_FEEDS.items():
        feed = feedparser.parse(url)
        content += f"<h2 align='center'>━━━━ {category} ━━━━</h2>\n\n"
        
        for entry in feed.entries[:2]: # ۲ خبر از هر کدام
            img_url = extract_image(entry) or fallback_img
            full_text = get_full_text(entry.link)

            content += f"<div align='center'>\n"
            content += f"<h3>{entry.title}</h3>\n"
            # استفاده از تگ img با قابلیت ریسپانسیو
            content += f"<img src='{img_url}' width='90%' style='max-height:400px; object-fit: cover; border-radius:15px;' />\n"
            content += f"</div>\n\n"
            
            content += f"{full_text}\n\n"
            content += f"<p align='right'>🔗 <i>Source: <a href='{entry.link}'>Read More</a></i></p>\n"
            content += "<hr width='50%'>\n\n"
            
    return content

if __name__ == "__main__":
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(get_news())
