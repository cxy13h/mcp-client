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