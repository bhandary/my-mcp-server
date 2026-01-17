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
    return f"Weather in {city}: 22degrees{unit[0].upper()}"

if __name__ == "__main__":
    import uvicorn
    # Get the port from environment variable
    port = int(os.environ.get("PORT", 8000))
    
    # Run the server programmatically
    mcp.run(transport="streamable-http", host="0.0.0.0", port=port)