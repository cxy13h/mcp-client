import json
from openai import OpenAI
from typing import Generator, Dict, Any, Optional

class StreamingJSONParser:
    def __init__(self):
        self.buffer = ""
        
    def parse_streaming_response(self, response) -> Generator[Dict[str, Any], None, None]:
        """解析流式响应并生成完整的JSON对象"""
        for chunk in response:
            if chunk.choices[0].delta.content:
                self.buffer += chunk.choices[0].delta.content
                
                # 尝试解析完整的JSON行
                while '\n' in self.buffer:
                    line, self.buffer = self.buffer.split('\n', 1)
                    line = line.strip()
                    
                    if line:
                        try:
                            json_obj = json.loads(line)
                            yield json_obj
                        except json.JSONDecodeError:
                            # 如果解析失败，可能是不完整的JSON，放回buffer
                            self.buffer = line + '\n' + self.buffer
                            break
        
        # 处理最后可能剩余的内容
        if self.buffer.strip():
            try:
                json_obj = json.loads(self.buffer.strip())
                yield json_obj
            except json.JSONDecodeError:
                print(f"Warning: Unable to parse remaining buffer: {self.buffer}")