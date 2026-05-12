import feedparser
import datetime
from newspaper import Article

# منابع خبری
RSS_FEEDS = {
    '🇮🇷 Iran Coverage': 'https://www.aljazeera.com/xml/rss/all.xml',
    '🇺🇸 US News (NYT)': 'https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml',
    '🌍 World News': 'https://www.reutersagency.com/feed/?best-topics=world-news&format=xml',
    '🎬 Celebrity': 'https://people.com/celebrity/feed/'
}

def get_full_text(url):
    try:
        article = Article(url)
        article.download()
        article.parse()
        return article.text[:2000] + "..." # دریافت متن اصلی (محدود به ۲۰۰۰ کاراکتر برای جلوگیری از سنگین شدن فایل)
    except:
        return "Full text could not be retrieved. Please visit the source link."

def get_news():
    now = datetime.datetime.now()
    header = f"""
<div align="center">
    <h1>🌍 GLOBAL MAHOOR MAGAZINE</h1>
    <p><i>Full Coverage - International Edition</i></p>
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
            if count >= 3: break # ۳ خبر برتر از هر منبع (به دلیل زمان‌بر بودن استخراج متن کامل)
            
            if 'Iran' in category and 'iran' not in entry.title.lower():
                continue

            print(f"Fetching full text for: {entry.title}")
            full_text = get_full_text(entry.link)
            
            content += f"### 📌 {entry.title}\n"
            content += f"**Source:** {entry.link}\n\n"
            # استفاده از تگ details برای نمایش متن کامل به صورت کشویی
            content += f"<details>\n<summary><b>Click to read full article content</b></summary>\n\n{full_text}\n\n</details>\n\n"
            content += "---\n\n"
            count += 1
            
    return content

if __name__ == "__main__":
    news_magazine = get_news()
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(news_magazine)
