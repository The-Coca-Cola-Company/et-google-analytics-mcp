# Copyright 2025 Google LLC All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Impersonation Wrappers for Google Analytics MCP.

This module intercepts the default tool registration and replaces the tools
with wrappers that support user impersonation.
"""

import contextvars
from typing import Any, Dict, List, Optional
import google.auth
from google.auth import impersonated_credentials
from google.oauth2 import service_account

# Import the functionality we need to wrap
from analytics_mcp.coordinator import mcp
from analytics_mcp.tools import utils
# Importing these triggers the original tool registration
from analytics_mcp.tools.admin import info
from analytics_mcp.tools.reporting import core, realtime, metadata

# --- Credential Monkey-Patching ---

# Context variable to store the impersonated email for the current request context.
_impersonated_email_ctx: contextvars.ContextVar[Optional[str]] = (
    contextvars.ContextVar("impersonated_email", default=None)
)

_original_create_credentials = utils._create_credentials

def _create_impersonated_credentials() -> google.auth.credentials.Credentials:
    """Creates credentials, optionally using impersonation if the context var is set."""
    impersonated_email = _impersonated_email_ctx.get()
    creds = _original_create_credentials()

    if impersonated_email:
        if hasattr(creds, "service_account_email") and isinstance(creds, service_account.Credentials):
             return creds.with_subject(impersonated_email)
        
        try:
             return impersonated_credentials.Credentials(
                source_credentials=creds,
                target_principal=impersonated_email,
                target_scopes=[utils._READ_ONLY_ANALYTICS_SCOPE],
                lifetime=3600
            ) 
        except Exception:
             pass
             
    return creds

# Apply the patch immediately upon import
utils._create_credentials = _create_impersonated_credentials


# --- Tool Replacement Helpers ---

def replace_tool(name: str):
    """Decorator to replace an existing tool with a new implementation."""
    def decorator(func):
        # 1. Remove the old tool if it exists
        if hasattr(mcp, "_tool_manager") and hasattr(mcp._tool_manager, "_tools"):
             if name in mcp._tool_manager._tools:
                 del mcp._tool_manager._tools[name]
        
        # 2. Register the new tool using the ORIGINAL name
        # We assume the wrapper function might have a different name (e.g. run_report_wrapper)
        # but we register it as 'run_report'.
        mcp.tool(name=name)(func)
        return func
    return decorator

def set_context(email: str | None):
    return _impersonated_email_ctx.set(email)

def reset_context(token):
    _impersonated_email_ctx.reset(token)


# --- Tool Wrappers ---

@replace_tool("run_report")
async def run_report(
    property_id: int | str,
    date_ranges: List[Dict[str, str]],
    dimensions: List[str],
    metrics: List[str],
    dimension_filter: Dict[str, Any] = None,
    metric_filter: Dict[str, Any] = None,
    order_bys: List[Dict[str, Any]] = None,
    limit: int = None,
    offset: int = None,
    currency_code: str = None,
    return_property_quota: bool = False,
    impersonated_email: str | None = None,
) -> Dict[str, Any]:
    """Wraps core.run_report with impersonation support."""
    token = set_context(impersonated_email)
    try:
        return await core.run_report(
            property_id=property_id,
            date_ranges=date_ranges,
            dimensions=dimensions,
            metrics=metrics,
            dimension_filter=dimension_filter,
            metric_filter=metric_filter,
            order_bys=order_bys,
            limit=limit,
            offset=offset,
            currency_code=currency_code,
            return_property_quota=return_property_quota
        )
    finally:
        reset_context(token)

# Re-apply description because replacement loses it
mcp._tool_manager._tools["run_report"].description = core._run_report_description()


@replace_tool("run_realtime_report")
async def run_realtime_report(
    property_id: int | str,
    dimensions: List[str],
    metrics: List[str],
    dimension_filter: Dict[str, Any] = None,
    metric_filter: Dict[str, Any] = None,
    order_bys: List[Dict[str, Any]] = None,
    limit: int = None,
    offset: int = None,
    return_property_quota: bool = False,
    impersonated_email: str | None = None,
) -> Dict[str, Any]:
    """Wraps realtime.run_realtime_report with impersonation support."""
    token = set_context(impersonated_email)
    try:
        return await realtime.run_realtime_report(
            property_id=property_id,
            dimensions=dimensions,
            metrics=metrics,
            dimension_filter=dimension_filter,
            metric_filter=metric_filter,
            order_bys=order_bys,
            limit=limit,
            offset=offset,
            return_property_quota=return_property_quota
        )
    finally:
        reset_context(token)
mcp._tool_manager._tools["run_realtime_report"].description = realtime._run_realtime_report_description()


@replace_tool("get_account_summaries")
async def get_account_summaries(impersonated_email: str | None = None) -> List[Dict[str, Any]]:
    """Retrieves information about the user's Google Analytics accounts and properties."""
    token = set_context(impersonated_email)
    try:
        return await info.get_account_summaries()
    finally:
        reset_context(token)


@replace_tool("list_google_ads_links")
async def list_google_ads_links(
    property_id: int | str,
    impersonated_email: str | None = None
) -> List[Dict[str, Any]]:
    """Returns a list of links to Google Ads accounts for a property."""
    token = set_context(impersonated_email)
    try:
        return await info.list_google_ads_links(property_id=property_id)
    finally:
        reset_context(token)


@replace_tool("get_property_details")
async def get_property_details(
    property_id: int | str,
    impersonated_email: str | None = None
) -> Dict[str, Any]:
    """Returns details about a property."""
    token = set_context(impersonated_email)
    try:
        return await info.get_property_details(property_id=property_id)
    finally:
        reset_context(token)


@replace_tool("list_property_annotations")
async def list_property_annotations(
    property_id: int | str,
    impersonated_email: str | None = None
) -> List[Dict[str, Any]]:
    """Returns annotations for a property."""
    token = set_context(impersonated_email)
    try:
        return await info.list_property_annotations(property_id=property_id)
    finally:
        reset_context(token)

@replace_tool("get_custom_dimensions_and_metrics")
async def get_custom_dimensions_and_metrics(
    property_id: int | str,
    impersonated_email: str | None = None
) -> Dict[str, List[Dict[str, Any]]]:
    """Returns the property's custom dimensions and metrics."""
    token = set_context(impersonated_email)
    try:
        return await metadata.get_custom_dimensions_and_metrics(property_id=property_id)
    finally:
        reset_context(token)
