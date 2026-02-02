# 🔌 MCP Server como Proxy de Azure DevOps MCP

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastMCP](https://img.shields.io/badge/FastMCP-2.0+-purple.svg)](https://gofastmcp.com/)
[![Azure DevOps](https://img.shields.io/badge/Azure%20DevOps-MCP-0078D4.svg)](https://github.com/microsoft/azure-devops-mcp)

## 🤔 ¿Qué problema resuelve?

El [Azure DevOps MCP Server](https://github.com/microsoft/azure-devops-mcp) oficial de Microsoft funciona únicamente via **stdio** (entrada/salida estándar). Esto significa que:

- ❌ Solo puede ejecutarse **localmente** en tu máquina
- ❌ No puede exponerse como un **servicio remoto**
- ❌ No es accesible desde **otros dispositivos o servidores**
- ❌ Requiere tener **Node.js instalado** en cada máquina cliente

**Este proxy resuelve estos problemas** exponiendo el Azure DevOps MCP Server via **HTTP/SSE**, permitiendo:

- ✅ Ejecutar el servidor en una **máquina centralizada**
- ✅ Acceder desde **cualquier cliente MCP** via HTTP
- ✅ **Compartir** el acceso a Azure DevOps entre múltiples usuarios/agentes
- ✅ Desplegar en un **servidor o contenedor** para acceso remoto

## 🏗️ Arquitectura

```
┌─────────────┐     HTTP/SSE      ┌─────────────────┐     stdio      ┌──────────────────────┐
│  MCP Client │ ───────────────▶  │  FastMCP Proxy  │ ────────────▶  │  Azure DevOps MCP    │
│  (Copilot)  │                   │  (Este Server)  │                │  (@azure-devops/mcp) │
└─────────────┘                   └─────────────────┘                └──────────────────────┘
                                         │
                                         ▼
                                  🔐 PAT Authentication
                                  (ADO_MCP_AUTH_TOKEN)
```

## 📋 Requisitos

- **Python** 3.10 o superior
- **Node.js** 20 o superior (para `npx`)
- **Personal Access Token (PAT)** de Azure DevOps

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

Edita el archivo `.env` con tus credenciales:

```env
AZURE_DEVOPS_ORG=tu-organizacion
ADO_MCP_AUTH_TOKEN=tu-personal-access-token
```

### 4. Ejecutar el servidor

```bash
python proxy_server.py
```

El servidor estará disponible en `http://localhost:8080/sse`

## 🔑 Permisos del PAT

Dependiendo de los dominios que necesites usar, tu PAT debe tener estos permisos:

| Dominio | Permiso requerido |
|---------|-------------------|
| `core` | Project and Team: **Read** |
| `work` / `work-items` | Work Items: **Read & Write** |
| `repositories` | Code: **Read** (o Read & Write para PRs) |
| `pipelines` | Build: **Read**, Release: **Read** |
| `wiki` | Wiki: **Read & Write** |
| `test-plans` | Test Management: **Read & Write** |
| `search` | Code: **Read**, Work Items: **Read** |
| `advanced-security` | Advanced Security: **Read** |

📎 Crea tu PAT en: `https://dev.azure.com/{tu-org}/_usersSettings/tokens`

## 🔌 Configuración del Cliente MCP

### VS Code (mcp.json)

```json
{
    "servers": {
        "azure-devops-proxy": {
            "type": "sse",
            "url": "http://localhost:8080/sse"
        }
    }
}
```

### Claude Desktop

```json
{
    "mcpServers": {
        "azure-devops": {
            "url": "http://localhost:8080/sse",
            "transport": "sse"
        }
    }
}
```

## ⚠️ Seguridad

> **IMPORTANTE**: Este proxy actualmente no implementa autenticación propia. 
> Para uso en producción, considera añadir una capa de autenticación.

Opciones recomendadas:

- 🔐 **Microsoft Entra ID**: [OAuth Proxy](https://gofastmcp.com/servers/auth/oauth-proxy)
- 🔑 **API Key**: [Auth docs](https://gofastmcp.com/servers/auth)
- 🛡️ **Custom middleware**: [Custom Auth](https://gofastmcp.com/servers/auth/custom)

## 📚 Referencias

- [FastMCP - Proxy Servers](https://gofastmcp.com/v2/servers/proxy)
- [Azure DevOps MCP Server](https://github.com/microsoft/azure-devops-mcp)
- [MCP Protocol](https://modelcontextprotocol.io/)

## 📄 Licencia

MIT