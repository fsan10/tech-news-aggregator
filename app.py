"""
科技资讯聚合器 - Flask主应用
"""
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from datetime import datetime
from typing import List, Dict
import os

# 导入爬虫
from crawlers.leiphone_crawler import LeiphoneCrawler
from crawlers.kr36_crawler import Kr36Crawler
from crawlers.techcrunch_crawler import TechCrunchCrawler
from crawlers.theverge_crawler import TheVergeCrawler
from crawlers.mit_crawler import MITTechReviewCrawler

# 导入翻译服务
from services.translator import AITranslator, AVAILABLE_MODELS

app = Flask(__name__)
CORS(app)

# 初始化爬虫
CRAWLERS = {
    'leiphone': LeiphoneCrawler(),
    '36kr': Kr36Crawler(),
    'techcrunch': TechCrunchCrawler(),
    'theverge': TheVergeCrawler(),
    'mit': MITTechReviewCrawler()
}

# 初始化翻译器
translator = AITranslator()

# 缓存数据
cache = {
    'articles': [],
    'last_update': None,
    'expires_seconds': 3600  # 1小时缓存
}


def get_all_articles(categories: List[str] = None, max_per_source: int = 10) -> List[Dict]:
    """获取所有来源的文章"""
    all_articles = []

    for name, crawler in CRAWLERS.items():
        try:
            articles = crawler.crawl(max_articles=max_per_source)
            all_articles.extend(articles)
        except Exception as e:
            print(f"[{name}] 爬取失败: {e}")

    # 按分类筛选
    if categories and 'all' not in categories:
        all_articles = [a for a in all_articles if a.get('category') in categories]

    # 按时间排序（最新的在前）
    all_articles.sort(key=lambda x: x.get('crawl_time', ''), reverse=True)

    return all_articles


def process_foreign_articles(articles: List[Dict]) -> List[Dict]:
    """处理国外文章 - 翻译和总结"""
    for article in articles:
        if article.get('is_foreign'):
            result = translator.translate_and_summarize(
                title=article.get('title', ''),
                content=article.get('summary', ''),
                source=article.get('source', '')
            )
            article['translated_title'] = result.get('translated_title', article.get('title'))
            article['chinese_summary'] = result.get('chinese_summary', '')
            article['key_points'] = result.get('key_points', [])
        else:
            result = translator.summarize_chinese(
                title=article.get('title', ''),
                content=article.get('summary', '')
            )
            article['chinese_summary'] = result.get('summary', article.get('summary', ''))
            article['key_points'] = result.get('key_points', [])

    return articles


# ==================== API路由 ====================

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')


@app.route('/api/articles', methods=['GET'])
def get_articles():
    """获取文章列表API"""
    categories = request.args.getlist('category')
    if not categories:
        categories = ['all']

    use_cache = request.args.get('cache', 'true').lower() == 'true'
    refresh = request.args.get('refresh', 'false').lower() == 'true'

    # 检查缓存
    now = datetime.now()
    if use_cache and cache['articles'] and cache['last_update']:
        elapsed = (now - cache['last_update']).total_seconds()
        if elapsed < cache['expires_seconds'] and not refresh:
            articles = cache['articles']
            if categories and 'all' not in categories:
                articles = [a for a in articles if a.get('category') in categories]
            return jsonify({
                'success': True,
                'data': articles,
                'cached': True,
                'last_update': cache['last_update'].strftime('%Y-%m-%d %H:%M:%S')
            })

    # 获取新数据
    articles = get_all_articles(categories=categories if 'all' not in categories else None)

    # AI处理
    articles = process_foreign_articles(articles)

    # 更新缓存
    cache['articles'] = articles
    cache['last_update'] = now

    return jsonify({
        'success': True,
        'data': articles,
        'cached': False,
        'last_update': now.strftime('%Y-%m-%d %H:%M:%S')
    })


@app.route('/api/models', methods=['GET'])
def get_models():
    """获取可用模型列表"""
    current_model = translator.model
    return jsonify({
        'success': True,
        'data': {
            'models': AVAILABLE_MODELS,
            'current': current_model
        }
    })


@app.route('/api/models', methods=['POST'])
def switch_model():
    """切换AI模型"""
    data = request.get_json() or {}
    model_id = data.get('model_id', '')

    # 验证模型ID
    valid_ids = [m['id'] for m in AVAILABLE_MODELS]
    if model_id not in valid_ids:
        return jsonify({
            'success': False,
            'message': f'无效的模型ID，可选: {valid_ids}'
        }), 400

    translator.set_model(model_id)
    # 切换模型后清空缓存，下次请求会用新模型重新处理
    cache['articles'] = []
    cache['last_update'] = None

    return jsonify({
        'success': True,
        'message': f'已切换到模型: {model_id}',
        'current_model': model_id
    })


@app.route('/api/sources', methods=['GET'])
def get_sources():
    """获取数据源列表"""
    sources = [
        {'id': 'leiphone', 'name': '雷锋网', 'url': 'https://www.leiphone.com', 'is_foreign': False},
        {'id': '36kr', 'name': '36氪', 'url': 'https://36kr.com', 'is_foreign': False},
        {'id': 'techcrunch', 'name': 'TechCrunch', 'url': 'https://techcrunch.com', 'is_foreign': True},
        {'id': 'theverge', 'name': 'The Verge', 'url': 'https://www.theverge.com', 'is_foreign': True},
        {'id': 'mit', 'name': 'MIT Technology Review', 'url': 'https://www.technologyreview.com', 'is_foreign': True}
    ]
    return jsonify({'success': True, 'data': sources})


@app.route('/api/categories', methods=['GET'])
def get_categories():
    """获取分类列表"""
    categories = [
        {'id': 'ai', 'name': 'AI人工智能', 'icon': '🤖'},
        {'id': 'semiconductor', 'name': '半导体', 'icon': '💻'},
        {'id': 'energy', 'name': '新能源', 'icon': '⚡'},
        {'id': 'other', 'name': '其他科技', 'icon': '📱'}
    ]
    return jsonify({'success': True, 'data': categories})


@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        'success': True,
        'message': 'Tech News Aggregator is running',
        'ai_configured': translator.is_configured(),
        'current_model': translator.model
    })


# ==================== Vercel入口 ====================

handler = app

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
