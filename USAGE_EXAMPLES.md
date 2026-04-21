# Drive MCP — Ejemplos de uso rápido

**SIN necesidad de modificar `.env` cada vez.**

Todos los tools de edición aceptan `document_id` como:
- **ID directo**: `1XyZ123abc...` (cualquier largo ≥25 caracteres)
- **Link completo**: `https://docs.google.com/document/d/1XyZ123abc/edit`

---

## 📋 Búsqueda (no modifican documento)

### Buscar archivos por nombre
```json
{
  "tool": "search_files",
  "params": {
    "name": "tesis"
  }
}
```

### Listar archivos en una subcarpeta
```json
{
  "tool": "list_files",
  "params": {
    "folder_id": "1XyZ_SUBCARPETA_ID",
    "max_results": 50
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

O con link:
```json
{
  "tool": "read_document",
  "params": {
    "document_id": "https://docs.google.com/document/d/1XyZ123abc/edit"
  }
}
```

---

## ✏️ Edición (SÍ modifican documento)

### 1️⃣ Reemplazar texto (búsqueda simple)
```json
{
  "tool": "edit_document_replace",
  "params": {
    "document_id": "1XyZ123abc",
    "find_text": "TODO",
    "replacement_text": "HECHO"
  }
}
```

**Parámetros opcionales:**
- `match_case`: `true` si debe respetar mayúsculas
- `all_occurrences`: `false` si solo quieres la primera instancia

**Con ambos opcionales:**
```json
{
  "tool": "edit_document_replace",
  "params": {
    "document_id": "1XyZ123abc",
    "find_text": "test",
    "replacement_text": "TEST",
    "match_case": true,
    "all_occurrences": false
  }
}
```

---

### 2️⃣ Agregar texto al final
```json
{
  "tool": "edit_document_append",
  "params": {
    "document_id": "1XyZ123abc",
    "text": "Nuevo párrafo\n\n"
  }
}
```

**Con formato:**
```json
{
  "tool": "edit_document_append",
  "params": {
    "document_id": "1XyZ123abc",
    "text": "Párrafo con formato\n\n",
    "bold": true,
    "italic": true,
    "font_size": 14
  }
}
```

**Parámetros de formato (todos opcionales):**
- `bold`: `true` o `false`
- `italic`: `true` o `false`
- `font_size`: tamaño en puntos (ej: 12, 14, 16)

---

### 3️⃣ Reemplazar + Aplicar formato
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

**Parámetros:**
- `document_id`: requerido (ID o link)
- `find_text`: requerido
- `replacement_text`: requerido
- `bold`: opcional
- `italic`: opcional
- `font_size`: opcional
- `match_case`: opcional (default: False)
- `all_occurrences`: opcional (default: True)

---

## 🎨 Estilos tipográficos (con perfiles)

### Aplicar perfil por defecto
```json
{
  "tool": "apply_document_styles",
  "params": {
    "document_id": "1XyZ123abc",
    "profile": "tesis_default"
  }
}
```

### Aplicar perfil con overrides
```json
{
  "tool": "apply_document_styles",
  "params": {
    "document_id": "1XyZ123abc",
    "profile": "tesis_default",
    "overrides": {
      "colors": {
        "h1": {"red": 0.0, "green": 0.0, "blue": 1.0},
        "h2": {"red": 0.0, "green": 0.0, "blue": 0.8},
        "h3": {"red": 0.0, "green": 0.2, "blue": 0.6}
      }
    }
  }
}
```

**Perfiles disponibles:**
- `tesis_default`: H1/H2 azul, H3 itálica
- `entrega_formal`: H1/H2 azul sin itálicas

---

## 🔗 Usando links (ahora más fácil)

**Antes:** Tenías que extraer manualmente el ID de `https://docs.google.com/document/d/ABC123XYZ/edit`

**Ahora:** Puedes pasar el link completo directamente

```json
{
  "tool": "edit_document_replace",
  "params": {
    "document_id": "https://docs.google.com/document/d/ABC123XYZ/edit",
    "find_text": "viejo",
    "replacement_text": "nuevo"
  }
}
```

El sistema extrae automáticamente `ABC123XYZ` y lo usa.

---

## ⚠️ Restricciones de seguridad

❌ **Estos comandos se BLOQUEARÁN automáticamente:**

```json
{
  "tool": "edit_document_replace",
  "params": {
    "document_id": "DOCUMENTO_FUERA_DE_CARPETA_RAIZ",
    "find_text": "...",
    "replacement_text": "..."
  }
}
```

