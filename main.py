import feedparser
import datetime
import requests
from bs4 import BeautifulSoup

def get_full_text(url):
    try:
        # ارسال درخواست با هویت مرورگر واقعی برای دور زدن محدودیت‌ها
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # پیدا کردن پاراگراف‌های اصلی متن
        paragraphs = soup.find_all('p')
        full_text = "\n\n".join([p.get_text() for p in paragraphs[:8]]) # دریافت ۸ پاراگراف اول
        
        if len(full_text) < 100:
            return "Full content is protected or requires a subscription. Please use the source link below."
        return full_text
    except Exception as e:
        return f"Error retrieving content: {str(e)}"

def get_news():
    now = datetime.datetime.now()
    RSS_FEEDS = {
        '🇮🇷 Iran & Middle East': 'https://www.aljazeera.com/xml/rss/all.xml',
        '🇺🇸 US Top Stories': 'https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml',
        '🌍 World News': 'https://www.reutersagency.com/feed/?best-topics=world-news&format=xml',
        '🎬 Celebrity & Style': 'https://people.com/celebrity/feed/'
    }

    header = f"""
<div align="center">
    <h1>🌍 GLOBAL MAHOOR MAGAZINE</h1>
    <p><i>Latest International Edition - High Quality News Coverage</i></p>
    <p>📅 <b>Updated on:</b> {now.strftime('%A, %d %B %Y | %H:%M')} UTC</p>
    <hr>
</div>
"""
    content = header
    
    for category, url in RSS_FEEDS.items():
        feed = feedparser.parse(url)
        content += f"## {category}\n\n"
        
        count = 0
        for entry in feed.entries:
            if count >= 3: break
            
            # فیلتر اختصاصی ایران
            if '🇮🇷' in category and 'iran' not in entry.title.lower():
                continue

            print(f"Processing: {entry.title}")
            
            # دریافت متن خبر با متد جدید
            full_content = get_full_text(entry.link)
            
            # استخراج تصویر (در صورت وجود در فید)
            img_tag = ""
            if 'media_content' in entry:
                img_url = entry.media_content[0]['url']
                img_tag = f'<img src="{img_url}" width="100%" />\n\n'

            content += f"### 📌 {entry.title}\n"
            content += img_tag
            content += f"<details>\n<summary><b>📖 Click to Expand Full Article</b></summary>\n\n"
            content += f"{full_content}\n\n"
            content += f"🔗 **Read more at:** [Source Link]({entry.link})\n\n"
            content += f"</details>\n\n---\n\n"
            count += 1
            
    return content

if __name__ == "__main__":
    try:
        final_magazine = get_news()
        with open("README.md", "w", encoding="utf-8") as f:
            f.write(final_magazine)
        print("Success: Magazine updated.")
    except Exception as e:
        print(f"Failed: {e}")
