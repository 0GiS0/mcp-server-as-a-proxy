"""
FastMCP Proxy Server for Azure DevOps MCP

This server acts as a proxy for the Azure DevOps MCP Server (@azure-devops/mcp),
exposing it via HTTP/SSE instead of stdio. Authentication is done via PAT
using the ADO_MCP_AUTH_TOKEN environment variable.
"""

import os
from dotenv import load_dotenv
from fastmcp import FastMCP
from fastmcp.server.proxy import ProxyClient
from fastmcp.client.transports import StdioTransport

# Load environment variables from .env file
load_dotenv()

# Get configuration from environment
AZURE_DEVOPS_ORG = os.environ.get("AZURE_DEVOPS_ORG")
ADO_MCP_AUTH_TOKEN = os.environ.get("ADO_MCP_AUTH_TOKEN")

if not AZURE_DEVOPS_ORG:
    raise ValueError("AZURE_DEVOPS_ORG environment variable is required")

if not ADO_MCP_AUTH_TOKEN:
    raise ValueError("ADO_MCP_AUTH_TOKEN environment variable is required")

# Create transport for the Azure DevOps MCP Server (stdio-based)
transport = StdioTransport(
    command="npx",
    args=[
        "-y",
        "@azure-devops/mcp",
        AZURE_DEVOPS_ORG,
        "--authentication",
        "envvar"
    ],
    env={
        "ADO_MCP_AUTH_TOKEN": ADO_MCP_AUTH_TOKEN
    }
)

# Create the proxy server using FastMCP.as_proxy()
proxy = FastMCP.as_proxy(
    ProxyClient(transport),
    name="AzureDevOpsProxy"
)

if __name__ == "__main__":
    # Run as HTTP/SSE server on port 8080
    proxy.run(transport="sse", host="0.0.0.0", port=8080)
