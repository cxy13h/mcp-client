import asyncio
import json
import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()


class MCPAgent:
    """MCP智能代理封装类"""
    
    def __init__(self):
        self.client = MCPClient()
        self.server_url = os.getenv("MCP_SERVER_URL")
        self.state_handlers = {
            '"User Interaction Needed"': self._handle_user_interaction,
            '"Action Input"': self._handle_action_input,
            '"Final Answer"': self._handle_final_answer
        }
    
    async def run(self) -> Optional[str]:
        """运行智能代理主循环"""
        try:
            await self.client.connect(self.server_url)
            await self.client.list_tools()
            
            prompt = Util.get_final_prompt(self.client.tools)
            state, content, prompt = Util.invoke(prompt)
            
            while state != '"Final Answer"':
                handler = self.state_handlers.get(state)
                if handler:
                    prompt = await handler(content, prompt)
                else:
                    raise ValueError(f"未知状态: {state}")
                
                state, content, prompt = Util.invoke(prompt)
            
            return content
            
        except Exception as e:
            print(f"程序运行出现严重错误:\n  {e}")
            return None
        finally:
            await self.client.disconnect()
    
    async def _handle_user_interaction(self, content: str, prompt: str) -> str:
        """处理用户交互"""
        print("需要用户交互")
        user_input = input("请输入: ")
        return prompt + f'\n{{"state": "User Input", "content":"{user_input}"}}'
    
    async def _handle_action_input(self, content: str, prompt: str) -> str:
        """处理工具执行"""
        print("需要执行工具")
        params = json.loads(content)
        observation = await self.client.call_tool(
            params["tool_name"], 
            params["arguments"]
        )
        return prompt + f'\n{{"state": "Observation", "content":{json.dumps(observation)}}}'
    
    async def _handle_final_answer(self, content: str, prompt: str) -> str:
        """处理最终答案"""
        return prompt


# 简化的运行方式
async def main():
    agent = MCPAgent()
    result = await agent.run()
    if result:
        print(f"最终结果: {result}")


if __name__ == "__main__":
    asyncio.run(main())