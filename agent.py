import asyncio
import json
import os
from typing import Dict, Any, Optional, Generator
from dotenv import load_dotenv

import Util
from llm import LLMClient
from mcp_client import MCPClient

load_dotenv()


class MCPAgent:
    """MCP智能代理封装类"""
    
    def __init__(self):
        self.mcp_client = MCPClient()
        self.llm_client = LLMClient()
        self.server_url = os.getenv("MCP_SERVER_URL")
        self.initial_prompt=""
        self.session_map = {}

    async def init_connection(self):
        """初始化MCP客户端连接"""
        try:
            await self.mcp_client.connect(self.server_url)
            await self.mcp_client.init_tools()
            self.initial_prompt = Util.get_final_prompt(self.mcp_client.tools)
        except Exception as e:
            print(f"❌ MCP客户端连接初始化失败: {e}")

    def get_session_prompt(self, sessionId: str) -> str:
        if sessionId not in self.session_map:
            self.session_map[sessionId] = self.initial_prompt

        return self.session_map[sessionId]

    # ===== 单次invoke的流式版本 =====
    def invoke_stream(self, sessionId: str, prompt: str) -> Generator[Dict[str, Any], None, None]:
        """
        流式版本的invoke函数

        Yields:
            流式事件，最后通过invoke_result事件返回完整结果
        """
        response = self.llm_client.invoke(prompt)

        last_state = None
        last_content = None

        for event_type, key, value in Util.parse_json_stream_by_chunks(Util.parse_llm_stream(response)):
            if event_type == "key_complete":
                yield {
                    "type": "key_complete",
                    "key": key
                }
            elif event_type == "value_chunk":
                yield {
                    "type": "value_chunk",
                    "key": key,
                    "value": value
                }
            elif event_type == "value_complete":
                if key == "state":
                    last_state = value
                elif key == "content":
                    last_content = value
                    prompt += f"\n{{\"state\": {last_state}, \"content\":{last_content}}}"
                    self.session_map[sessionId] = prompt

                yield {
                    "type": "value_complete",
                    "key": key,
                    "value": value
                }

    # ===== 处理单次请求的函数 =====
    async def handle_request(self, session_id: str, user_input: Optional[str] = None, client=None) -> Generator[
        Dict[str, Any], None, None]:
        """
        处理单次请求，执行循环直到需要用户输入或对话结束

        Args:
            session_id: 会话ID
            user_input: 用户输入
            client: 工具调用客户端

        Yields:
            流式事件
        """
        # 获取或初始化prompt
        prompt = self.get_session_prompt(session_id)

        # 如果有用户输入，追加到prompt
        if user_input is not None:
            prompt += f'\n{{"state": UserInput, "content":\"{user_input}\"}}'
        self.session_map[session_id] = prompt
        # 循环执行invoke，直到需要用户输入或对话结束
        while True:
            last_state = None
            last_content = None

            # 执行一次invoke
            for event in self.invoke_stream(session_id, self.session_map[session_id]):
                if event["type"] == "value_complete":
                    if event["key"] == "state":
                        last_state = event["value"]
                    if event["key"] == "content":
                        last_content = event["value"]
                else:
                    yield event
            # 检查是否需要结束循环
            if last_state == "FinalAnswer":
                # 对话完成，结束循环
                break

            if last_state == "UserInteractionNeeded":
                # 需要用户输入，结束循环，等待下一次请求
                break

            # 如果是Action Input，执行工具后继续循环
            if last_state == "ActionInput":
                try:
                    last_content_json = json.loads(last_content)
                    tool_name = last_content_json["tool_name"]
                    arguments = last_content_json["arguments"]

                    # 执行工具
                    if self.mcp_client:
                        last_content_json = json.loads(last_content)
                        observation = await self.mcp_client.call_tool(last_content_json["tool_name"],last_content_json["arguments"])
                        prompt = self.get_session_prompt(session_id)
                        prompt += f"\n{{\"state\": Observation, \"content\":\"{observation}\"}}"
                        self.session_map[session_id] = prompt

                        yield {
                            "type": "tool_executed",
                            "tool_name": tool_name,
                            "observation": observation
                        }
                        # 继续循环，执行下一次invoke
                except Exception as e:
                    yield {
                        "type": "error",
                        "error": str(e)
                    }
                    break

# 简化的运行方式
async def main():
    agent = MCPAgent()
    try:
        await agent.init_connection()
        # 使用 async for 迭代异步生成器
        async for event in agent.handle_request("1214212412", "你好，你能为我做什么"):
            # print(event)
            pass

    finally:
        # 确保在程序结束前断开连接
        if agent.mcp_client and agent.mcp_client.session:
            await agent.mcp_client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())