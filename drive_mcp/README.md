# Drive MCP

Servidor MCP (Model Context Protocol) interno para interactuar con Google Drive y Google Docs.
Permite al agente de IA listar, buscar y leer archivos, y aplicar estilos al documento de tesis.

---

## Configuración

### Credenciales OAuth2 requeridas

El servidor usa el mismo token OAuth2 que `apply_styles.py`. Para generarlo por primera vez:

```bash
python drive_mcp/apply_styles.py
```

Se abrirá una ventana del navegador para autorizar el acceso. Luego se crea automáticamente
`token_styles.json` en la raíz del proyecto.

> ⚠️ `token_styles.json` y `gcp-oauth.keys.json` contienen datos sensibles.
> Nunca subirlos al repositorio (ya están en `.gitignore`).

### Variables de entorno

Todas opcionales: el servidor las detecta automáticamente si los archivos están en la raíz.

```bash
# Ruta al client secret descargado de Google Cloud Console.
# Default: gcp-oauth.keys.json en la raíz del proyecto.
GOOGLE_CLIENT_SECRET_PATH=./gcp-oauth.keys.json

# Ruta al token de sesión OAuth2.
# Default: token_styles.json en la raíz del proyecto.
GOOGLE_DRIVE_MCP_TOKEN_FILE=./token_styles.json
```

### Cómo arranca el servidor

El servidor es lanzado por VS Code a través de `.vscode/mcp.json`:

```json
"drive_mcp": {
  "type": "stdio",
  "command": "./.venv/Scripts/python.exe",
  "args": ["scripts/run_drive_mcp.py"]
}
```

Para probarlo manualmente:

```bash
python scripts/run_drive_mcp.py
```

---

## Herramientas disponibles

### `list_files`
Lista archivos en Google Drive. Opcionalmente filtra por carpeta.

| Parámetro | Tipo | Requerido | Descripción |
|---|---|---|---|
| `folder_id` | string | No | ID de la carpeta (se ve en la URL de Drive) |
| `max_results` | integer | No | Máximo de resultados (default: 20) |

---

### `search_files`
Busca archivos en Drive por nombre y/o query de Drive API.

| Parámetro | Tipo | Requerido | Descripción |
|---|---|---|---|
| `name` | string | No | Texto a buscar en el nombre del archivo |
| `query` | string | No | Query libre de Drive API (ej: `mimeType='application/vnd.google-apps.document'`) |
| `max_results` | integer | No | Máximo de resultados (default: 10) |

---

### `get_file_metadata`
Obtiene los metadatos completos de un archivo por su ID.

| Parámetro | Tipo | Requerido | Descripción |
|---|---|---|---|
| `file_id` | string | **Sí** | ID del archivo en Drive |

Devuelve: `id`, `name`, `mimeType`, `modifiedTime`, `size`, `parents`, `webViewLink`, `createdTime`.

---

### `read_document`
Lee el contenido de un Google Doc como texto plano.

| Parámetro | Tipo | Requerido | Descripción |
|---|---|---|---|
| `document_id` | string | **Sí** | ID del documento (se ve en la URL del Doc) |

---

## Script utilitario: `apply_styles.py`

Aplica estilos de fuente y color al documento de tesis en Google Docs.

**Estilos aplicados:**
- Fuente global: Montserrat
- H1 / H2 / TITLE: `#077BDE`, Bold 700
- H3: `#055A9E`, SemiBold 600, italic
- Líneas en mayúsculas detectadas como subtítulos: `#077BDE`, Bold 700

**Uso:**

```bash
python drive_mcp/apply_styles.py
```

> La primera ejecución abre el navegador para autorizar acceso OAuth2.
> Las siguientes usan el token guardado en `token_styles.json`.

---

## Archivos del módulo

```
drive_mcp/
├── __init__.py      # Marca el paquete Python
├── server.py        # Servidor MCP (JSON-RPC 2.0)
├── apply_styles.py  # Script para aplicar estilos al Doc de tesis
└── README.md        # Esta documentación
```
