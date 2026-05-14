"""
科技资讯爬虫基础类
"""
import requests
from bs4 import BeautifulSoup
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from datetime import datetime
import time
import random


class BaseCrawler(ABC):
    """爬虫基类"""
    
    def __init__(self, source_name: str, base_url: str):
        self.source_name = source_name
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        })
    
    def _get_page(self, url: str, retries: int = 3) -> Optional[BeautifulSoup]:
        """获取页面内容"""
        for i in range(retries):
            try:
                response = self.session.get(url, timeout=15)
                response.raise_for_status()
                response.encoding = response.apparent_encoding
                return BeautifulSoup(response.text, 'lxml')
            except Exception as e:
                print(f"[{self.source_name}] 获取页面失败 (尝试 {i+1}/{retries}): {e}")
                if i < retries - 1:
                    time.sleep(random.uniform(1, 3))
        return None
    
    def _classify_category(self, title: str, content: str = "") -> str:
        """根据标题和内容分类赛道"""
        text = (title + " " + content).lower()
        
        # AI相关关键词
        ai_keywords = ['ai', '人工智能', 'gpt', 'chatgpt', '大模型', '机器学习', '深度学习', 
                       'openai', 'anthropic', 'claude', 'gemini', 'llm', 'neural', '神经网络',
                       '自动驾驶', 'autonomous', '机器人', 'robot', '智能', 'intelligence']
        
        # 半导体相关关键词
        semiconductor_keywords = ['芯片', 'chip', '半导体', 'semiconductor', '晶圆', 'wafer',
                                  '台积电', 'tsmc', '英伟达', 'nvidia', 'intel', 'amd', 'arm',
                                  '光刻', 'lithography', 'asml', '制程', '工艺', 'foundry',
                                  '存储', 'memory', 'gpu', 'cpu', '处理器', 'processor']
        
        # 新能源相关关键词
        energy_keywords = ['新能源', '电池', 'battery', '电动车', 'ev', 'electric vehicle',
                          '特斯拉', 'tesla', '比亚迪', 'byd', '宁德时代', 'catl', '储能',
                          'solar', '光伏', '太阳能', '风电', 'wind power', '氢能', 'hydrogen',
                          '充电', 'charging', '锂电', 'lithium', '固态电池', 'solid-state']
        
        # 匹配分类
        for keyword in ai_keywords:
            if keyword in text:
                return 'ai'
        
        for keyword in semiconductor_keywords:
            if keyword in text:
                return 'semiconductor'
        
        for keyword in energy_keywords:
            if keyword in text:
                return 'energy'
        
        return 'other'
    
    @abstractmethod
    def crawl(self, max_articles: int = 20) -> List[Dict]:
        """爬取文章列表，子类必须实现"""
        pass
    
    def _create_article(self, title: str, url: str, summary: str = "", 
                        publish_time: str = "", category: str = None) -> Dict:
        """创建标准化的文章字典"""
        if category is None:
            category = self._classify_category(title, summary)
        
        return {
            'title': title.strip(),
            'url': url,
            'summary': summary.strip()[:500] if summary else "",
            'publish_time': publish_time,
            'source': self.source_name,
            'category': category,
            'crawl_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'is_foreign': self.source_name in ['TechCrunch', 'The Verge', 'MIT Technology Review']
        }
