import os
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

# Export the ASGI app for uvicorn
app = mcp.get_asgi_app()

# Run with streamable HTTP transport when executed directly
if __name__ == "__main__":
    mcp.run(transport="streamable-http")