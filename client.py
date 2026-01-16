import asyncio
from mcp import ClientSession
from mcp.client.sse import sse_client

async def run_remote_test():
    # Replace with your actual Railway URL
    url = "https://my-mcp-server-production-1900.up.railway.app/sse"
    
    async with sse_client(url) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            # Initialize
            await session.initialize()
            
            # List tools
            tools = await session.list_tools()
            print(f"Available Tools: {tools}")

            # Call the tool
            result = await session.call_tool("get_weather", arguments={"city": "San Jose"})
            print(f"Result: {result.content[0].text}")

if __name__ == "__main__":
    asyncio.run(run_remote_test())