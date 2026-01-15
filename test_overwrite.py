from mcp.server.fastmcp import FastMCP
import asyncio

mcp = FastMCP("Test")

@mcp.tool()
def my_tool():
    """Original"""
    return "original"

print(f"Tools before overwrite: {[t.name for t in mcp._tool_manager.list_tools()]}")

@mcp.tool()
def my_tool():
    """Overwritten"""
    return "overwritten"

print(f"Tools after overwrite: {[t.name for t in mcp._tool_manager.list_tools()]}")

async def run():
    # Execute the tool to see which one runs
    result = await mcp.call_tool("my_tool", {})
    print(f"Result: {result}")

if __name__ == "__main__":
    asyncio.run(run())
