# 科技资讯聚合器

一个自动聚合国内外科技资讯的网页工具，支持AI翻译和智能总结。

## 功能特点

- 📰 **多源聚合**: 整合雷锋网、36氪、TechCrunch、The Verge、MIT Technology Review等科技媒体
- 🤖 **AI翻译**: 国外资讯自动翻译为中文
- 📝 **智能总结**: AI自动提取关键要点
- 🏷️ **赛道分类**: 自动识别AI、半导体、新能源等热门赛道
- 🔄 **自动刷新**: 支持可调间隔的自动更新
- 📱 **响应式设计**: 支持桌面和移动端

## 本地运行

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并填入你的AI服务配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-3.5-turbo
```

支持任何OpenAI兼容的API服务（如DeepSeek、通义千问等）。

### 3. 运行应用

```bash
python app.py
```

访问 http://localhost:5000

## 部署到Vercel

### 方法一：通过Vercel CLI

1. 安装Vercel CLI：
```bash
npm install -g vercel
```

2. 登录并部署：
```bash
vercel login
vercel
```

3. 设置环境变量：
在Vercel Dashboard中设置以下环境变量：
- `OPENAI_API_KEY`
- `OPENAI_BASE_URL`
- `OPENAI_MODEL`

### 方法二：通过GitHub

1. 将代码推送到GitHub仓库
2. 在Vercel中导入该仓库
3. 配置环境变量
4. 部署

## API接口

### 获取文章列表
```
GET /api/articles?category=ai&refresh=false
```

参数：
- `category`: 分类筛选 (ai/semiconductor/energy/other/all)
- `refresh`: 是否强制刷新 (true/false)

### 获取数据源列表
```
GET /api/sources
```

### 获取分类列表
```
GET /api/categories
```

### 健康检查
```
GET /api/health
```

## 项目结构

```
tech-news-aggregator/
├── app.py                 # Flask主应用
├── requirements.txt       # Python依赖
├── vercel.json           # Vercel配置
├── .env.example          # 环境变量示例
├── crawlers/             # 爬虫模块
│   ├── base_crawler.py   # 爬虫基类
│   ├── leiphone_crawler.py
│   ├── kr36_crawler.py
│   ├── techcrunch_crawler.py
│   ├── theverge_crawler.py
│   └── mit_crawler.py
├── services/             # 服务模块
│   └── translator.py     # AI翻译服务
└── templates/            # 前端模板
    └── index.html
```

## 注意事项

1. 爬虫频率建议设置合理间隔，避免对目标网站造成压力
2. AI翻译需要配置有效的API Key
3. Vercel免费版有函数执行时间限制，建议控制单次爬取数量

## License

MIT
