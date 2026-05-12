import feedparser
import datetime

# لیست منابع خبری انگلیسی
# تمرکز بر ایران، جهان و سلبریتی‌ها
RSS_FEEDS = {
    '🇮🇷 Iran in Focus': 'https://www.aljazeera.com/xml/rss/all.xml', # فیلتر می‌شود برای اخبار ایران
    '🌍 World News': 'http://feeds.bbci.co.uk/news/world/rss.xml',
    '🎬 Celebrity & Stars': 'https://people.com/celebrity/feed/',
    '🔥 Global Trends': 'https://www.reutersagency.com/feed/?best-topics=world-news&format=xml'
}

def get_news():
    news_content = "# 🌎 Global News Magazine (International Edition)\n\n"
    news_content += f"**Last Updated:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC\n\n"
    
    for category, url in RSS_FEEDS.items():
        feed = feedparser.parse(url)
        news_content += f"## {category}\n"
        
        # برای بخش ایران، فقط خبرهایی که کلمه Iran دارند را جدا می‌کنیم
        count = 0
        for entry in feed.entries:
            if count >= 5: break
            
            if category == '🇮🇷 Iran in Focus':
                if 'iran' in entry.title.lower() or 'iran' in entry.summary.lower():
                    news_content += f"- [{entry.title}]({entry.link})\n"
                    count += 1
            else:
                news_content += f"- [{entry.title}]({entry.link})\n"
                count += 1
        
        news_content += "\n"
    
    return news_content

if __name__ == "__main__":
    content = get_news()
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(content)
