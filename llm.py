import os
from openai import OpenAI
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class LLMClient:
    """简洁的LLM客户端封装类"""
    
    def __init__(self):
        self.api_key = os.getenv("LLM_API_KEY")
        self.base_url = os.getenv("LLM_BASE_URL")
        self.model = os.getenv("LLM_MODEL")
        self._client = None
    
    @property
    def client(self) -> OpenAI:
        """延迟初始化OpenAI客户端"""
        if self._client is None:
            self._client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
        return self._client
    
    def invoke(self, prompt: str, stream: bool = True):
        """调用LLM并返回响应流"""
        return self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            stream=stream
        )

