try:
    from google.analytics import admin_v1beta
    print("Successfully imported google.analytics.admin_v1beta")
except Exception as e:
    print(f"Failed to import: {e}")
    import traceback
    traceback.print_exc()
