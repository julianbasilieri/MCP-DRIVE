# PPS — Scripts de Google Docs

Scripts Python para automatizar tareas sobre un documento de Google Docs:

- **`apply_styles.py`** — Aplica estilos de fuente y color a títulos (`H1`, `H2`, `H3`) usando Montserrat y la paleta `#077BDE` / `#055A9E`.
- **`update_dates.py`** — Reemplaza fechas de sprints en el documento usando un mapa de fechas antiguas → nuevas.

---

## Requisitos previos

- Python 3.10+
- Una cuenta de Google con acceso al documento
- Un proyecto en [Google Cloud Console](https://console.cloud.google.com/) con las APIs habilitadas

### APIs que deben estar habilitadas en el proyecto GCP

- Google Docs API
- Google Drive API

---

## Configurar credenciales OAuth2

### 1. Crear credenciales en Google Cloud Console

1. Abrí [https://console.cloud.google.com/apis/credentials](https://console.cloud.google.com/apis/credentials)
2. Hacé clic en **Crear credenciales → ID de cliente de OAuth 2.0**
3. Tipo de aplicación: **Aplicación de escritorio**
4. Descargá el archivo JSON generado
5. Renombralo a `gcp-oauth.keys.json` y colocalo en la raíz del proyecto

> **Importante:** este archivo contiene el `client_secret` y **nunca debe subirse al repositorio**. Ya está listado en `.gitignore`.

### 2. Configurar la pantalla de consentimiento OAuth

1. En el menú lateral, ir a **APIs y servicios → Pantalla de consentimiento de OAuth**
2. Tipo: **Externo** (o Interno si usás Google Workspace)
3. Completar nombre de la app y correo de soporte
4. En **Alcances**, agregar:
   - `https://www.googleapis.com/auth/documents`
   - `https://www.googleapis.com/auth/drive`
5. En **Usuarios de prueba**, agregar la cuenta de Google que usarás

---

## Configuración de MCP (Model Context Protocol)

### Archivos sensibles

Los archivos con credenciales están **excluidos de Git** por seguridad:
- `.vscode/mcp.json` — Configuración de MCPs con tokens/credenciales
- `gcp-oauth.keys.json` — Credenciales de Google Cloud

### Usar el archivo de ejemplo

1. Copia `.vscode/mcp.example.json` a `.vscode/mcp.json`
2. Rellena tus propias credenciales:
   - **Google Workspace**: ruta al archivo `gcp-oauth.keys.json`
   - **Jira**: Tu URL de Jira, email y API token

```bash
cp .vscode/mcp.example.json .vscode/mcp.json
# Edita mcp.json con tus credenciales
```

> ⚠️ **Importante:** Nunca commits `.vscode/mcp.json`. Si accidentalmente lo subiste, regenera los tokens inmediatamente.

---

```bash
# Crear entorno virtual
python -m venv .venv

# Activar (Windows)
.venv\Scripts\activate

# Activar (Linux/macOS)
source .venv/bin/activate

# Instalar dependencias
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

---

## Primer uso — Autorización

La primera vez que corras cualquiera de los scripts, se abrirá una ventana del navegador para que autorices el acceso con tu cuenta de Google.

```bash
python apply_styles.py
```

Después de autorizar, se crea automáticamente el archivo `token_styles.json` con el token de acceso y el refresh token. Las siguientes ejecuciones no requieren autorización manual.

> **Importante:** `token_styles.json` también contiene datos sensibles y **nunca debe subirse al repositorio**. Ya está cubierto por `.gitignore` (`token_*.json`).

---

## Uso

```bash
# Aplicar estilos al documento
python apply_styles.py

# Actualizar fechas de sprints
python update_dates.py
```

---

## Estructura del proyecto

```
PPS/
├── apply_styles.py        # Aplica estilos de fuente y color
├── update_dates.py        # Actualiza fechas de sprints
├── gcp-oauth.keys.json    # ⚠️ Credenciales OAuth — NO subir al repo
├── token_styles.json      # ⚠️ Token de sesión — NO subir al repo (generado automáticamente)
├── .gitignore
└── README.md
```

---

## Seguridad

Los archivos sensibles están excluidos del repositorio por `.gitignore`:

| Archivo | Contenido | Estado |
|---|---|---|
| `gcp-oauth.keys.json` | `client_id` y `client_secret` de GCP | Ignorado |
| `token_*.json` | Access token y refresh token | Ignorado |

Si accidentalmente ya subiste alguno de estos archivos, **revocá las credenciales de inmediato** en la [consola de GCP](https://console.cloud.google.com/apis/credentials) y generá nuevas.
