import feedparser
import datetime
import requests
from bs4 import BeautifulSoup

def get_full_text(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # حذف المان‌های مزاحم مثل تبلیغات و منوها
        for script in soup(["script", "style", "nav", "header", "footer", "aside"]):
            script.decompose()

        # استخراج پاراگراف‌ها (تلاش برای پیدا کردن بدنه اصلی خبر)
        # اکثر سایت‌های خبری متن اصلی را در تگ‌های p قرار می‌دهند
        paragraphs = soup.find_all('p')
        
        # فیلتر کردن پاراگراف‌های خیلی کوتاه یا نامربوط
        text_blocks = [p.get_text().strip() for p in paragraphs if len(p.get_text()) > 80]
        
        if not text_blocks:
            return "Note: Content is behind a paywall or requires JavaScript. Please visit the source link for the full story."
        
        return "\n\n".join(text_blocks[:10]) # دریافت ۱۰ پاراگراف اول خبر
    except Exception as e:
        return f"Content temporarily unavailable. Please check the source link."

def get_news():
    now = datetime.datetime.now()
    # لیست منابع معتبر آمریکایی و جهانی
    RSS_FEEDS = {
        '🇺🇸 CNN Top News': 'http://rss.cnn.com/rss/edition.rss',
        '🗽 New York Times': 'https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml',
        '🏛️ Reuters World': 'https://www.reutersagency.com/feed/?best-topics=world-news&format=xml',
        '🎬 Hollywood & Stars': 'https://people.com/celebrity/feed/'
    }

    header = f"""
<div align="center">
    <h1>🌍 GLOBAL MAHOOR NEWSROOM</h1>
    <p><i>Premium International Edition - Powered by Major US Networks</i></p>
    <p>📅 <b>Last Update:</b> {now.strftime('%A, %d %B %Y | %H:%M')} UTC</p>
    <hr>
</div>
"""
    content = header
    
    for category, url in RSS_FEEDS.items():
        feed = feedparser.parse(url)
        content += f"## {category}\n\n"
        
        count = 0
        for entry in feed.entries:
            if count >= 4: break # نمایش ۴ خبر برتر از هر منبع
            
            print(f"Scraping: {entry.title}")
            full_content = get_full_text(entry.link)
            
            content += f"### 📌 {entry.title}\n"
            
            # نمایش خلاصه کوتاه پیش از باز کردن آکاردئون
            summary = entry.get('summary', '')
            if summary:
                # پاکسازی تگ‌های HTML احتمالی در خلاصه
                clean_summary = BeautifulSoup(summary, "html.parser").get_text()[:200]
                content += f"*{clean_summary}...*\n\n"

            content += f"<details>\n<summary><b>📖 READ FULL ARTICLE CONTENT</b></summary>\n\n"
            content += f"{full_content}\n\n"
            content += f"🔗 **Source:** [{entry.link}]({entry.link})\n\n"
            content += f"</details>\n\n---\n\n"
            count += 1
            
    return content

if __name__ == "__main__":
    try:
        magazine_content = get_news()
        with open("README.md", "w", encoding="utf-8") as f:
            f.write(magazine_content)
        print("Magazine updated successfully.")
    except Exception as e:
        print(f"Error: {e}")
