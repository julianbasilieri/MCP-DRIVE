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
GOOGLE_DOCS_ID=13OeKBKdRtsLYBhN-ro0cGLVTW_NkQgg1eSzaBZpaIuU
```

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
| `GOOGLE_DOCS_ID` | ID del documento Google Docs a formatear | `13OeKBKdRtsLYBhN-ro0cGLVTW_NkQgg1eSzaBZpaIuU` |

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

> La primera ejecución abre el navegador para autorizar (ver Paso 6).
> Las siguientes usan el token guardado en `token_styles.json` y no requieren intervención.

---

## Estructura del módulo

```
drive_mcp/
├── __init__.py             # Marca el paquete Python
├── server.py               # Servidor MCP (JSON-RPC 2.0) - 4 herramientas
├── apply_styles.py         # Script para aplicar estilos al Doc
├── auth_first_time.py      # Script ÚNICO para autenticación inicial
├── auth.py                 # Gestión de autenticación OAuth2
├── config.py               # Configuración centralizada (carpeta raíz compartida)
├── constants.py            # Constantes (colores RGB, paleta)
├── security.py             # Validación de seguridad (carpeta raíz compartida)
├── styles.py               # Lógica de aplicación de estilos
└── README.md               # Esta documentación
```

### Flujo de autenticación

```
apply_styles.py (carga .env)
  ↓
auth.py:get_credentials()
  ├─ Intenta cargar token guardado (token_styles.json)
  ├─ Si existe, intenta refrescarlo
  ├─ Si falla (token revocado), abre navegador OAuth
  └─ Guarda nuevo token para futuras ejecuciones
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

❌ **Bloqueado:**
- Acceder a archivos fuera de la carpeta raíz
- Crear archivos en otras carpetas de Drive
- Cualquier operación que intente escapar del scope del proyecto

La validación es automática — intentos de acceso fuera del scope lanzarán `PermissionError` con mensaje descriptivo.
