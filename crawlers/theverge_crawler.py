"""
The Verge爬虫
"""
from typing import List, Dict
from .base_crawler import BaseCrawler
import feedparser
import re


class TheVergeCrawler(BaseCrawler):
    """The Verge爬虫 - https://www.theverge.com/"""
    
    def __init__(self):
        super().__init__("The Verge", "https://www.theverge.com")
        self.rss_url = "https://www.theverge.com/rss/index.xml"
    
    def crawl(self, max_articles: int = 20) -> List[Dict]:
        """爬取The Verge科技资讯 - 使用RSS Feed"""
        articles = []
        
        try:
            feed = feedparser.parse(self.rss_url)
            
            for entry in feed.entries[:max_articles]:
                title = entry.get('title', '')
                url = entry.get('link', '')
                summary = entry.get('summary', '') or entry.get('description', '')
                publish_time = entry.get('published', '') or entry.get('pubDate', '')
                
                if not title or not url:
                    continue
                
                # 清理HTML标签
                summary = re.sub(r'<[^>]+>', '', summary)
                summary = summary.strip()[:500]
                
                article = self._create_article(
                    title=title,
                    url=url,
                    summary=summary,
                    publish_time=publish_time
                )
                articles.append(article)
                
        except Exception as e:
            print(f"[The Verge] RSS解析失败: {e}")
        
        return articles
