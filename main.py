from quart import Quart, request, Response
from quart_cors import cors
import json
from agent import MCPAgent

app = Quart(__name__)
app = cors(app)

agent = None


@app.before_serving
async def startup():
    global agent
    agent = MCPAgent()
    await agent.init_connection()


@app.route('/api/chat', methods=['POST'])
async def chat():
    data = await request.get_json()
    message = data.get('message', '')
    session_id = data.get('session_id', '11111')

    async def generate():
        async for event in agent.handle_request(session_id, message):
            yield json.dumps(event, ensure_ascii=False)

    return Response(generate(), mimetype='text/plain')


if __name__ == '__main__':
    app.run(debug=True, port=5000)