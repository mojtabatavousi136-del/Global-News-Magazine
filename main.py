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
        # حذف المان‌های مزاحم
        for el in soup(["script", "style", "nav", "header", "footer", "aside", "button", "form"]): 
            el.decompose()
        
        paragraphs = soup.find_all('p')
        # فیلتر کردن پاراگراف‌های معنادار
        text_blocks = [p.get_text().strip() for p in paragraphs if len(p.get_text()) > 80]
        
        if not text_blocks:
            return "*(Full content is available on the main website via the link below)*"
        
        # ترکیب ۱۰ پاراگراف اول برای نمایش متن کامل
        return "\n\n".join(text_blocks[:10])
    except:
        return "*(Content could not be extracted at this time. Please use the source link.)*"

def extract_image(entry):
    # استخراج عکس از تگ‌های مختلف فید
    if 'media_content' in entry:
        return entry.media_content[0]['url']
    if 'links' in entry:
        for link in entry.links:
            if 'image' in link.get('type', ''):
                return link.get('href')
    if 'summary' in entry:
        img_match = re.search(r'<img.+?src=["\'](.+?)["\']', entry.summary)
        if img_match:
            return img_match.group(1)
    return None

def get_news():
    now = datetime.datetime.now()
    # منابع منتخب شما
    RSS_FEEDS = {
        '🌍 AL JAZEERA': 'https://www.aljazeera.com/xml/rss/all.xml',
        '🇺🇸 CNN WORLD': 'http://rss.cnn.com/rss/edition.rss',
        '🗽 NEW YORK TIMES': 'https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml',
        '🏛️ REUTERS': 'https://www.reutersagency.com/feed/?best-topics=world-news&format=xml',
        '🎬 CELEBRITY & STYLE': 'https://people.com/celebrity/feed/'
    }

    header = f"""
<div align="center">
    <img src="https://img.icons8.com/fluency/96/news.png" width="60" />
    <h1>GLOBAL MAHOOR NEWSROOM</h1>
    <p><i>Premium Daily Magazine - English Edition</i></p>
    <p>📅 <b>{now.strftime('%A, %d %B %Y')}</b></p>
    <hr size="3" color="#333">
</div>
\n"""
    content = header
    
    for category, url in RSS_FEEDS.items():
        feed = feedparser.parse(url)
        content += f"<br><h2 align='center' style='color: #2c3e50;'>━━━━━━ {category} ━━━━━━</h2>\n\n"
        
        count = 0
        for entry in feed.entries:
            if count >= 2: break # دو خبر برتر از هر منبع برای جلوگیری از طولانی شدن بیش از حد
            
            img_url = extract_image(entry)
            full_text = get_full_text(entry.link)

            # استایل مشابه مجله فارسی (تیتر، عکس، متن)
            content += f"<div align='center'>\n"
            content += f"<h3>📢 {entry.title}</h3>\n"
            
            if img_url:
                content += f"<img src='{img_url}' width='85%' style='border-radius: 15px; margin: 10px 0;' />\n"
            
            content += f"</div>\n\n"
            
            # نمایش مستقیم متن کامل
            content += f"{full_text}\n\n"
            content += f"<div align='right'>🔗 <i>Source: <a href='{entry.link}'>Click Here</a></i></div>\n\n"
            content += "<hr width='70%' align='center' style='border: 0.5px dashed #bbb;'>\n\n"
            count += 1
            
    return content

if __name__ == "__main__":
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(get_news())
