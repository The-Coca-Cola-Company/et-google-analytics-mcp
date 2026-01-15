from mcp.server.fastmcp import FastMCP
import asyncio

mcp = FastMCP("Test")

@mcp.tool()
def my_tool():
    """Original"""
    return "original"

# Try to remove it
try:
    print("Attempting to remove 'my_tool'...")
    # Accessing internal dictionary - structure assumed based on previous tool output
    if hasattr(mcp, "_tool_manager"):
         if hasattr(mcp._tool_manager, "_tools"):
             del mcp._tool_manager._tools["my_tool"]
             print("Removed from _tools dict.")
         else:
             print("_tool_manager has no _tools attribute")
    else:
        print("mcp has no _tool_manager attribute")

except Exception as e:
    print(f"Failed to remove: {e}")

# Re-register
@mcp.tool()
def my_tool():
    """Overwritten"""
    return "overwritten"

async def run():
    # Execute the tool to see which one runs
    # Note: call_tool fetches from the manager, so if we swapped it in the dict, it should work.
    try:
        result = await mcp.call_tool("my_tool", {})
        print(f"Result: {result}")
    except Exception as e:
        print(f"Call failed: {e}")

if __name__ == "__main__":
    asyncio.run(run())
