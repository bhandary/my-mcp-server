from fastapi import FastAPI, Request
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.types import Tool, TextContent

app = FastAPI()
mcp_server = Server("my-remote-server")

# Define a sample tool
@mcp_server.list_tools()
async def handle_list_tools():
    return [
        Tool(
            name="get_weather",
            description="Get the current weather for a city",
            inputSchema={
                "type": "object",
                "properties": {
                    "city": {"type": "string"}
                },
                "required": ["city"]
            }
        )
    ]

@mcp_server.call_tool()
async def handle_call_tool(name, arguments):
    if name == "get_weather":
        city = arguments.get("city", "Unknown")
        return [TextContent(type="text", text=f"The weather in {city} is sunny and 25°C.")]
    raise ValueError(f"Tool not found: {name}")

# MCP Transport Routes
sse = SseServerTransport("/messages")

@app.get("/sse")
async def handle_sse(request: Request):
    async with sse.connect_sse(request.scope, request.receive, request._send) as (read_stream, write_stream):
        await mcp_server.run(read_stream, write_stream, mcp_server.create_initialization_options())

@app.post("/messages")
async def handle_messages(request: Request):
    await sse.handle_post_message(request.scope, request.receive, request._send)