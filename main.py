from quart import Quart, request, Response
from quart_cors import cors
import json
import asyncio
from agent import MCPAgent

app = Quart(__name__)
app = cors(app)

agent = MCPAgent()


@app.before_serving
async def startup():
    global agent
    await agent.init_connection()


@app.route('/api/chat', methods=['POST'])
async def chat():
    """
        浏览器 POST 数据过来后，这个 view 立即返回一个
        Content-Type: text/event-stream 的 Response。
        之后所有 `yield` 都会被推到同一条连接。
        """
    data = await request.get_json()
    message = data.get("message", "")
    session_id = data.get("session_id", "11111")

    async def event_gen():
        async for event in agent.handle_request(session_id, message):
            # SSE 规范：每条消息必须以 \n\n 结尾，并以 "data: " 开头
            yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"
            await asyncio.sleep(0)  # 等价 flush，让框架立刻发出去

    # 关键：把生成器包进 Response，并声明 text/event-stream
    return Response(event_gen(),
                    content_type="text/event-stream",
                    headers={"Cache-Control": "no-cache"})
    # data = await request.get_json()
    # message = data.get('message', '')
    # session_id = data.get('session_id', '11111')
    #
    # async def generate():
    #     async for event in agent.handle_request(session_id, message):
    #         yield f"{json.dumps(event, ensure_ascii=False)}\n\n"
    #
    # return Response(generate(), mimetype='application/x-ndjson')


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000)