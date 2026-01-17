# server.py
from fastmcp import FastMCP
from datetime import datetime

# 1. Initialize the MCP server
mcp = FastMCP("Demo Remote Server")

# 2. Define a simple tool
@mcp.tool()
async def get_current_time(timezone: str = "UTC") -> str:
    """
    Returns the current server time.
    :param timezone: The timezone string (default 'UTC')
    """
    now = datetime.now().isoformat()
    return f"The current time in {timezone} is {now}"

# 3. Entry point for running as a remote SSE server
if __name__ == "__main__":
    # Using 'sse' transport makes it accessible over HTTP
    mcp.run(transport="sse")