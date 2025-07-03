from contextlib import AsyncExitStack
from typing import Optional, List, Any, Dict
from mcp.types import Tool
from mcp.client.streamable_http import streamablehttp_client
import Util
from mcp import ClientSession


class MCPClient:
    def __init__(self):
        # 初始化会话和客户端对象
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.tools = []

    async def connect(self, server_url: str):
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

        except Exception as e:
            print(f"❌ 连接失败: {e}")
            await self.disconnect()  # 连接失败时也尝试清理资源
            raise

    async def disconnect(self):
        if self.session:
            await self.exit_stack.aclose()
            self.session = None

    async def list_tools(self) -> List[Tool]:
        if not self.session:
            print("❌尚未连接到服务器。")
            return []

        response = await self.session.list_tools()
        tools = response.tools
        return tools

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        if not self.session:
            print("❌ 尚未连接到服务器。")
            return None
        try:
            response = await self.session.call_tool(tool_name, arguments)
            return response.content[0].text
        except Exception as e:
            print(f"❌ 工具调用失败:\n {e}  \n -----------------\n")
            return None

    async def init_tools(self):
        if not self.session:
            print("❌尚未连接到服务器。")
            return []
        self.tools=[]
        response = await self.session.list_tools()
        tools = response.tools
        for tool in tools:
            self.tools.append(Util.format_tool(tool.__dict__))