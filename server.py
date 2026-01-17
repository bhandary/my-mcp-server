from mcp.server.fastmcp import FastMCP

mcp = FastMCP(name="Tool Example")


@mcp.tool()
def sum(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b


@mcp.tool()
def get_weather(city: str, unit: str = "celsius") -> str:
    """Get weather for a city."""
    # This would normally call a weather API
    return f"Weather in {city}: 22degrees{unit[0].upper()}"

# 2. Extract the ASGI app for the production server
# FastMCP uses Starlette under the hood for HTTP/SSE
app = mcp.get_asgi_app()

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    # Note: We point uvicorn to "server:app" (the ASGI app) 
    # instead of running mcp.run() directly
    uvicorn.run(app, host="0.0.0.0", port=port)