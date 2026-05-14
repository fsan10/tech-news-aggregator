"""
AI翻译和总结服务 - 通用自定义配置
支持用户自定义任何OpenAI兼容的AI服务
"""
import os
import json
from typing import Dict, List, Optional
from openai import OpenAI


class AIConfig:
    """AI配置管理"""
    
    def __init__(self):
        self.configs: List[Dict] = []
        self.active_config_id: Optional[str] = None
        self._load_default_config()
    
    def _load_default_config(self):
        """从环境变量加载默认配置"""
        api_key = os.getenv('OPENAI_API_KEY', '')
        base_url = os.getenv('OPENAI_BASE_URL', '')
        model = os.getenv('OPENAI_MODEL', '')
        
        if api_key and base_url and model:
            self.configs.append({
                'id': 'default',
                'name': '默认配置',
                'api_key': api_key,
                'base_url': base_url,
                'model': model
            })
            self.active_config_id = 'default'
    
    def get_all_configs(self) -> List[Dict]:
        """获取所有配置（隐藏API Key）"""
        return [
            {
                'id': c['id'],
                'name': c['name'],
                'base_url': c['base_url'],
                'model': c['model'],
                'is_active': c['id'] == self.active_config_id
            }
            for c in self.configs
        ]
    
    def get_active_config(self) -> Optional[Dict]:
        """获取当前激活的配置"""
        for config in self.configs:
            if config['id'] == self.active_config_id:
                return config
        return None
    
    def add_config(self, name: str, api_key: str, base_url: str, model: str) -> Dict:
        """添加新配置"""
        import uuid
        config_id = str(uuid.uuid4())[:8]
        self.configs.append({
            'id': config_id,
            'name': name,
            'api_key': api_key,
            'base_url': base_url,
            'model': model
        })
        if len(self.configs) == 1:
            self.active_config_id = config_id
        return {'id': config_id, 'name': name, 'base_url': base_url, 'model': model}
    
    def update_config(self, config_id: str, **kwargs) -> bool:
        """更新配置"""
        for config in self.configs:
            if config['id'] == config_id:
                for key in ['name', 'api_key', 'base_url', 'model']:
                    if key in kwargs and kwargs[key]:
                        config[key] = kwargs[key]
                return True
        return False
    
    def delete_config(self, config_id: str) -> bool:
        """删除配置"""
        if config_id == 'default':
            return False
        for i, config in enumerate(self.configs):
            if config['id'] == config_id:
                self.configs.pop(i)
                if self.active_config_id == config_id:
                    self.active_config_id = self.configs[0]['id'] if self.configs else None
                return True
        return False
    
    def switch_config(self, config_id: str) -> bool:
        """切换激活的配置"""
        for config in self.configs:
            if config['id'] == config_id:
                self.active_config_id = config_id
                return True
        return False


class AITranslator:
    """AI翻译和总结服务 - 通用版"""
    
    def __init__(self):
        self.config_manager = AIConfig()
        self.client: Optional[OpenAI] = None
        self._init_client()
    
    def _init_client(self):
        """根据当前配置初始化客户端"""
        config = self.config_manager.get_active_config()
        if config:
            try:
                self.client = OpenAI(api_key=config['api_key'], base_url=config['base_url'])
            except Exception as e:
                print(f"[AI翻译] 初始化失败: {e}")
                self.client = None
    
    def is_configured(self) -> bool:
        return self.client is not None
    
    def get_current_model(self) -> str:
        config = self.config_manager.get_active_config()
        return config['model'] if config else ''
    
    def reload_config(self):
        self._init_client()
    
    def _parse_json_response(self, result_text: str) -> dict:
        text = result_text.strip()
        if text.startswith('```'):
            parts = text.split('\n', 1)
            if len(parts) > 1:
                text = parts[1].rsplit('```', 1)[0]
        return json.loads(text)
    
    def translate_and_summarize(self, title: str, content: str = "", source: str = "") -> Dict:
        if not self.is_configured():
            return {'translated_title': title, 'chinese_summary': content[:200] if content else "", 'key_points': [], 'error': 'AI服务未配置'}
        
        config = self.config_manager.get_active_config()
        model = config['model'] if config else 'gpt-3.5-turbo'
        
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
                model=model,
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
        except Exception as e:
            print(f"[AI翻译] 错误: {e}")
            return {'translated_title': title, 'chinese_summary': content[:200] if content else "", 'key_points': [], 'error': str(e)}
    
    def summarize_chinese(self, title: str, content: str = "") -> Dict:
        if not self.is_configured():
            return {'summary': content[:150] if content else "", 'key_points': [], 'error': 'AI服务未配置'}
        
        config = self.config_manager.get_active_config()
        model = config['model'] if config else 'gpt-3.5-turbo'
        
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
                model=model,
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
        except Exception as e:
            print(f"[AI总结] 错误: {e}")
            return {'summary': content[:150] if content else "", 'key_points': [], 'error': str(e)}
