"""
TechCrunch爬虫
"""
from typing import List, Dict
from .base_crawler import BaseCrawler
import feedparser


class TechCrunchCrawler(BaseCrawler):
    """TechCrunch爬虫 - https://techcrunch.com/"""
    
    def __init__(self):
        super().__init__("TechCrunch", "https://techcrunch.com")
        self.rss_url = "https://techcrunch.com/feed/"
    
    def crawl(self, max_articles: int = 20) -> List[Dict]:
        """爬取TechCrunch科技资讯 - 使用RSS Feed"""
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
                import re
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
            print(f"[TechCrunch] RSS解析失败: {e}")
        
        return articles
