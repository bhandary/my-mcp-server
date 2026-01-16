import os
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from clerk_backend_api import Clerk

from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.types import Tool, TextContent

# --- Configuration ---
CLERK_SECRET_KEY = os.getenv("CLERK_SECRET_KEY")
CLERK_ISSUER_URL = os.getenv("CLERK_ISSUER_URL")
# The public URL of your Railway app (e.g., https://...up.railway.app)
BASE_URL = os.getenv("RAILWAY_PUBLIC_DOMAIN", "http://localhost:8000")

app = FastAPI()
security = HTTPBearer()
clerk_client = Clerk(bearer_auth=CLERK_SECRET_KEY)
mcp_server = Server("my-remote-server")

# --- Authentication Dependency ---
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        # Validates the session token with Clerk
        request_state = clerk_client.authenticate_request(token)
        if not request_state.is_signed_in:
            raise HTTPException(status_code=401)
        return request_state.user
    except Exception:
        raise HTTPException(status_code=401)

# --- MCP OAuth Metadata (RFC 9728) ---
@app.get("/.well-known/oauth-protected-resource")
async def oauth_metadata():
    return {
        "resource": f"{BASE_URL}/",
        "authorization_servers": [CLERK_ISSUER_URL],
        "scopes_supported": ["openid", "profile", "email"]
    }

# --- MCP 401 Challenge Handler ---
# This tells the MCP client where to find the login metadata
@app.exception_handler(HTTPException)
async def mcp_auth_challenge_handler(request: Request, exc: HTTPException):
    if exc.status_code == 401:
        metadata_url = f"{BASE_URL}/.well-known/oauth-protected-resource"
        return JSONResponse(
            status_code=401,
            content={"detail": "Authentication required"},
            headers={
                "WWW-Authenticate": f'Bearer realm="mcp", resource_metadata="{metadata_url}"'
            }
        )
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

# --- MCP Tool Definitions ---
@mcp_server.list_tools()
async def handle_list_tools():
    return [
        Tool(
            name="get_weather",
            description="Get the current weather for a city",
            inputSchema={
                "type": "object",
                "properties": {"city": {"type": "string"}},
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

# --- MCP Transport Routes ---
sse = SseServerTransport("/messages")

@app.get("/sse", dependencies=[Depends(get_current_user)])
async def handle_sse(request: Request):
    async with sse.connect_sse(request.scope, request.receive, request._send) as (read_stream, write_stream):
        await mcp_server.run(read_stream, write_stream, mcp_server.create_initialization_options())

@app.post("/messages", dependencies=[Depends(get_current_user)])
async def handle_messages(request: Request):
    await sse.handle_post_message(request.scope, request.receive, request._send)