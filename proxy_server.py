"""
🔌 FastMCP Proxy Server for Azure DevOps MCP
=============================================

This proxy server bridges the Azure DevOps MCP Server (@azure-devops/mcp) 
to HTTP/SSE, enabling remote access to Azure DevOps tools via MCP protocol.

⚠️ TODO: IMPORTANT - Add authentication to this proxy server!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Currently this proxy exposes the Azure DevOps MCP Server without authentication.
For production use, implement one of these authentication methods:

    🔐 Microsoft Entra ID (recommended for Azure DevOps):
       https://gofastmcp.com/servers/auth/oauth-proxy
       
       Example with Entra ID:
       ```python
       from fastmcp.server.auth import OAuthProxy
       
       oauth_proxy = OAuthProxy(
           proxy,
           provider="azure",
           client_id="your-client-id",
           client_secret="your-client-secret",
           tenant_id="your-tenant-id"
       )
       ```
    
    🔑 API Key authentication:
       https://gofastmcp.com/servers/auth
       
    🛡️ Custom middleware:
       https://gofastmcp.com/servers/auth/custom
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🏗️ Architecture:
                                                
    ┌─────────────┐     HTTP/SSE      ┌─────────────────┐     stdio      ┌──────────────────────┐
    │  MCP Client │ ───────────────▶  │  FastMCP Proxy  │ ────────────▶  │  Azure DevOps MCP    │
    │  (Copilot)  │                   │  (This Server)  │                │  (@azure-devops/mcp) │
    └─────────────┘                   └─────────────────┘                └──────────────────────┘
                                             │
                                             ▼
                                      🔐 PAT Authentication
                                      (ADO_MCP_AUTH_TOKEN)

🔑 Authentication:
    Uses Personal Access Token (PAT) via environment variable ADO_MCP_AUTH_TOKEN
    The PAT is passed to the Azure DevOps MCP Server using --authentication envvar

📋 Requirements:
    - Python 3.10+
    - Node.js 20+ (for npx)
    - Azure DevOps PAT with appropriate scopes

🚀 Usage:
    1. Copy .env.example to .env and configure your credentials
    2. Run: python proxy_server.py
    3. Connect via SSE at http://localhost:8080/sse
"""

import os
from dotenv import load_dotenv
from fastmcp import FastMCP
from fastmcp.server.proxy import ProxyClient
from fastmcp.client.transports import StdioTransport

# 📂 Load environment variables from .env file
load_dotenv()

# ⚙️ Get configuration from environment
AZURE_DEVOPS_ORG = os.environ.get("AZURE_DEVOPS_ORG")
ADO_MCP_AUTH_TOKEN = os.environ.get("ADO_MCP_AUTH_TOKEN")

# ✅ Validate required environment variables
if not AZURE_DEVOPS_ORG:
    raise ValueError("❌ AZURE_DEVOPS_ORG environment variable is required")

if not ADO_MCP_AUTH_TOKEN:
    raise ValueError("❌ ADO_MCP_AUTH_TOKEN environment variable is required")

# 🚇 Create stdio transport for the Azure DevOps MCP Server
# This transport launches the official Microsoft Azure DevOps MCP Server
# using npx and configures it to use PAT authentication via environment variable
transport = StdioTransport(
    command="npx",
    args=[
        "-y",                      # Auto-confirm npx install
        "@azure-devops/mcp",       # Official Azure DevOps MCP package
        AZURE_DEVOPS_ORG,          # Your Azure DevOps organization name
        "--authentication",        # Authentication method flag
        "envvar"                   # Use environment variable for PAT
    ],
    env={
        # 🔐 Pass the PAT to the Azure DevOps MCP Server
        "ADO_MCP_AUTH_TOKEN": ADO_MCP_AUTH_TOKEN
    }
)

# 🔌 Create the proxy server using FastMCP
# ProxyClient wraps the stdio transport and handles MCP protocol forwarding
# FastMCP.as_proxy() creates a server that forwards all requests to the backend
proxy = FastMCP.as_proxy(
    ProxyClient(transport),
    name="AzureDevOpsProxy"
)

# 🚀 Main entry point
if __name__ == "__main__":
    print("🔌 Starting Azure DevOps MCP Proxy Server...")
    print(f"📡 Organization: {AZURE_DEVOPS_ORG}")
    print(f"🌐 Listening on: http://0.0.0.0:8080/sse")
    print("─" * 50)
    
    # Run as HTTP/SSE server on port 8080
    # This exposes the stdio-based Azure DevOps MCP Server via HTTP/SSE
    proxy.run(transport="sse", host="0.0.0.0", port=8080)
