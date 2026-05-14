"""
AI翻译和总结服务 - 阿里百炼平台
"""
import os
import json
from typing import Dict
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# 百炼平台支持的模型列表
AVAILABLE_MODELS = [
    {'id': 'kimi-k2.6', 'name': 'Kimi K2.6'},
    {'id': 'qwen3.5-flash', 'name': '通义千问3.5 Flash'},
    {'id': 'qwen3.6-plus', 'name': '通义千问3.6 Plus'},
]

# 默认模型
DEFAULT_MODEL = os.getenv('OPENAI_MODEL', 'qwen3.5-flash')


class AITranslator:
    """AI翻译和总结服务 - 基于阿里百炼平台"""

    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY', '')
        self.base_url = os.getenv('OPENAI_BASE_URL', 'https://dashscope.aliyuncs.com/compatible-mode/v1')
        self.model = DEFAULT_MODEL
        self.client = None

        if self.api_key:
            try:
                self.client = OpenAI(
                    api_key=self.api_key,
                    base_url=self.base_url
                )
            except Exception as e:
                print(f"[AI翻译] 初始化失败: {e}")

    def is_configured(self) -> bool:
        return self.client is not None

    def set_model(self, model_id: str):
        """切换模型"""
        self.model = model_id

    def _parse_json_response(self, result_text: str) -> dict:
        """解析AI返回的JSON"""
        text = result_text.strip()
        if text.startswith('```'):
            text = text.split('\n', 1)[1]
            text = text.rsplit('```', 1)[0]
        return json.loads(text)

    def translate_and_summarize(self, title: str, content: str = "", source: str = "") -> Dict:
        """翻译并总结国外科技资讯"""
        if not self.is_configured():
            return {
                'translated_title': title,
                'chinese_summary': content[:200] if content else "",
                'key_points': [],
                'error': 'AI服务未配置'
            }

        try:
            prompt = f"""请对以下英文科技资讯进行翻译和总结：

来源：{source}
标题：{title}
内容：{content[:1000] if content else '无详细内容'}

请按以下JSON格式返回结果（只返回JSON，不要其他内容）：
{{
    "translated_title": "中文翻译标题",
    "chinese_summary": "100-150字的中文摘要，概括核心内容",
    "key_points": ["关键点1", "关键点2", "关键点3"]
}}"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的科技资讯翻译和总结助手。请准确翻译并提炼关键信息。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )

            result_text = response.choices[0].message.content.strip()
            result = self._parse_json_response(result_text)

            return {
                'translated_title': result.get('translated_title', title),
                'chinese_summary': result.get('chinese_summary', ''),
                'key_points': result.get('key_points', [])
            }

        except json.JSONDecodeError:
            return {
                'translated_title': title,
                'chinese_summary': result_text[:200] if 'result_text' in dir() else content[:200],
                'key_points': []
            }
        except Exception as e:
            print(f"[AI翻译] 错误: {e}")
            return {
                'translated_title': title,
                'chinese_summary': content[:200] if content else "",
                'key_points': [],
                'error': str(e)
            }

    def summarize_chinese(self, title: str, content: str = "") -> Dict:
        """总结中文科技资讯"""
        if not self.is_configured():
            return {
                'summary': content[:150] if content else "",
                'key_points': [],
                'error': 'AI服务未配置'
            }

        try:
            prompt = f"""请对以下中文科技资讯进行总结：

标题：{title}
内容：{content[:1000] if content else '无详细内容'}

请按以下JSON格式返回结果（只返回JSON，不要其他内容）：
{{
    "summary": "100-150字的摘要，概括核心内容",
    "key_points": ["关键点1", "关键点2", "关键点3"]
}}"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的科技资讯总结助手。请提炼关键信息。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )

            result_text = response.choices[0].message.content.strip()
            result = self._parse_json_response(result_text)

            return {
                'summary': result.get('summary', ''),
                'key_points': result.get('key_points', [])
            }

        except json.JSONDecodeError:
            return {
                'summary': result_text[:200] if 'result_text' in dir() else content[:150],
                'key_points': []
            }
        except Exception as e:
            print(f"[AI总结] 错误: {e}")
            return {
                'summary': content[:150] if content else "",
                'key_points': [],
                'error': str(e)
            }
