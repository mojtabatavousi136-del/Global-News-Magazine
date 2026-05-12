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
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/533.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/533.36'
        }
        response = requests.get(url, headers=headers, timeout=12)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # ۱. استخراج عکس شاخص (تلاش اول: متاتگ‌ها)
            meta_img = (soup.find("meta", property="og:image") or 
                        soup.find("meta", attrs={"name": "twitter:image"}))
            if meta_img:
                result['image'] = meta_img.get('content')
            else:
                # تلاش دوم: جستجوی تگ img با کلاس common (مثلا برای ناسا)
                first_img = soup.find('img')
                if first_img and first_img.get('src'):
                    img_src = first_img.get('src')
                    # فیلتر کردن تصاویر آیکون یا لوگو
                    if not any(ext in img_src for ext in ['.gif', '.svg', 'logo', 'icon']) and (first_img.get('width') and int(first_img.get('width')) > 200 or not first_img.get('width')):
                        if img_src.startswith('//'):
                            result['image'] = 'https:' + img_src
                        elif not img_src.startswith('http'):
                            # تلاش برای ساخت URL کامل در صورت نسبی بودن
                            base_url_parts = url.split('/')[:3]
                            base_url = '/'.join(base_url_parts)
                            result['image'] = base_url + img_src if img_src.startswith('/') else base_url + '/' + img_src
                        else:
                            result['image'] = img_src
            
            # ۲. استخراج متن اصلی خبر
            for s in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'button', 'form']):
                s.decompose()
            
            paragraphs = soup.find_all('p')
            content_list = []
            for p in paragraphs:
                txt = p.get_text().strip()
                if len(txt) > 70 and not txt.startswith("©"): # فیلتر جملات بسیار کوتاه یا کپی‌رایت
                    content_list.append(txt)
            
            full_text = "\n\n".join(content_list[:8]) # محدود به ۸ پاراگراف اول
            result['text'] = full_text
    except Exception as e:
        print(f"Error getting content from {url}: {e}") # برای دیباگ در صورت لزوم
        pass
    return result

def get_news():
    now = datetime.datetime.now()
    
    FEEDS = {
        '🇮🇷 MIDDLE EAST NEWS': [
            ('Al Jazeera', 'https://www.aljazeera.com/xml/rss/all.xml')
        ],
        '🌍 TOP GLOBAL AGENCIES': [
            ('BBC World', 'https://feeds.bbci.co.uk/news/world/rss.xml'),
            # Reuters حذف شد
            ('The Guardian', 'https://www.theguardian.com/world/rss'),
            ('NY Times', 'https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml'), # همچنان اضافه شده اما در گیت‌هاب کار نمی‌کند
            ('Associated Press', 'https://newsatme.com/en/category/world/feed/')
        ],
        '🚀 SCIENCE': [
            ('NASA News', 'https://www.nasa.gov/news-release/feed/'),
            # National Geographic حذف شد
        ],
        '🎬 ENTERTAINMENT & TECH': [
            # People Magazine حذف شد
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
                if not feed.entries: # اگر فید خالی بود یا خطا داشت
                    content += f"<p align='center' style='color: red;'>⚠️ Could not retrieve news from {name}.</p>\n"
                    continue

                for entry in feed.entries[:5]: # ۵ خبر برتر
                    # برای نیویورک تایمز، اگر خطا داشتیم، آن را نمایش نده
                    if name == 'NY Times':
                        try:
                            # فقط یک تلاش برای NYT در گیت‌هاب
                            response = requests.get(entry.link, headers=headers, timeout=5)
                            if response.status_code != 200:
                                print(f"NY Times link {entry.link} blocked or returned {response.status_code}")
                                continue # این خبر را رد کن
                        except requests.exceptions.RequestException:
                            print(f"NY Times link {entry.link} connection error.")
                            continue # این خبر را رد کن

                    data = get_full_article_content(entry.link)
                    
                    content += f"<div align='center'>\n"
                    content += f"<h3>{entry.title}</h3>\n"
                    
                    if data['image']:
                        content += f"<img src='{data['image']}' width='85%' style='border-radius: 12px; margin-bottom: 15px;' />\n"
                    
                    if data['text']:
                        content += f"<div align='justify' style='line-height: 1.6; color: #333; padding: 0 15px;'>\n\n{data['text']}\n\n</div>\n"
                    else:
                        summary = entry.get('summary', '')
                        if summary: # اگر خلاصه هم داشتیم، نمایش بده
                            content += f"<p align='justify' style='line-height: 1.6; color: #555; padding: 0 15px;'>{summary}</p>\n"
                        else:
                            content += f"<p align='center' style='color: gray;'>No full article text or summary available.</p>\n"
                    
                    content += f"<p>🔗 <a href='{entry.link}'>Source: {name}</a></p>\n"
                    content += "<p>━━━━━━━━━━━━━━━━━━━━━━━━━</p>\n"
                    content += f"</div>\n\n"
                
                time.sleep(2) # وقفه برای جلوگیری از بلاک شدن
            except Exception as e:
                content += f"<p align='center' style='color: red;'>⚠️ Failed to load news for {name}. Error: {e}</p>\n"
                continue
                
            content += f"<p align='right'><a href='#top'>🔼 Back to Top</a></p>\n<hr>\n"
            
    return content

if __name__ == "__main__":
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(get_news())