✅ **Error esperado:** `PermissionError: Acceso denegado: El archivo NO está dentro de la carpeta raíz.`

✅ **Todos los documentos DEBEN estar dentro de:**
```
13cEoJyVieAmc_S6aBMOoEt9us9gJT877
```

---

## 📊 Respuestas exitosas (ejemplos)

### Replace - documento found
```json
{
  "success": true,
  "action": "replace_text",
  "find_text": "TODO",
  "replacement_text": "HECHO",
  "occurrences_changed": 3,
  "document_id": "1XyZ123abc"
}
```

### Append - éxito
```json
{
  "success": true,
  "action": "append_text",
  "text": "Nuevo párrafo",
  "bold": true,
  "italic": false,
  "font_size": 14,
  "document_id": "1XyZ123abc"
}
```

### Styles - aplicadas
```json
{
  "success": true,
  "result": {
    "document_id": "1XyZ123abc",
    "profile": "tesis_default",
    "requests_total": 181,
    "batches": 4
  }
}
```

---

## 🐛 Errores comunes & soluciones

| Error | Causa | Solución |
|---|---|---|
| `occurrences_changed: 0` | El texto buscado no existe | Verifica la ortografía exacta y mayúsculas. Usa `match_case: false` |
| `No se pudo extraer document_id` | Link o ID inválido | Usa un link de Google Docs válido o un ID de 25+ caracteres |
| `PermissionError: NO está dentro de la carpeta raíz` | Documento fuera del scope | Mueve el documento a la carpeta raíz o usa otro documento |
| `google.auth.exceptions.RefreshError` | Token expirado/revocado | Elimina `token_styles.json` y reautentica ejecutando `auth_first_time.py` |

---

## ✅ Verificación rápida

Ver que los 8 tools están disponibles:

```bash
source .venv/Scripts/activate
python -c "from drive_mcp.server import DriveMCPServer; \
  s = DriveMCPServer(); \
  req = {'jsonrpc':'2.0','id':1,'method':'tools/list'}; \
  tools = s.handle_list_tools(req)['result']['tools']; \
  [print(f'✓ {t[\"name\"]}') for t in tools]"
```

Esperado:
```
✓ list_files
✓ search_files
✓ get_file_metadata
✓ read_document
✓ apply_document_styles
✓ edit_document_replace
✓ edit_document_append
✓ edit_document_replace_and_format
✓ create_document
✓ create_folder
✓ copy_file
✓ rename_file
```

---

## 📁 Gestión de archivos/carpetas ✨ NUEVOS

### Crear nuevo Google Docs
```json
{
  "tool": "create_document",
  "params": {
    "name": "Informe Mensual - Abril",
    "folder_id": "19usCpkzcL0WizQSb1k12wIoEMPeEBMZX"
  }
}
```

### Crear nueva carpeta
```json
{
  "tool": "create_folder",
  "params": {
    "name": "Entregables - Abril",
    "folder_id": "19usCpkzcL0WizQSb1k12wIoEMPeEBMZX"
  }
}
```

### Copiar archivo
```json
{
  "tool": "copy_file",
  "params": {
    "file_id": "147eDbi4bVV1E1sSoyGnreMHtViS_JfMNKpaz8Is6VPg",
    "new_name": "Copia de Informe - Backup"
  }
}
```

O a una carpeta específica:
```json
{
  "tool": "copy_file",
  "params": {
    "file_id": "147eDbi4bVV1E1sSoyGnreMHtViS_JfMNKpaz8Is6VPg",
    "new_name": "Copia de Informe",
    "destination_folder_id": "19usCpkzcL0WizQSb1k12wIoEMPeEBMZX"
  }
}
```

### Renombrar archivo
```json
{
  "tool": "rename_file",
  "params": {
    "file_id": "147eDbi4bVV1E1sSoyGnreMHtViS_JfMNKpaz8Is6VPg",
    "new_name": "Informe Final - v2.0"
  }
}
```

---

## 📝 Notas finales

- **Sin .env:** Los tools aceptan `document_id` directamente sin tocar `.env`
- **Con link:** Puedes compartir el link completo del Google Doc
- **Seguridad:** La carpeta raíz se valida automáticamente en cada operación
- **Formato:** Font_size siempre en puntos (ej: 12, 14, 16)
- **Nuevos tools:** Ahora puedes crear documentos, carpetas, copiar y renombrar sin UI de Drive
