# 🔌 MCP Server Proxy con FastMCP

<div align="center">

[![YouTube Channel Subscribers](https://img.shields.io/youtube/channel/subscribers/UC140iBrEZbOtvxWsJ-Tb0lQ?style=for-the-badge&logo=youtube&logoColor=white&color=red)](https://www.youtube.com/c/GiselaTorres?sub_confirmation=1)
[![GitHub followers](https://img.shields.io/github/followers/0GiS0?style=for-the-badge&logo=github&logoColor=white)](https://github.com/0GiS0)
[![LinkedIn Follow](https://img.shields.io/badge/LinkedIn-Sígueme-blue?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/giselatorresbuitrago/)
[![X Follow](https://img.shields.io/badge/X-Sígueme-black?style=for-the-badge&logo=x&logoColor=white)](https://twitter.com/0GiS0)

</div>

---

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastMCP](https://img.shields.io/badge/FastMCP-2.0+-purple.svg)](https://gofastmcp.com/)


## 🤔 ¿Qué problema resuelve?

Muchos MCP Servers tienen limitaciones que dificultan su uso en entornos compartidos o remotos:

- ❌ Funcionan via **stdio** → Solo pueden ejecutarse localmente
- ❌ Requieren **credenciales** (PAT, API Keys, tokens) → Cada cliente debe configurarlas
- ❌ Necesitan **dependencias** específicas → Hay que instalarlas en cada máquina
- ❌ No pueden exponerse como **servicio remoto**

**Este proyecto demuestra cómo crear un proxy** con [FastMCP](https://gofastmcp.com/) que resuelve estos problemas:

- ✅ Ejecutar el servidor en una **máquina centralizada**
- ✅ Acceder desde **cualquier cliente MCP** via HTTP
- ✅ **Compartir** el acceso entre múltiples usuarios/agentes
- ✅ **Centralizar la autenticación** (tokens, PATs, API keys)
- ✅ Desplegar en un **servidor o contenedor** para acceso remoto


<img width="50%" height="50%" alt="MCP Server como proxy" src="https://github.com/user-attachments/assets/f6781c71-c801-4db2-b37d-554cb51942d6" />


## 🎯 Caso de ejemplo: Azure DevOps MCP

Este repositorio usa el [Azure DevOps MCP Server](https://github.com/microsoft/azure-devops-mcp) como ejemplo porque:

1. **Usa stdio** → No puede exponerse directamente como servicio
2. **Requiere PAT** → Necesita un Personal Access Token para autenticarse
3. **Es muy útil** → Permite interactuar con Azure DevOps desde agentes IA

Pero el mismo patrón aplica a **cualquier MCP Server** que use stdio y/o requiera credenciales.

## 🏗️ Arquitectura

```
┌─────────────┐     HTTP/SSE      ┌─────────────────┐     stdio      ┌──────────────────────┐
│  MCP Client │ ───────────────▶  │  FastMCP Proxy  │ ────────────▶  │  MCP Server (stdio)  │
│  (Copilot)  │                   │  (Este Server)  │                │  (ej: Azure DevOps)  │
└─────────────┘                   └─────────────────┘                └──────────────────────┘
                                         │
                                         ▼
                                  🔐 Credenciales centralizadas
                                  (PAT, API Keys, Tokens...)
```

## 📋 Requisitos

- **Python** 3.10 o superior
- **Node.js** 20 o superior (para el ejemplo con Azure DevOps)
- Las **credenciales** que requiera el MCP Server que quieras proxear

## 🚀 Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/0GiS0/mcp-server-as-a-proxy.git
cd mcp-server-as-a-proxy
```

### 2. Instalar dependencias

```bash
pip install -e .
```

### 3. Configurar variables de entorno

```bash
cp .env.example .env
```

Edita el archivo `.env` con tus credenciales (ejemplo para Azure DevOps):

```env
AZURE_DEVOPS_ORG=tu-organizacion
ADO_MCP_AUTH_TOKEN=tu-personal-access-token
```

### 4. Ejecutar el servidor

```bash
python proxy_server.py
```

El servidor estará disponible en `http://localhost:8080/mcp`

## 🔧 Cómo adaptar a otro MCP Server

El código en `proxy_server.py` se puede adaptar fácilmente para cualquier MCP Server stdio:

```python
from fastmcp import FastMCP
from fastmcp.server.proxy import ProxyClient
from fastmcp.client.transports import StdioTransport

# 1️⃣ Configura el transport para TU MCP Server
transport = StdioTransport(
    command="npx",                    # O python, node, etc.
    args=["-y", "@tu-mcp/server"],    # Argumentos del servidor
    env={
        "API_KEY": "tu-api-key",      # Variables de entorno necesarias
        "OTHER_SECRET": "..."
    }
)

# 2️⃣ Crea el proxy
proxy = FastMCP.as_proxy(
    ProxyClient(transport),
    name="MiMCPProxy"
)

# 3️⃣ Expón via HTTP (Streamable)
if __name__ == "__main__":
    proxy.run(transport="http", host="0.0.0.0", port=8080)
```

## 🔌 Configuración del Cliente MCP

### VS Code (mcp.json)

```json
{
  "servers": {
    "mi-proxy": {
      "type": "http",
      "url": "http://localhost:8080/mcp"
    }
  }
}
```

### Claude Desktop

```json
{
  "mcpServers": {
    "mi-proxy": {
      "url": "http://localhost:8080/mcp",
      "transport": "http"
    }
  }
}
```

## ⚠️ Seguridad

> **IMPORTANTE**: Este proxy actualmente no implementa autenticación propia.
> Para uso en producción, añade una capa de autenticación.

### 🔐 Autenticación con Microsoft Entra ID

FastMCP incluye un provider nativo para Azure. Documentación completa: [FastMCP Azure Integration](https://gofastmcp.com/integrations/azure)

```python
from fastmcp.server.auth.providers.azure import AzureProvider

auth_provider = AzureProvider(
    client_id="tu-app-client-id",
    client_secret="tu-client-secret",
    tenant_id="tu-tenant-id",
    base_url="http://localhost:8080",
    required_scopes=["mcp-access"],
)

proxy = FastMCP.as_proxy(
    ProxyClient(transport),
    name="MiProxy",
    auth=auth_provider  # 👈 Añadir autenticación
)
```

## 📚 Referencias

- [FastMCP - Proxy Servers](https://gofastmcp.com/v2/servers/proxy)
- [FastMCP - Azure Auth](https://gofastmcp.com/integrations/azure)
- [Azure DevOps MCP Server](https://github.com/microsoft/azure-devops-mcp) (ejemplo usado)
- [MCP Protocol](https://modelcontextprotocol.io/)

## 🌐 Sígueme en Mis Redes Sociales

Si te ha gustado este proyecto y quieres ver más contenido como este, no olvides suscribirte a mi canal de YouTube y seguirme en mis redes sociales:

<div align="center">

[![YouTube Channel Subscribers](https://img.shields.io/youtube/channel/subscribers/UC140iBrEZbOtvxWsJ-Tb0lQ?style=for-the-badge&logo=youtube&logoColor=white&color=red)](https://www.youtube.com/c/GiselaTorres?sub_confirmation=1)
[![GitHub followers](https://img.shields.io/github/followers/0GiS0?style=for-the-badge&logo=github&logoColor=white)](https://github.com/0GiS0)
[![LinkedIn Follow](https://img.shields.io/badge/LinkedIn-Sígueme-blue?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/giselatorresbuitrago/)
[![X Follow](https://img.shields.io/badge/X-Sígueme-black?style=for-the-badge&logo=x&logoColor=white)](https://twitter.com/0GiS0)

</div>

## 📄 Licencia

MIT
