---
name: thesis-doc
description: Gestiona autenticación, estilos y edición de documentos en Google Drive/Docs usando el MCP sin necesidad de modificar .env. Todos los tools aceptan document_id como ID directo o link de Google Docs.
---

# Thesis Doc — Skill dinámica para Drive/Docs

Este skill cubre autenticación, aplicación de estilos y edición de Google Docs dentro de la carpeta raíz compartida del equipo. **Sin necesidad de modificar `.env` cada vez.**

## Archivos relevantes

| Archivo | Propósito |
|---|---|
| `drive_mcp/auth.py` | Obtiene/refresca credenciales OAuth2 |
| `drive_mcp/auth_first_time.py` | Bootstrap de autenticación inicial |
| `drive_mcp/utils.py` | Extrae document_id de links (normalización) |
| `drive_mcp/edit.py` | Funciones para editar documentos (replace, append, etc.) |
| `drive_mcp/file_ops.py` | Operaciones de archivos (crear, copiar, renombrar) |
| `drive_mcp/styles.py` | Aplicación de estilos por perfil dinámico |
| `drive_mcp/style_profiles.py` | Perfiles base (tesis_default, entrega_formal) |
| `drive_mcp/server.py` | MCP tools (12 herramientas: list, search, read, edit, create, copy, rename, style, etc.) |
| `drive_mcp/config.py` | Carpeta raíz compartida del proyecto |

## MCP Tools disponibles (sin necesidad de .env)

### Lectura & búsqueda (no modifican documento)

| Tool | Descripción | Parámetro clave |
|---|---|---|
| `list_files` | Listar archivos en Drive | `folder_id` (opcional, default: raíz) |
| `search_files` | Buscar por nombre o query Drive API | `name` o `query` |
| `get_file_metadata` | Obtener metadatos (tamaño, owner, etc.) | `file_id` |
| `read_document` | Leer contenido como texto plano | `document_id` (ID o link) |

### Edición & estilos (modifican documento)

| Tool | Descripción | Parámetro clave |
|---|---|---|
| `edit_document_replace` | Buscar y reemplazar texto | `document_id` (ID o link), `find_text`, `replacement_text` |
| `edit_document_append` | Agregar texto al final | `document_id` (ID o link), `text`, opcional: `bold`, `italic`, `font_size` |
| `edit_document_replace_and_format` | Reemplazar + aplicar formato | `document_id` (ID o link), `find_text`, `replacement_text`, opcional: `bold`, `italic`, `font_size` |
| `apply_document_styles` | Aplicar estilos tipográficos con perfil | `document_id` (ID o link, optional: usa GOOGLE_DOCS_ID), `profile`, `overrides` |

### Gestión de archivos/carpetas (modifican Drive) ✨ NUEVOS

| Tool | Descripción | Parámetro clave |
|---|---|---|
| `create_document` | Crear Google Docs en carpeta específica | `name`, `folder_id` (opcional) |
| `create_folder` | Crear carpeta en Drive | `name`, `folder_id` (opcional) |
| `copy_file` | Copiar archivo o carpeta | `file_id`, `new_name`, `destination_folder_id` (opcional) |
| `rename_file` | Renombrar archivo o carpeta | `file_id`, `new_name` |

---

## Cómo usar: SIN MODIFICAR .env

### ✅ Opción 1: Pasar document_id directamente

El equipo puede pedirte editar un documento simplemente pasando el ID:

```
Usuario: "Edita el documento ABC123XYZ y reemplaza 'viejo' por 'nuevo'"
```

Tu MCP call:
```json
{
  "tool": "edit_document_replace",
  "params": {
    "document_id": "ABC123XYZ",
    "find_text": "viejo",
    "replacement_text": "nuevo"
  }
}
```

### ✅ Opción 2: Pasar link completo de Google Docs

El usuario puede compartir el link directamente:

```
Usuario: "Agrega este párrafo al final: https://docs.google.com/document/d/1XyZ123abc/edit"
```

Tu MCP call (el helper extrae automáticamente el ID):
```json
{
  "tool": "edit_document_append",
  "params": {
    "document_id": "https://docs.google.com/document/d/1XyZ123abc/edit",
    "text": "Este es un nuevo párrafo.\n\nCon múltiples líneas."
  }
}
```

### ✅ Opción 3: Con formato

Reemplazar texto Y aplicar formato en un solo call:

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

---

## Perfiles de estilos

