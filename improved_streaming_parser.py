import json
from typing import List, Dict, Any, Optional

class ImprovedStreamParser:
    def __init__(self):
        self.buffer = ""
        self.current_state = None
        self.json_start_pos = -1
        self.brace_count = 0
        self.in_json = False
        self.in_string = False
        self.escape_next = False
        
    def parse_chunk(self, chunk: str) -> List[Dict[str, Any]]:
        """解析新的chunk并返回事件列表"""
        if not chunk:
            return []
            
        self.buffer += chunk
        events = []
        
        # 逐字符处理新增内容
        start_pos = len(self.buffer) - len(chunk)
        for i in range(start_pos, len(self.buffer)):
            char = self.buffer[i]
            event = self._process_char(char, i)
            if event:
                events.append(event)
                
        return events
    
    def _process_char(self, char: str, pos: int) -> Optional[Dict[str, Any]]:
        """处理单个字符"""
        # 处理字符串内的转义
        if self.escape_next:
            self.escape_next = False
            return None
            
        # 如果还没开始JSON，寻找状态标识
        if not self.in_json:
            # 查找JSON格式：{"state": "xxx", "content": ...}
            if char == '{':
                # 开始JSON
                self.in_json = True
                self.json_start_pos = pos
                self.brace_count = 1
                return None
                
        # 如果在JSON中，追踪大括号（考虑字符串内的大括号）
        elif self.in_json:
            # 处理转义字符
            if char == '\\' and not self.escape_next:
                self.escape_next = True
                return None
                
            # 处理字符串边界
            if char == '"' and not self.escape_next:
                self.in_string = not self.in_string
                return None
                
            # 只在非字符串中计算大括号
            if not self.in_string:
                if char == '{':
                    self.brace_count += 1
                elif char == '}':
                    self.brace_count -= 1
                    
                    # JSON完整了
                    if self.brace_count == 0:
                        json_str = self.buffer[self.json_start_pos:pos+1]
                        event = self._parse_complete_json(json_str)
                        
                        # 重置状态
                        self.in_json = False
                        self.in_string = False
                        self.escape_next = False
                        self.json_start_pos = -1
                        
                        # 清理已处理的内容（可选，节省内存）
                        # self.buffer = self.buffer[pos+1:]
                        
                        return event
        
        return None
    
    def _parse_complete_json(self, json_str: str) -> Dict[str, Any]:
        """解析完整的JSON并转换为事件"""
        try:
            data = json.loads(json_str)
            
            # 适配原始格式：{"state": "ThinkTool", "content": {...}}
            state = data.get("state", data.get("State", "unknown"))
            content = data.get("content", data.get("Content", ""))
            
            # 根据状态类型发送对应的事件
            if state == "ThinkTool":
                tool_info = content if isinstance(content, dict) else {}
                return {
                    "type": "TOOL_CALL_START",
                    "tool": tool_info.get("ThinkTool", ""),
                    "input": tool_info.get("ThinkInput", ""),
                    "raw": data
                }
                
            elif state == "ThinkOutput":
                return {
                    "type": "TEXT_MESSAGE_CONTENT",
                    "content": content,
                    "category": "thought",
                    "raw": data
                }
                
            elif state == "ThinkRiskAssess":
                return {
                    "type": "RISK_ASSESSMENT",
                    "content": content,
                    "raw": data
                }
                
            elif state == "User Interaction Needed":
                return {
                    "type": "USER_INTERACTION_REQUIRED",
                    "content": content,
                    "category": "interaction",
                    "raw": data
                }
                
            # 兼容原始格式
            elif state == "Thought":
                return {
                    "type": "TEXT_MESSAGE_CONTENT",
                    "content": content,
                    "category": "thought",
                    "raw": data
                }
                
            elif state == "Action":
                return {
                    "type": "TOOL_CALL_START", 
                    "tool": data.get("Tool", ""),
                    "input": data.get("Input", {}),
                    "raw": data
                }
                
            elif state == "Observation":
                return {
                    "type": "TOOL_CALL_END",
                    "result": content,
                    "raw": data
                }
                
            elif state == "FinalAnswer":
                return {
                    "type": "TEXT_MESSAGE_CONTENT",
                    "content": content,
                    "category": "final_answer",
                    "raw": data
                }
                
            else:
                return {
                    "type": "UNKNOWN_STATE",
                    "state": state,
                    "content": content,
                    "raw": data
                }
                
        except json.JSONDecodeError as e:
            return {
                "type": "PARSE_ERROR", 
                "error": str(e),
                "raw": json_str
            }

# 使用示例
def demo_streaming():
    """演示流式解析"""
    parser = ImprovedStreamParser()
    
    # 模拟被切分的流
    chunks = [
        '{"state": "Thi',
        'nkTool", "content": {"',
        'ThinkTool": "ThinkPlan", "ThinkInput": "用户请求建立数据库连接"}}',
        '\n{"state": "ThinkOutput", ',
        '"content": "使用默认参数存在安全风险"}',
        '\n{"state": "User ',
        'Interaction Needed", "content": "请提供数据库连接信息"}'
    ]
    
    print("流式解析演示：")
    print("=" * 60)
    
    for i, chunk in enumerate(chunks):
        print(f"\nChunk {i+1}: {repr(chunk)}")
        events = parser.parse_chunk(chunk)
        
        for event in events:
            print(f"\n触发事件: {event['type']}")
            if event['type'] == 'TOOL_CALL_START':
                print(f"  工具: {event['tool']}")
                print(f"  输入: {event['input']}")
            elif event['type'] == 'TEXT_MESSAGE_CONTENT':
                print(f"  类别: {event['category']}")
                print(f"  内容: {event['content']}")
            elif event['type'] == 'USER_INTERACTION_REQUIRED':
                print(f"  内容: {event['content']}")

# 与OpenAI集成的完整示例
def integrate_with_openai(prompt: str):
    """与OpenAI API集成的完整示例"""
    from openai import OpenAI
    
    client = OpenAI(
        api_key="sk-6996164597154fc7ad1ca0a5c6544e89",
        base_url="https://api.deepseek.com/v1"
    )
    
    parser = ImprovedStreamParser()
    
    # 创建流式响应
    response = client.chat.completions.create(
        model="deepseek-reasoner",
        messages=[{"role": "user", "content": prompt}],
        stream=True
    )
    
    # 处理流式响应
    for chunk in response:
        if chunk.choices[0].delta.content:
            events = parser.parse_chunk(chunk.choices[0].delta.content)
            
            for event in events:
                # 根据事件类型执行相应操作
                if event['type'] == 'TOOL_CALL_START':
                    print(f"🛠️ 调用工具: {event['tool']}")
                    # 可以在这里触发实际的工具调用
                    
                elif event['type'] == 'TEXT_MESSAGE_CONTENT':
                    if event['category'] == 'thought':
                        print(f"💭 思考: {event['content']}")
                    elif event['category'] == 'final_answer':
                        print(f"✅ 最终答案: {event['content']}")
                        
                elif event['type'] == 'USER_INTERACTION_REQUIRED':
                    print(f"👤 需要用户输入: {event['content']}")
                    # 可以在这里暂停并等待用户输入
                    
                elif event['type'] == 'RISK_ASSESSMENT':
                    print(f"⚠️ 风险评估: {event['content']}")

if __name__ == "__main__":
    demo_streaming()