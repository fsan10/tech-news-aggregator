"""
雷锋网爬虫
"""
from typing import List, Dict
from .base_crawler import BaseCrawler
import re


class LeiphoneCrawler(BaseCrawler):
    """雷锋网爬虫 - https://www.leiphone.com/"""
    
    def __init__(self):
        super().__init__("雷锋网", "https://www.leiphone.com")
    
    def crawl(self, max_articles: int = 20) -> List[Dict]:
        """爬取雷锋网科技资讯"""
        articles = []
        
        # 雷锋网首页
        soup = self._get_page(self.base_url)
        if not soup:
            return articles
        
        # 查找文章链接
        article_links = soup.select('a[href*="/news/"]') + soup.select('a[href*="/article/"]')
        
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
            title_elem = link.select_one('h2, h3, .title, .article-title')
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
                
                # 获取发布时间
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
