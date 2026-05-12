import feedparser
import requests
from bs4 import BeautifulSoup
import re
import time
from datetime import datetime

def get_full_content(entry, source_name):
    image_url = None
    full_text = None
    
    # استخراج تصویر از فید
    if 'media_content' in entry:
        image_url = entry.media_content[0]['url']
    elif 'links' in entry:
        for link in entry.links:
            if 'image' in link.get('type', ''):
                image_url = link.href
                break

    try:
        # هدرهای بسیار پیشرفته برای فریب سیستم‌های امنیتی
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'max-age=0',
            'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Upgrade-Insecure-Requests': '1'
        }
        
        # ایجاد وقفه برای الجزیره جهت جلوگیری از بلاک شدن
        if source_name == "Al Jazeera":
            time.sleep(2)

        response = requests.get(entry.link, headers=headers, timeout=20, allow_redirects=True)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # استخراج عکس از متاتگ‌ها اگر در فید نبود
            if not image_url:
                img_tag = soup.find("meta", property="og:image") or soup.find("meta", name="twitter:image")
                if img_tag: image_url = img_tag["content"]

            # پاکسازی المان‌های غیرضروری
            for junk in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'form', 'button', 'svg', 'iframe', 'ul']):
                junk.decompose()

            # جستجوی گسترده برای یافتن محتوای اصلی الجزیره
            article_body = None
            if source_name == "Al Jazeera":
                # تست تمام کلاس‌های احتمالی الجزیره (نسخه جدید و قدیم)
                article_body = soup.find('div', class_=re.compile(r'wysiwyg|article-body|all-content|main-content-column|l-col--8'))
            
            if not article_body:
                article_body = soup.find('article') or soup.find('main') or soup.find('div', id='main-content-area')

            source_to_use = article_body if article_body else soup
            paragraphs = source_to_use.find_all('p')

            text_parts = []
            # لیست کلمات ممنوعه برای تمیز کردن متن
            junk_words = ["Subscribe", "Share this", "Follow us", "Advertisement", "Read more", "©", "Sign up", "Loading", "Copyright"]
            
            for p in paragraphs:
                txt = p.get_text().strip()
                # فیلتر کردن پاراگراف‌های کوتاه یا تبلیغاتی
                if len(txt) > 55 and not any(word in txt for word in junk_words):
                    if txt not in text_parts:
                        text_parts.append(txt)
            
            if text_parts:
                # برای الجزیره پاراگراف‌های بیشتری (تا ۱۵ تا) برمی‌داریم
                limit = 15 if source_name == "Al Jazeera" else 10
                full_text = '\n\n'.join(text_parts[:limit])
                
    except Exception as e:
        print(f"Error for {source_name}: {e}")
        
    return image_url, full_text

def main():
    sources = {
        "Al Jazeera": "https://www.aljazeera.com/xml/rss/all.xml",
        "BBC World": "https://feeds.bbci.co.uk/news/world/rss.xml",
        "The Guardian": "https://www.theguardian.com/world/rss",
        "NY Times": "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
        "Associated Press": "https://newsatme.com/en/category/world/feed/",
        "NASA News": "https://www.nasa.gov/news-release/feed/",
        "TMZ": "https://www.tmz.com/rss.xml",
        "The Verge": "https://www.theverge.com/rss/index.xml"
    }

    now = datetime.now()
    now_str = now.strftime('%Y/%m/%d - %H:%M')
    
    markdown = f"<div align=\"center\">\n\n# 📰 MAHOOR WORLD PREMIER NEWS\n\n**📅 Update:** `{now_str}`\n\n---\n\n### 📌 QUICK NAVIGATION\n"
    
    # ساخت منوی دسترسی سریع (اصلاح شده برای گیت‌هاب)
    nav_links = [f"[{name}](#{name.lower().replace(' ', '-')})" for name in sources.keys()]
    markdown += " | ".join(nav_links) + "\n\n--- \n</div>\n\n"

    for name, url in sources.items():
        print(f"Processing: {name}...")
        try:
            feed = feedparser.parse(url)
            markdown += f"## {name}\n"
            
            if not feed.entries:
                markdown += "> ⚠️ *Source currently unavailable.*\n\n"
                continue
            
            for entry in feed.entries[:5]:
                markdown += f"### 📰 {entry.title}\n"
                img, content = get_full_content(entry, name)
                
                if img:
                    markdown += f"<img src='{img}' width='100%' style='border-radius:15px;'>\n\n"
                
                markdown += "<div align='justify'>\n<font size='4'>\n\n"
                
                if content:
                    markdown += f"{content}\n\n"
                else:
                    # سیستم جایگزین: اگر استخراج متن شکست خورد، خلاصه فید را نشان بده
                    summary = re.sub('<[^<]+?>', '', entry.get('summary', ''))
                    if not summary: summary = entry.get('description', 'Full content available at the link below.')
                    markdown += f"*{summary}*\n\n"
                
                markdown += "</font>\n</div>\n\n"
                markdown += f" [🔗 Read Full Story on {name}]({entry.link})\n\n"
                markdown += "<p align='center'>━━━━━━━━━━━━━━━━━━━━━━━━━</p>\n\n"
            
            markdown += "\n---\n"
        except:
            continue

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(markdown)

if __name__ == "__main__":
    main()
