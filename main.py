import asyncio
import json
from typing import Optional, List, Dict, Any
from contextlib import AsyncExitStack
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from mcp.types import Tool
from openai import OpenAI
import Util


class MCPClient:
    def __init__(self):
        # 初始化会话和客户端对象
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.tools = []

    async def connect(self, server_url: str):
        """
        连接到 MCP 服务器并初始化会शन
        """
        print(f"🔗 正在连接到服务器: {server_url}")
        try:
            # --- 关键修改：解包返回的读写流 ---
            read_stream, write_stream, _ = await self.exit_stack.enter_async_context(
                streamablehttp_client(server_url)
            )

            # --- 关键修改：将两个流分别传入 ClientSession ---
            self.session = await self.exit_stack.enter_async_context(
                ClientSession(read_stream, write_stream)
            )

            # 初始化协议握手
            await self.session.initialize()
            print("✅ 服务器连接成功，会话已建立！")

        except Exception as e:
            print(f"❌ 连接失败: {e}")
            await self.disconnect()  # 连接失败时也尝试清理资源
            raise

    async def disconnect(self):
        """
        干净地断开连接并关闭所有资源
        """
        if self.session:
            print("🔌 正在断开连接...")
            await self.exit_stack.aclose()
            self.session = None
            print("🔌 连接已断开。")

    async def list_tools(self) -> List[Tool]:
        """
        列出所有可用的工具
        """
        if not self.session:
            print("❌尚未连接到服务器。")
            return []

        response = await self.session.list_tools()
        tools = response.tools
        for tool in tools:
            toolDescription = Util.format_tool(tool.__dict__)
            self.tools.append(toolDescription)
        return tools

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """
        调用指定的工具
        """
        if not self.session:
            print("❌ 尚未连接到服务器。")
            return None

        print(f"\n🔧 正在调用工具 '{tool_name}'...")
        print(f"   参数:\n  {arguments}")
        try:
            response = await self.session.call_tool(tool_name, arguments)
            print(f"✅ 工具调用成功!")
            print(f"   调用结果:\n  {response.content[0].text}")
            return response.content[0].text
        except Exception as e:
            print(f"❌ 工具调用失败:\n {e}")
            return None


async def main():
    client = MCPClient()
    try:
        # --- 连接服务器 ---
        # 注意：这里的URL应该是服务器的根路径，不需要/mcp/
        await client.connect("http://101.126.145.194:8000/mcp/")

        # --- 列出工具 ---
        await client.list_tools()
        prompt = Util.get_final_prompt(client.tools)
        last_state, last_content, prompt = Util.invoke(prompt)
        print("last_state: " + last_state + " last_content: " + last_content)
        while last_state != '"Final Answer"':
            if last_state == '"User Interaction Needed"':
                print("需要用户交互")
                user_input = input("请输入: ")
                prompt += f"\n{{\"state\": \"User Input\", \"content\":{user_input}}}"
                # print("现在的prompt内容：\n" + prompt)
            elif last_state == '"Action Input"':
                print("需要执行工具")
                last_content_json = json.loads(last_content)
                observation = await client.call_tool(last_content_json["tool_name"], last_content_json["arguments"])
                prompt += f"\n{{\"state\": \"Observation\", \"content\":{observation}}}"
                # print("现在的prompt内容：\n" + prompt)
            last_state, last_content, prompt = Util.invoke(prompt)
    except Exception as e:
        print(f"程序运行出现严重错误:\n  {e}")
    finally:
        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
