# Google Analytics MCP Server

This repository provides a [Model Context Protocol (MCP)](https://modelcontextprotocol.io) server that allows LLMs to interact with [Google Analytics](https://support.google.com/analytics) via the Google Analytics Admin and Data APIs.

## Overview

The server exposes several tools that enable Gemini (or other MCP-compatible clients) to:
- Retrieve account and property summaries.
- List links to Google Ads accounts.
- Get detailed property information.
- Run core reports for data analysis.
- Run realtime reports for live updates.
- Manage custom dimensions and metrics.

## Setup

### Prerequisites
- Python 3.10 or higher.
- [pipx](https://pipx.pypa.io/stable/#install-pipx) installed.
- A Google Cloud project with the following APIs enabled:
  - [Google Analytics Admin API](https://console.cloud.google.com/apis/library/analyticsadmin.googleapis.com)
  - [Google Analytics Data API](https://console.cloud.google.com/apis/library/analyticsdata.googleapis.com)

### Authentication
The server uses [Application Default Credentials (ADC)](https://cloud.google.com/docs/authentication/provide-credentials-adc). You must configure credentials for a user with access to the target Google Analytics accounts.

Example command to log in:
```bash
gcloud auth application-default login \
  --scopes https://www.googleapis.com/auth/analytics.readonly,https://www.googleapis.com/auth/cloud-platform \
  --client-id-file=YOUR_CLIENT_JSON_FILE
```

### Configuration in Gemini
Add the following to your `~/.gemini/settings.json` file:

```json
{
  "mcpServers": {
    "analytics-mcp": {
      "command": "pipx",
      "args": [
        "run",
        "analytics-mcp"
      ],
      "env": {
        "GOOGLE_APPLICATION_CREDENTIALS": "PATH_TO_CREDENTIALS_JSON",
        "GOOGLE_PROJECT_ID": "YOUR_PROJECT_ID"
      }
    }
  }
}
```

## Core Components

- **[server.py](file:///c:/Users/Z22431/OneDrive - The Coca-Cola Company/Documents/_Phani/Github Repos/MCP servers/et-google-analytics-mcp/analytics_mcp/server.py)**: The entry point of the application. It initializes the MCP server and registers tools.
- **[coordinator.py](file:///c:/Users/Z22431/OneDrive - The Coca-Cola Company/Documents/_Phani/Github Repos/MCP servers/et-google-analytics-mcp/analytics_mcp/coordinator.py)**: Defines the singleton `FastMCP` instance used for tool registration.
- **[tools/](file:///c:/Users/Z22431/OneDrive - The Coca-Cola Company/Documents/_Phani/Github Repos/MCP servers/et-google-analytics-mcp/analytics_mcp/tools/)**: Contains tool implementations categorized by API.
  - **[admin/info.py](file:///c:/Users/Z22431/OneDrive - The Coca-Cola Company/Documents/_Phani/Github Repos/MCP servers/et-google-analytics-mcp/analytics_mcp/tools/admin/info.py)**: Tools for account and property management using the Admin API.
  - **[reporting/core.py](file:///c:/Users/Z22431/OneDrive - The Coca-Cola Company/Documents/_Phani/Github Repos/MCP servers/et-google-analytics-mcp/analytics_mcp/tools/reporting/core.py)**: Tools for running standard reports using the Data API.
  - **[reporting/realtime.py](file:///c:/Users/Z22431/OneDrive - The Coca-Cola Company/Documents/_Phani/Github Repos/MCP servers/et-google-analytics-mcp/analytics_mcp/tools/reporting/realtime.py)**: Tools for running realtime reports.
  - **[utils.py](file:///c:/Users/Z22431/OneDrive - The Coca-Cola Company/Documents/_Phani/Github Repos/MCP servers/et-google-analytics-mcp/analytics_mcp/tools/utils.py)**: Shared utilities for client creation, resource name construction, and proto-to-dict conversion.

## Available Tools

### Account and Property Info
- `get_account_summaries`: Lists all accounts and properties accessible to the user.
- `get_property_details`: Retrieves configuration details for a specific property.
- `list_google_ads_links`: Displays Google Ads accounts linked to a property.

### Data Reporting
- `run_report`: Executes complex queries against historical GA4 data. Supports dimensions, metrics, filters, and ordering.
- `run_realtime_report`: Executes queries against realtime data (usually last 30 minutes).

### Metadata
- `get_custom_dimensions_and_metrics`: Lists available custom fields for a specific property.

## Usage Sample Prompts

- "What can the analytics-mcp server do?"
- "Give me details about my Google Analytics property with 'marketing' in the name."
- "What are the most popular events in my property in the last 30 days?"
- "Show me the realtime visitor count for my property."
