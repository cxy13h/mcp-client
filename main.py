import asyncio
import json
from typing import Optional, List, Dict, Any
from contextlib import AsyncExitStack
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from mcp.types import Tool
from openai import OpenAI
import improved_streaming_parser
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
        print(f"   参数: {arguments}")
        try:
            response = await self.session.call_tool(tool_name, arguments)
            print(f"✅ 工具调用成功!")
            print(f"   响应: {response}")
            return response
        except Exception as e:
            print(f"❌ 工具调用失败: {e}")
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
        llm_client = OpenAI(api_key="sk-6996164597154fc7ad1ca0a5c6544e89", base_url="https://api.deepseek.com/v1")
        state_file = open("state.txt", "w", encoding="utf-8")
        content_file = open("content.txt", "w", encoding="utf-8")
        response = llm_client.chat.completions.create(
            model="deepseek-reasoner",
            messages=[{"role":"user", "content":prompt}],
            stream=True
        )
        last_state=''
        for event_type, key, content in Util.parse_json_stream_by_chunks(Util.parse_llm_stream(response)):
            if event_type == "key_complete":
                print(f"\n[{key}]: ", end="", flush=True)
                if(key=="state"):
                    last_state=content
            
            elif event_type == "value_chunk":
                # 输出整个chunk，而不是单个字符
                print(content, end="", flush=True)
            
            elif event_type == "value_complete":
                print()  # 换行
        print(f"\n最后的状态是{last_state}")
    except Exception as e:
        print(f"程序运行出现严重错误: {e}")
    finally:
        state_file.close()
        content_file.close()
        # --- 确保最后断开连接 ---
        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
