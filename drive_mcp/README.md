# Drive MCP

Servidor MCP (Model Context Protocol) interno para interactuar con Google Drive y Google Docs.
Permite al agente de IA listar, buscar y leer archivos, y aplicar estilos al documento de tesis.

**Arquitectura con carpeta raíz COMPARTIDA** — Todos los miembros del equipo trabajan dentro de la misma carpeta oficial del proyecto.

---

## Configuración paso a paso

### Paso 1 — Crear un proyecto en Google Cloud Console

1. Ir a [https://console.cloud.google.com/](https://console.cloud.google.com/)
2. En el selector de proyectos (arriba a la izquierda), hacer clic en **Nuevo proyecto**
3. Darle un nombre (ej: `PPS-MCP`) y hacer clic en **Crear**
4. Asegurarse de que el proyecto nuevo quede seleccionado en el selector

---

### Paso 2 — Habilitar las APIs requeridas

Dentro del proyecto recién creado:

1. Ir al menú lateral → **APIs y servicios → Biblioteca**
2. Buscar **Google Drive API** → hacer clic en el resultado → **Habilitar**
3. Volver a la Biblioteca, buscar **Google Docs API** → **Habilitar**

---

### Paso 3 — Configurar la pantalla de consentimiento OAuth

1. Ir a **APIs y servicios → Pantalla de consentimiento de OAuth**
2. Tipo de usuario: seleccionar **Externo** → **Crear**
3. Completar los campos obligatorios:
   - **Nombre de la aplicación**: cualquier nombre (ej: `PPS Drive MCP`)
   - **Correo electrónico de asistencia**: tu email
   - **Correo de contacto del desarrollador** (al final del formulario): tu email
4. Hacer clic en **Guardar y continuar**
5. En la sección **Permisos (Scopes)**:
   - Hacer clic en **Agregar o quitar permisos**
   - Buscar y seleccionar:
     - `https://www.googleapis.com/auth/drive`
     - `https://www.googleapis.com/auth/documents`
   - Hacer clic en **Actualizar** → **Guardar y continuar**
6. En la sección **Usuarios de prueba**:
   - Hacer clic en **Agregar usuarios**
   - Ingresar el email de la cuenta de Google con la que vas a autorizar el acceso
   - Hacer clic en **Agregar** → **Guardar y continuar**
7. Revisar el resumen y hacer clic en **Volver al panel**

> ⚠️ Mientras la app esté en modo **Testing**, solo los emails agregados como usuarios de prueba
> pueden autorizar el acceso. Si necesitás agregar más personas, repetir el paso 6.

---

### Paso 4 — Crear las credenciales OAuth 2.0

1. Ir a **APIs y servicios → Credenciales**
2. Hacer clic en **Crear credenciales → ID de cliente de OAuth 2.0**
3. Tipo de aplicación: seleccionar **Aplicación de escritorio**
4. Nombre: cualquiera (ej: `PPS Desktop Client`)
5. Hacer clic en **Crear**
6. En el cuadro que aparece, hacer clic en **Descargar JSON**
7. Renombrar el archivo descargado a `gcp-oauth.keys.json`
8. Copiarlo a la **raíz del proyecto** (`PPS/gcp-oauth.keys.json`)

> El archivo contiene el `client_id` y el `client_secret`. Nunca subirlo al repositorio
> (ya está en `.gitignore`).

---

### Paso 5 — Copiar archivo de configuración

Copiar el archivo `.env.example` a `.env` en la raíz del proyecto:

```bash
cp .env.example .env
```

**NO necesitas modificar nada relacionado con la carpeta raíz.** El valor está hardcodeado en `config.py` y es compartido para todo el equipo:
- **Carpeta raíz:** https://drive.google.com/drive/folders/13cEoJyVieAmc_S6aBMOoEt9us9gJT877

Solo necesitas configurar tus credenciales personales en `.env` si quieres cambiar los paths:

```env
# Opcional: ruta al client secret (default: ./gcp-oauth.keys.json)
GOOGLE_CLIENT_SECRET_PATH=./gcp-oauth.keys.json

# Opcional: ruta al token (default: ./token_styles.json)
GOOGLE_DRIVE_MCP_TOKEN_FILE=./token_styles.json

# Opcional: ID del doc a formatear
GOOGLE_DOCS_ID=REEMPLAZAR_POR_DOC_ID_DENTRO_DE_CARPETA_RAIZ
```

Nota: `GOOGLE_DOCS_ID` debe pertenecer a un documento dentro de la carpeta raíz compartida.

---

### Paso 6 — Generar el token de sesión

Este paso abre el navegador para autorizar el acceso con tu cuenta de Google.
Solo es necesario hacerlo una vez (el token se renueva automáticamente).

```bash
# Desde la raíz del proyecto, con el entorno virtual activo
python drive_mcp/auth_first_time.py
```

El navegador abre una pantalla de Google. Seleccionar la cuenta de Google
cargada como usuario de prueba en el Paso 3. Aceptar los permisos solicitados.

Al finalizar, se crea automáticamente `token_styles.json` en la raíz del proyecto.
Este archivo contiene el access token y el refresh token.

> ⚠️ `token_styles.json` contiene datos de sesión sensibles. Nunca subirlo al repositorio
> (ya está en `.gitignore`).

---

### Paso 7 — Verificar que el servidor arranca

Reiniciar el servidor `drive_mcp` desde VS Code (panel MCP → ícono de recarga).

Si el servidor aparece como **Running**, la configuración es correcta.
Desde el chat del agente ya podés usar las herramientas de Drive.

---

## Variables de entorno

### Obligatoria (No modificable)

| Variable | Descripción | Valor |
|---|---|---|
| `DRIVE_ROOT_FOLDER_ID` | **Carpeta raíz compartida del equipo** — Hardcodeada en `config.py`. TODOS los archivos deben estar aquí. | `13cEoJyVieAmc_S6aBMOoEt9us9gJT877` |

### Opcionales (con defaults sensatos)

| Variable | Descripción | Default |
|---|---|---|
| `GOOGLE_CLIENT_SECRET_PATH` | Ruta al client secret descargado de Google Cloud Console | `./gcp-oauth.keys.json` |
| `GOOGLE_DRIVE_MCP_TOKEN_FILE` | Ruta al token de sesión OAuth2 | `./token_styles.json` |
| `GOOGLE_DOCS_ID` | *(Obsoleto para el flujo MCP)* Fallback para `apply_document_styles` sin `document_id`. Solo útil si usás `apply_styles.py` como script standalone. | — |

> **Nota:** `GOOGLE_DOCS_ID` ya no es necesaria para el equipo. Todos los MCP tools aceptan `document_id` como parámetro directo (ID o link). Es solo un fallback de compatibilidad.

Importante: si el documento está fuera de la carpeta raíz compartida, la operación será bloqueada por seguridad.

---

## Herramientas disponibles

### `list_files`
Lista archivos en Google Drive (dentro de la carpeta raíz compartida).

| Parámetro | Tipo | Requerido | Descripción |
|---|---|---|---|
| `folder_id` | string | No | ID de la subcarpeta (se ve en la URL de Drive) |
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

### `apply_document_styles`
Aplica estilos a un Google Doc usando perfiles dinámicos y overrides opcionales.

| Parámetro | Tipo | Requerido | Descripción |
|---|---|---|---|
| `document_id` | string | No | ID del documento. Si se omite usa `GOOGLE_DOCS_ID`. |
| `profile` | string | No | Perfil de estilos. Default: `tesis_default`. |
| `overrides` | object | No | Ajustes parciales del perfil (ej. color o fuente). |

Perfiles disponibles por defecto:
- `tesis_default`
- `entrega_formal`

Ejemplo de override:

```json
{
  "profile": "tesis_default",
  "overrides": {
    "font_family": "Arial",
    "colors": {
      "heading": {"red": 0.0, "green": 0.4, "blue": 0.8}
    }
  }
}
```

---

### `edit_document_replace` ✨ NUEVO

Busca y reemplaza texto en un Google Doc.
**Acepta `document_id` como ID directo O como link de Google Docs.**

| Parámetro | Tipo | Requerido | Descripción |
|---|---|---|---|
| `document_id` | string | **Sí** | ID del documento O link: `https://docs.google.com/document/d/...` |
| `find_text` | string | **Sí** | Texto a buscar |
| `replacement_text` | string | **Sí** | Texto de reemplazo |
| `match_case` | boolean | No | Respetar mayúsculas (default: False) |
| `all_occurrences` | boolean | No | Reemplazar todas (default: True) |

**Ejemplo:**
```json
{
  "document_id": "1XyZ123abc...",
  "find_text": "TODO",
  "replacement_text": "HECHO",
  "all_occurrences": true
}
```

---

### `edit_document_append` ✨ NUEVO

Agrega texto al final de un Google Doc con formato opcional.
**Acepta `document_id` como ID directo O como link de Google Docs.**

| Parámetro | Tipo | Requerido | Descripción |
|---|---|---|---|
| `document_id` | string | **Sí** | ID del documento O link: `https://docs.google.com/document/d/...` |
| `text` | string | **Sí** | Texto a agregar |
| `bold` | boolean | No | Negrita (default: False) |
| `italic` | boolean | No | Itálica (default: False) |
| `font_size` | integer | No | Tamaño de fuente en puntos (ej: 12) |

**Ejemplo:**
```json
{
  "document_id": "https://docs.google.com/document/d/1XyZ123abc/edit",
  "text": "Párrafo agregado\n\n",
  "bold": true,
  "font_size": 14
}
```

---

### `edit_document_replace_and_format` ✨ NUEVO

Reemplaza texto Y aplica formato en una sola operación.
**Acepta `document_id` como ID directo O como link de Google Docs.**

| Parámetro | Tipo | Requerido | Descripción |
|---|---|---|---|
| `document_id` | string | **Sí** | ID del documento O link: `https://docs.google.com/document/d/...` |
| `find_text` | string | **Sí** | Texto a buscar |
| `replacement_text` | string | **Sí** | Texto de reemplazo |
| `bold` | boolean | No | Negrita del reemplazo (default: False) |
| `italic` | boolean | No | Itálica del reemplazo (default: False) |
| `font_size` | integer | No | Tamaño de fuente en puntos |
| `match_case` | boolean | No | Respetar mayúsculas (default: False) |
| `all_occurrences` | boolean | No | Reemplazar todas (default: True) |

**Ejemplo:**
```json
{
  "document_id": "1XyZ123abc...",
  "find_text": "IMPORTANTE",
  "replacement_text": "IMPORTANTE",
  "bold": true,
  "italic": true,
  "font_size": 14
}
```

---

### `create_document` ✨ NUEVO

Crea un nuevo Google Docs en una carpeta específica.

| Parámetro | Tipo | Requerido | Descripción |
|---|---|---|---|
| `name` | string | **Sí** | Nombre del documento |
| `folder_id` | string | No | ID de la carpeta destino (opcional, usa raíz si omitido) |

**Ejemplo:**
```json
{
  "name": "Informe Mensual - Abril",
  "folder_id": "19usCpkzcL0WizQSb1k12wIoEMPeEBMZX"
}
```

Retorna: `document_id`, `name`, `link` del nuevo documento.

---

### `create_folder` ✨ NUEVO

Crea una nueva carpeta en Google Drive.

| Parámetro | Tipo | Requerido | Descripción |
|---|---|---|---|
| `name` | string | **Sí** | Nombre de la carpeta |
| `folder_id` | string | No | ID de la carpeta padre (opcional, usa raíz si omitido) |

**Ejemplo:**
```json
{
  "name": "Entregables - Abril",
  "folder_id": "19usCpkzcL0WizQSb1k12wIoEMPeEBMZX"
}
```

Retorna: `folder_id`, `name`, `link` de la nueva carpeta.

---

### `copy_file` ✨ NUEVO

Copia un archivo o carpeta en Google Drive. Si es una carpeta, copia toda la estructura.

| Parámetro | Tipo | Requerido | Descripción |
|---|---|---|---|
| `file_id` | string | **Sí** | ID del archivo o carpeta a copiar |
| `new_name` | string | **Sí** | Nombre de la copia |
| `destination_folder_id` | string | No | ID de la carpeta destino (opcional, usa misma ubicación si omitido) |

**Ejemplo:**
```json
{
  "file_id": "147eDbi4bVV1E1sSoyGnreMHtViS_JfMNKpaz8Is6VPg",
  "new_name": "Copia de Informe - Backup",
  "destination_folder_id": "19usCpkzcL0WizQSb1k12wIoEMPeEBMZX"
}
```

Retorna: `original_file_id`, `new_file_id`, `new_name`, `link` de la copia.

---

### `rename_file` ✨ NUEVO

Renombra un archivo o carpeta sin moverlo de ubicación.

| Parámetro | Tipo | Requerido | Descripción |
|---|---|---|---|
| `file_id` | string | **Sí** | ID del archivo o carpeta a renombrar |
| `new_name` | string | **Sí** | Nuevo nombre |

**Ejemplo:**
```json
{
  "file_id": "147eDbi4bVV1E1sSoyGnreMHtViS_JfMNKpaz8Is6VPg",
  "new_name": "Informe Final - v2.0"
}
```

Retorna: `file_id`, `old_name`, `new_name`, `link` del archivo renombrado.

---

## ✨ Flujo sin modificar `.env`

Ahora el equipo puede pedir ediciones directamente sin tener que cambiar el `.env`:

**Antes:**
```
Usuario: "Edita el documento XXX"
Agente: "Necesito actualizar GOOGLE_DOCS_ID en .env..."
```

**Ahora:**
```
Usuario: "Edita https://docs.google.com/document/d/1XyZ123abc/edit"
Agente: MCP call con tool (ya funciona, sin tocar .env)
```

Los 3 tools de edición (`edit_document_*`) aceptan automáticamente links o IDs
con la misma función.

---

## Estructura del módulo

```
drive_mcp/
├── __init__.py             # Marca el paquete Python
├── server.py               # Servidor MCP (JSON-RPC 2.0) - 12 herramientas
├── apply_styles.py         # Script para aplicar estilos al Doc
├── auth_first_time.py      # Script ÚNICO para autenticación inicial
├── auth.py                 # Gestión de autenticación OAuth2
├── config.py               # Configuración centralizada (carpeta raíz compartida)
├── constants.py            # Constantes (colores RGB, paleta)
├── style_profiles.py       # Perfiles dinámicos + merge de overrides
├── utils.py                # Utilities: extrae document_id de links
├── edit.py                 # Funciones de edición (replace, append, etc.)
├── file_ops.py             # Operaciones de archivos (create, copy, rename) ✨ NUEVO
├── security.py             # Validación de seguridad (carpeta raíz compartida)
├── styles.py               # Lógica de aplicación de estilos
└── README.md               # Esta documentación
```

### Flujo de autenticación

```
auth_first_time.py o apply_styles.py (carga .env)
  ↓
auth.py:get_credentials()
  ├─ Intenta cargar token guardado (token_styles.json)
  ├─ Si existe, intenta refrescarlo
  ├─ Si falla (token revocado), abre navegador OAuth
  └─ Guarda nuevo token para futuras ejecuciones
```

### Flujo de estilos dinámicos

```
tools/call -> apply_document_styles
  ↓
styles.py:apply_styles(profile_name, profile_overrides)
  ↓
style_profiles.py:get_style_profile()
  ├─ carga perfil base
  └─ aplica overrides runtime
```

### Flujo de edición flexible (nuevo)

```
tools/call -> edit_document_replace (o append, o replace_and_format)
  ↓
utils.py:normalize_document_input(document_id)
  ├─ Si es un link: extrae el ID del link
  ├─ Si es un ID: devuelve tal cual
  └─ Si es inválido: lanza ValueError
  ↓
edit.py:replace_text() / append_text() / replace_and_format()
  ├─ Usa Google Docs batchUpdate API
  └─ Devuelve metrics (occurrences_changed, success, etc.)
```

### Flujo de seguridad

```
Cualquier operación en Drive
  ↓
config.py (validación de carpeta raíz compartida)
  ├─ DRIVE_ROOT_FOLDER_ID = "13cEoJyVieAmc_S6aBMOoEt9us9gJT877"
  ├─ Hardcodeado para el equipo completo
  └─ No modificable por usuario
  ↓
security.py:validate_operation()
  ├─ Obtiene jerarquía de carpetas del archivo
  ├─ Verifica que esté dentro de la carpeta raíz compartida
  └─ Bloquea si está fuera del scope (PermissionError)
```

---

## Restricciones de seguridad

✅ **Permitido:**
- Acceder a archivos dentro de `13cEoJyVieAmc_S6aBMOoEt9us9gJT877` y sus subcarpetas
- Usar cualquier subcarpeta dentro de la raíz (wearables/, Proyecto mineria/, etc.)
- Crear nuevos archivos dentro de la raíz
- **Pasar links completos de Google Docs sin extraer el ID manualmente**

❌ **Bloqueado:**
- Acceder a archivos fuera de la carpeta raíz
- Crear archivos en otras carpetas de Drive
- Cualquier operación que intente escapar del scope del proyecto
- **Editar documentos pasando links inválidos o IDs malformados**

La validación es automática — intentos de acceso fuera del scope lanzarán `PermissionError` con mensaje descriptivo.
