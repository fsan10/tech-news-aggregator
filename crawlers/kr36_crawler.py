"""
36氪爬虫
"""
from typing import List, Dict
from .base_crawler import BaseCrawler
import json
import re


class Kr36Crawler(BaseCrawler):
    """36氪爬虫 - https://36kr.com/"""
    
    def __init__(self):
        super().__init__("36氪", "https://36kr.com")
    
    def crawl(self, max_articles: int = 20) -> List[Dict]:
        """爬取36氪科技资讯"""
        articles = []
        
        # 36氪科技频道
        soup = self._get_page(f"{self.base_url}/news")
        if not soup:
            return articles
        
        # 查找文章链接
        article_links = soup.select('a[href*="/news/"]') + soup.select('a[href*="/p/"]')
        
        seen_urls = set()
        for link in article_links[:max_articles * 2]:
            if len(articles) >= max_articles:
                break
            
            href = link.get('href', '')
            if not href or href in seen_urls:
                continue
            
            # 构建完整URL
            if href.startswith('/'):
                href = self.base_url + href
            
            seen_urls.add(href)
            
            # 获取标题
            title_elem = link.select_one('h2, h3, .title, .article-title, .news-title')
            title = title_elem.get_text(strip=True) if title_elem else link.get_text(strip=True)
            
            if not title or len(title) < 5:
                continue
            
            # 获取文章详情
            article_soup = self._get_page(href)
            summary = ""
            publish_time = ""
            
            if article_soup:
                # 获取摘要
                meta_desc = article_soup.select_one('meta[name="description"]')
                if meta_desc:
                    summary = meta_desc.get('content', '')
                
                # 尝试从JSON-LD获取信息
                json_ld = article_soup.select_one('script[type="application/ld+json"]')
                if json_ld:
                    try:
                        data = json.loads(json_ld.string)
                        if isinstance(data, list):
                            data = data[0] if data else {}
                        if not summary and 'description' in data:
                            summary = data['description']
                        if 'datePublished' in data:
                            publish_time = data['datePublished']
                    except:
                        pass
                
                # 获取发布时间
                if not publish_time:
                    time_elem = article_soup.select_one('.time, .date, .publish-time, time')
                    if time_elem:
                        publish_time = time_elem.get_text(strip=True)
            
            article = self._create_article(
                title=title,
                url=href,
                summary=summary,
                publish_time=publish_time
            )
            articles.append(article)
        
        return articles
