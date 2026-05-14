# 科技资讯聚合器

一个自动聚合国内外科技资讯的网页工具，支持用户自定义AI翻译服务。

## 功能特点

- 📰 **多源聚合**: 整合雷锋网、36氪、TechCrunch、The Verge、MIT Technology Review等科技媒体
- 🤖 **AI翻译**: 支持用户自定义任何OpenAI兼容的AI服务
- 📝 **智能总结**: AI自动提取关键要点
- 🏷️ **赛道分类**: 自动识别AI、半导体、新能源等热门赛道
- 🔄 **自动刷新**: 支持可调间隔的自动更新
- 📱 **响应式设计**: 支持桌面和移动端

## 数据源

| 媒体 | 类型 | 说明 |
|------|------|------|
| 雷锋网 | 国内 | 人工智能与科技创新 |
| 36氪 | 国内 | 科技创投与商业 |
| TechCrunch | 国外 | 全球科技新闻 |
| The Verge | 国外 | 科技与生活方式 |
| MIT Technology Review | 国外 | MIT科技评论 |

## 本地运行

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置AI服务（可选）

复制 `.env.example` 为 `.env` 并填入你的AI服务配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```
# 可选：默认AI配置，启动时会自动加载
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-3.5-turbo
```

**注意**：AI配置完全可以在网页界面中添加和管理，环境变量配置是可选的。

### 3. 运行应用

```bash
python app.py
```

访问 http://localhost:5000

## AI服务配置

在网页端点击 **"AI配置"** 按钮，可以：

1. **添加配置**: 输入配置名称、API端点、API Key、模型名称
2. **编辑配置**: 修改已有配置的参数
3. **删除配置**: 删除不需要的配置
4. **激活配置**: 切换当前使用的AI服务

### 支持的AI服务商示例

| 服务商 | API端点 | 模型示例 |
|--------|---------|----------|
| OpenAI | `https://api.openai.com/v1` | `gpt-4o-mini`, `gpt-3.5-turbo` |
| 阿里百炼 | `https://dashscope.aliyuncs.com/compatible-mode/v1` | `qwen-plus`, `qwen-turbo` |
| DeepSeek | `https://api.deepseek.com/v1` | `deepseek-chat` |
| 智谱AI | `https://open.bigmodel.cn/api/paas/v4` | `glm-4` |
| 其他OpenAI兼容服务 | 根据服务商文档 | 根据服务商文档 |

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

3. 设置环境变量（可选）：
在Vercel Dashboard中设置：
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

### AI配置管理
```
GET    /api/ai-configs              # 获取所有配置
POST   /api/ai-configs              # 添加配置
PUT    /api/ai-configs/{id}         # 更新配置
DELETE /api/ai-configs/{id}         # 删除配置
POST   /api/ai-configs/{id}/activate # 激活配置
```

### 其他接口
```
GET /api/sources      # 获取数据源列表
GET /api/categories   # 获取分类列表
GET /api/health       # 健康检查
```

## 项目结构

```
tech-news-aggregator/
├── app.py                 # Flask主应用
├── requirements.txt       # Python依赖
├── vercel.json           # Vercel配置
├── .env.example          # 环境变量示例
├── README.md             # 使用说明
├── crawlers/             # 爬虫模块
│   ├── base_crawler.py   # 爬虫基类
│   ├── leiphone_crawler.py   # 雷锋网
│   ├── kr36_crawler.py       # 36氪
│   ├── techcrunch_crawler.py # TechCrunch
│   ├── theverge_crawler.py   # The Verge
│   └── mit_crawler.py        # MIT Tech Review
├── services/             # 服务模块
│   └── translator.py     # AI翻译服务
└── templates/            # 前端模板
    └── index.html
```

## License

MIT
