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

---

## Herramientas MCP para Drive/Docs (SIN modificar .env)

### ✨ Novedad: Document_id flexible

Todos los MCP tools de Drive aceptan `document_id` como:
- **ID directo**: `1XyZ123abc...` (28+ caracteres)
- **Link de Google Docs**: `https://docs.google.com/document/d/1XyZ123abc/edit`

El sistema extrae automáticamente el ID del link. **No hay necesidad de modificar `.env` cada vez.**

### 12 Herramientas disponibles ✨ 4 NUEVOS

#### 📂 Lectura & búsqueda (no modifican)

| Tool | Uso |
|---|---|
| `list_files` | Listar archivos en Drive (con filter por carpeta opcional) |
| `search_files` | Buscar archivos por nombre o query Drive API |
| `get_file_metadata` | Obtener metadatos (tamaño, propietario, fecha modificación) |
| `read_document` | Leer contenido de un Google Doc como texto plano |

#### ✏️ Edición & estilos (sí modifican)

| Tool | Uso |
|---|---|
| `edit_document_replace` | Buscar y reemplazar texto (con opción `all_occurrences`) |
| `edit_document_append` | Agregar texto al final del documento (con formato opcional) |
| `edit_document_replace_and_format` | Reemplazar texto + aplicar formato (bold, italic, tamaño) |
| `apply_document_styles` | Aplicar estilos tipográficos con perfil (`tesis_default`, `entrega_formal`, etc.) |

#### 📁 Gestión de archivos/carpetas (sí modifican) ✨ NUEVOS

| Tool | Uso |
|---|---|
| `create_document` | Crear nuevo Google Docs en carpeta específica |
| `create_folder` | Crear nueva carpeta en Drive |
| `copy_file` | Copiar archivo o carpeta (incluye toda la estructura) |
| `rename_file` | Renombrar archivo o carpeta (sin moverlo) |

### Ejemplos de uso

#### Ejemplo 1: El equipo te dice "Edita documento ABC123"

```json
{
  "tool": "edit_document_replace",
  "params": {
    "document_id": "ABC123...",
    "find_text": "viejo",
    "replacement_text": "nuevo",
    "all_occurrences": true
  }
}
```

#### Ejemplo 2: Comparten un link de Google Docs

```json
{
  "tool": "edit_document_append",
  "params": {
    "document_id": "https://docs.google.com/document/d/1XyZ123abc/edit",
    "text": "Párrafo nuevo",
    "bold": true
  }
}
```

#### Ejemplo 3: Editar y aplicar estilos en un call

```json
{
  "tool": "edit_document_replace_and_format",
  "params": {
    "document_id": "1XyZ123abc",
    "find_text": "IMPORTANTE",
    "replacement_text": "IMPORTANTE",
    "bold": true,
    "italic": true,
    "font_size": 14
  }
}
```

#### Ejemplo 4: Aplicar perfil de estilos

```json
{
  "tool": "apply_document_styles",
  "params": {
    "document_id": "1XyZ123abc",
    "profile": "tesis_default",
    "overrides": {
      "colors": {
        "h1": {"red": 0.0, "green": 0.0, "blue": 1.0}
      }
    }
  }
}
```

---

## Seguridad garantizada

✅ **Carpeta raíz bloqueada**: `13cEoJyVieAmc_S6aBMOoEt9us9gJT877`
- Todo documento **DEBE** estar dentro de esta carpeta
- Intentos de editar fuera = `PermissionError` automático
- El equipo no puede acceder documentos externos accidentalmente

---

## Para agregar más herramientas MCP

Ver [drive_mcp/README.md](drive_mcp/README.md) y [.agents/skills/thesis-doc/SKILL.md](.agents/skills/thesis-doc/SKILL.md)
