"""
🔌 FastMCP Proxy Server for Azure DevOps MCP
=============================================

This proxy server bridges the Azure DevOps MCP Server (@azure-devops/mcp) 
to HTTP (Streamable), enabling remote access to Azure DevOps tools via MCP protocol.

⚠️ TODO: IMPORTANT - Add authentication to this proxy server!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Currently this proxy exposes the Azure DevOps MCP Server without authentication.
For production use, implement Microsoft Entra ID authentication using FastMCP's
built-in AzureProvider:

    🔐 Microsoft Entra ID (recommended for Azure DevOps):
       https://gofastmcp.com/integrations/azure
       
       Example with AzureProvider:
       ```python
       from fastmcp import FastMCP
       from fastmcp.server.auth.providers.azure import AzureProvider
       
       auth_provider = AzureProvider(
           client_id="your-app-client-id",        # From Azure App Registration
           client_secret="your-client-secret",    # From Certificates & secrets
           tenant_id="your-tenant-id",            # Your Azure AD tenant
           base_url="http://localhost:8080",      # Must match App registration
           required_scopes=["mcp-access"],        # Scopes from "Expose an API"
       )
       
       # Create proxy with authentication
       proxy = FastMCP.as_proxy(
           ProxyClient(transport),
           name="AzureDevOpsProxy",
           auth=auth_provider  # 👈 Add this!
       )
       ```
    
    📋 Azure App Registration steps:
       1. Create App in Azure Portal → Microsoft Entra ID → App registrations
       2. Set Redirect URI: http://localhost:8080/auth/callback
       3. Create Client Secret in Certificates & secrets
       4. Expose an API → Add scope (e.g., "mcp-access")
       5. Set requestedAccessTokenVersion to 2 in Manifest
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
    3. Connect via HTTP at http://localhost:8080/mcp
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
    print(f"🌐 Listening on: http://0.0.0.0:8080/mcp")
    print("─" * 50)
    
    # Run as HTTP server on port 8080 (Streamable HTTP transport)
    # This exposes the stdio-based Azure DevOps MCP Server via HTTP
    # Clients connect to http://localhost:8080/mcp
    proxy.run(transport="http", host="0.0.0.0", port=8080)
