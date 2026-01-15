try:
    import analytics_mcp.impersonated_server
    print("Successfully imported analytics_mcp.impersonated_server")
except Exception as e:
    print(f"Failed to import: {e}")
    import traceback
    traceback.print_exc()
