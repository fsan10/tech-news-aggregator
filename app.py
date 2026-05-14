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
from services.translator import AITranslator

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
    'expires_seconds': 3600
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

    if categories and 'all' not in categories:
        all_articles = [a for a in all_articles if a.get('category') in categories]

    all_articles.sort(key=lambda x: x.get('crawl_time', ''), reverse=True)
    return all_articles


def process_articles(articles: List[Dict]) -> List[Dict]:
    """处理文章 - AI翻译和总结"""
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
    return render_template('index.html')


@app.route('/api/articles', methods=['GET'])
def get_articles():
    categories = request.args.getlist('category')
    if not categories:
        categories = ['all']

    use_cache = request.args.get('cache', 'true').lower() == 'true'
    refresh = request.args.get('refresh', 'false').lower() == 'true'

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

    articles = get_all_articles(categories=categories if 'all' not in categories else None)
    articles = process_articles(articles)

    cache['articles'] = articles
    cache['last_update'] = now

    return jsonify({
        'success': True,
        'data': articles,
        'cached': False,
        'last_update': now.strftime('%Y-%m-%d %H:%M:%S')
    })


# ==================== AI配置管理 API ====================

@app.route('/api/ai-configs', methods=['GET'])
def get_ai_configs():
    """获取所有AI配置"""
    return jsonify({
        'success': True,
        'data': translator.config_manager.get_all_configs()
    })


@app.route('/api/ai-configs', methods=['POST'])
def add_ai_config():
    """添加AI配置"""
    data = request.get_json() or {}
    name = data.get('name', '').strip()
    api_key = data.get('api_key', '').strip()
    base_url = data.get('base_url', '').strip()
    model = data.get('model', '').strip()

    if not all([name, api_key, base_url, model]):
        return jsonify({'success': False, 'message': '所有字段都不能为空'}), 400

    try:
        result = translator.config_manager.add_config(name, api_key, base_url, model)
        translator.reload_config()
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/ai-configs/<config_id>', methods=['PUT'])
def update_ai_config(config_id):
    """更新AI配置"""
    data = request.get_json() or {}
    try:
        success = translator.config_manager.update_config(
            config_id,
            name=data.get('name'),
            api_key=data.get('api_key'),
            base_url=data.get('base_url'),
            model=data.get('model')
        )
        if success:
            translator.reload_config()
            return jsonify({'success': True})
        return jsonify({'success': False, 'message': '配置不存在'}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/ai-configs/<config_id>', methods=['DELETE'])
def delete_ai_config(config_id):
    """删除AI配置"""
    try:
        success = translator.config_manager.delete_config(config_id)
        if success:
            translator.reload_config()
            return jsonify({'success': True})
        return jsonify({'success': False, 'message': '无法删除默认配置或配置不存在'}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/ai-configs/<config_id>/activate', methods=['POST'])
def activate_ai_config(config_id):
    """激活AI配置"""
    try:
        success = translator.config_manager.switch_config(config_id)
        if success:
            translator.reload_config()
            cache['articles'] = []  # 清空缓存
            cache['last_update'] = None
            return jsonify({'success': True})
        return jsonify({'success': False, 'message': '配置不存在'}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# ==================== 其他API ====================

@app.route('/api/sources', methods=['GET'])
def get_sources():
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
    categories = [
        {'id': 'ai', 'name': 'AI人工智能', 'icon': '🤖'},
        {'id': 'semiconductor', 'name': '半导体', 'icon': '💻'},
        {'id': 'energy', 'name': '新能源', 'icon': '⚡'},
        {'id': 'other', 'name': '其他科技', 'icon': '📱'}
    ]
    return jsonify({'success': True, 'data': categories})


@app.route('/api/health', methods=['GET'])
def health_check():
    active_config = translator.config_manager.get_active_config()
    return jsonify({
        'success': True,
        'message': 'Tech News Aggregator is running',
        'ai_configured': translator.is_configured(),
        'current_model': translator.get_current_model(),
        'has_default_config': len(translator.config_manager.configs) > 0
    })


# ==================== Vercel入口 ====================

handler = app

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