Base profiles (definidos en `style_profiles.py`):
- **`tesis_default`**: H1/H2 azul, H3 itálica, fuente Montserrat
- **`entrega_formal`**: H1/H2 azul sin itálicas, H3 normal, fuente Montserrat

Usando perfiles:

```json
{
  "tool": "apply_document_styles",
  "params": {
    "document_id": "1XyZ123abc",
    "profile": "entrega_formal",
    "overrides": {
      "colors": {
        "h1": {"red": 0.0, "green": 0.0, "blue": 1.0},
        "h2": {"red": 0.0, "green": 0.0, "blue": 0.8}
      }
    }
  }
}
```

---

## Flujo recomendado para el equipo

### Primera vez (autenticación)

```bash
source .venv/Scripts/activate && python drive_mcp/auth_first_time.py
# Se abre el browser para que autorices, genera token_styles.json
```

### Luego: Usar MCP tools sin tocar .env

Todos los tools MCP aceptan `document_id` directamente:

```bash
# El equipo dice: "Edita el doc XYZ"
# Tú haces: MCP call con edit_document_* sin tocar .env
```

---

## Seguridad (OBLIGATORIO)

- Carpeta raíz de Drive: **`13cEoJyVieAmc_S6aBMOoEt9us9gJT877`**
- **TODOS** los documentos editados DEBEN estar dentro de esa carpeta
- Si alguien intenta editar un doc fuera: `PermissionError` (bloqueado automáticamente)

---

## Validar que todo funciona

```bash
# 1. Activar venv
source .venv/Scripts/activate

# 2. Validar sintaxis
python -m py_compile drive_mcp/utils.py drive_mcp/edit.py drive_mcp/server.py

# 3. Confirmar que los 8 tools están registrados
python -c "from drive_mcp.server import DriveMCPServer; \
  s = DriveMCPServer(); \
  req = {'jsonrpc':'2.0','id':1,'method':'tools/list'}; \
  tools = s.handle_list_tools(req)['result']['tools']; \
  print([t['name'] for t in tools])"

# Resultado esperado:
# ['list_files', 'search_files', 'get_file_metadata', 'read_document', 
#  'apply_document_styles', 'edit_document_replace', 'edit_document_append', 
#  'edit_document_replace_and_format']
```

---

## Ejemplos de uso (copy-paste ready)

### Buscar un documento por nombre
```json
{
  "tool": "search_files",
  "params": {
    "name": "tesis"
  }
}
```

### Leer contenido de un documento
```json
{
  "tool": "read_document",
  "params": {
    "document_id": "1XyZ123abc"
  }
}
```

### Reemplazar "TODO" por "HECHO" (todas las instancias)
```json
{
  "tool": "edit_document_replace",
  "params": {
    "document_id": "1XyZ123abc",
    "find_text": "TODO",
    "replacement_text": "HECHO",
    "all_occurrences": true
  }
}
```

### Agregar cabecera al documento
```json
{
  "tool": "edit_document_append",
  "params": {
    "document_id": "1XyZ123abc",
    "text": "Actualizado: Abril 2026\n\n",
    "bold": true,
    "font_size": 12
  }
}
```

### Aplicar estilos con perfil tesis_default
```json
{
  "tool": "apply_document_styles",
  "params": {
    "document_id": "1XyZ123abc",
    "profile": "tesis_default"
  }
}
```

---

## Errores comunes

| Error | Solución |
|---|---|
| `No se pudo extraer document_id de: ...` | El link/ID es inválido. Usa: `https://docs.google.com/document/d/IDAQUÍ/edit` o solo el ID |
| `Acceso denegado: El archivo NO está dentro de la carpeta raíz` | El documento está fuera de `13cEoJyVieAmc_S6aBMOoEt9us9gJT877`. Mueve el documento o pide otro |
| `google.auth.exceptions.RefreshError` | Token expirado. Elimina `token_styles.json` y vuelve a autenticar |
| `occurrences_changed: 0` en replace | El texto buscado no existe en el documento. Verifica mayúsculas/espacios |

---

## Workflow de desarrollo

Si necesitas agregar más tools de edición:

1. Agrega la función en `drive_mcp/edit.py`
2. Agrega el método en `DriveMCPServer` (server.py)
3. Registra el tool en `handle_list_tools` (schema de parámetros)
4. Agrega el routing en `handle_call_tool`
5. Valida: `python -m py_compile drive_mcp/*.py`
6. Verifica que aparezca en tools/list
