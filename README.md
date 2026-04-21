# PPS — Proyecto de Práctica Profesional Supervisada

Repositorio con servidores MCP (Model Context Protocol) para Jira y Google Drive,
más scripts de automatización sobre Google Docs.

Para la configuración y herramientas de cada MCP ver sus READMEs:
- [jira_mcp/README.md](jira_mcp/README.md)
- [drive_mcp/README.md](drive_mcp/README.md)

---

## Requisitos

| Requisito | Versión mínima |
|---|---|
| Python | 3.10 |
| pip | 22+ |
| Git | cualquier versión reciente |
| Cuenta Google | con acceso al documento de tesis |
| Cuenta Atlassian | con API Token generado |

---

## Instalación

### 1. Clonar el repositorio

```bash
git clone <URL_DEL_REPO>
cd PPS
```

### 2. Crear y activar el entorno virtual

```bash
# Crear
python -m venv .venv

# Activar en Windows
.venv\Scripts\activate

# Activar en Linux/macOS
source .venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install jira google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

---

## Configuración de credenciales

### Google (Drive MCP)

1. Abrí [https://console.cloud.google.com/apis/credentials](https://console.cloud.google.com/apis/credentials)
2. Crear credenciales → **ID de cliente OAuth 2.0** → tipo **Aplicación de escritorio**
3. Descargar el JSON generado y renombrarlo a `gcp-oauth.keys.json` en la raíz del proyecto
4. En **APIs y servicios → Pantalla de consentimiento**, agregar los alcances:
   - `https://www.googleapis.com/auth/documents`
   - `https://www.googleapis.com/auth/drive`
5. Generar el token de sesión ejecutando:
   ```bash
   python drive_mcp/apply_styles.py
   ```
   Se abrirá el navegador para autorizar. Luego se crea `token_styles.json` automáticamente.

### Jira (Jira MCP)

1. Obtener el API Token en [https://id.atlassian.com/manage-profile/security/api-tokens](https://id.atlassian.com/manage-profile/security/api-tokens)
2. Copiar `.env.example` a `.env` y completar:
   ```bash
   cp .env.example .env
   ```
   ```bash
   JIRA_HOST=https://TU_DOMINIO.atlassian.net
   JIRA_EMAIL=tu_email@example.com
   JIRA_API_TOKEN=tu_api_token
   ```

---

## Configuración de VS Code MCP

```bash
cp .vscode/mcp.example.json .vscode/mcp.json
```

> ⚠️ Nunca subas `.vscode/mcp.json` al repositorio. Si lo hiciste accidentalmente,
> revocá las credenciales de inmediato en la consola de GCP y en Atlassian.

---

## Estructura del proyecto

```
PPS/
├── jira_mcp/                  # MCP para Jira Cloud
│   ├── __init__.py
│   ├── server.py
│   └── README.md              # Configuración y herramientas
├── drive_mcp/                 # MCP para Google Drive / Docs
│   ├── __init__.py
│   ├── server.py
│   ├── apply_styles.py
│   └── README.md              # Configuración y herramientas
├── scripts/
│   ├── run_jira_mcp.py        # Launcher Jira MCP
│   ├── run_drive_mcp.py       # Launcher Drive MCP
│   └── test_jira_mcp.py       # Prueba de integración Jira MCP
├── .vscode/
│   └── mcp.example.json       # Plantilla de configuración MCP
├── .env.example               # Plantilla de variables de entorno
├── gcp-oauth.keys.json        # ⚠️ Credenciales OAuth — NO subir al repo
├── token_styles.json          # ⚠️ Token de sesión — NO subir al repo
└── README.md
```

---

## Archivos sensibles

Todos excluidos del repositorio por `.gitignore`:

| Archivo | Contenido |
|---|---|
| `gcp-oauth.keys.json` | `client_id` y `client_secret` de GCP |
| `token_*.json` | Access token y refresh token de Google |
| `.env` / `.env.local` | API Token de Jira y otras variables privadas |
| `.vscode/mcp.json` | Configuración local de servidores MCP |
