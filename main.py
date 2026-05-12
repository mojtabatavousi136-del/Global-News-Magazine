import feedparser
import datetime

# لیست منابع خبری معتبر (آمریکایی و جهانی)
RSS_FEEDS = {
    '🇮🇷 Iran Coverage (Global)': 'https://www.aljazeera.com/xml/rss/all.xml', 
    '🇺🇸 Top US Stories (CNN/NYT)': 'https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml',
    '🌎 World Headlines (Reuters)': 'https://www.reutersagency.com/feed/?best-topics=world-news&format=xml',
    '🎬 Hollywood & Celebrity': 'https://people.com/celebrity/feed/',
    '🏛️ US Politics (Fox News)': 'https://feeds.foxnews.com/foxnews/politics'
}

def get_news():
    news_content = "# 🌎 Global News Magazine\n\n"
    news_content += f"**Last Updated:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC\n\n"
    news_content += "--- \n\n"
    
    for category, url in RSS_FEEDS.items():
        feed = feedparser.parse(url)
        news_content += f"## {category}\n"
        
        count = 0
        for entry in feed.entries:
            if count >= 6: break # نمایش ۶ خبر برتر از هر منبع
            
            # فیلتر اختصاصی برای بخش ایران در منابع جهانی
            if 'Iran' in category:
                if 'iran' in entry.title.lower() or 'iran' in entry.summary.lower():
                    news_content += f"- **[{entry.title}]({entry.link})**\n"
                    count += 1
            else:
                news_content += f"- **[{entry.title}]({entry.link})**\n"
                count += 1
        
        news_content += "\n"
    
    return news_content

if __name__ == "__main__":
    content = get_news()
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(content)
