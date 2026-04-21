---
name: thesis-doc
description: Edita y ejecuta los scripts apply_styles.py y update_dates.py que aplican estilos y actualizan fechas en el Google Doc de la tesis PPS. Usar cuando el usuario quiera cambiar colores, fuentes, fechas de sprints o el DOC_ID del documento.
---

# Thesis Doc — Skill de gestión de estilos y fechas

Este skill cubre la edición y ejecución de los dos scripts Python que mantienen el documento de tesis en Google Docs.

## Archivos del proyecto

| Archivo | Propósito |
|---|---|
| `apply_styles.py` | Aplica fuente, colores y estilos tipográficos al Google Doc |
| `update_dates.py` | Reemplaza fechas de sprints en el Google Doc |
| `gcp-oauth.keys.json` | Credenciales OAuth de GCP (no modificar) |
| `token_styles.json` | Token de sesión OAuth (se renueva automáticamente) |

## Parámetros de estilo actuales (`apply_styles.py`)

```python
DOC_ID   = "13OeKBKdRtsLYBhN-ro0cGLVTW_NkQgg1eSzaBZpaIuU"
FONT     = "Montserrat"

BLUE_H1H2 = {"red": 7/255,  "green": 123/255, "blue": 222/255}  # #077BDE  H1, H2, TITLE, H4
BLUE_H3   = {"red": 5/255,  "green": 90/255,  "blue": 158/255}  # #055A9E  H3
BLACK     = {"red": 0,       "green": 0,        "blue": 0}        # #000000  cuerpo

# Pesos de fuente
NORMAL_WEIGHT  = 400   # Regular     → NORMAL_TEXT
HEADING_WEIGHT = 700   # Bold        → H1, H2, TITLE, H4, mayúsculas
H3_WEIGHT      = 600   # SemiBold    → H3
```

## Reglas de estilo (NO cambiar sin instrucción explícita)

- **Fuente universal**: Montserrat en todo el documento, incluidas las celdas de tablas.
- **H1 / H2 / TITLE / H4**: `#077BDE`, Bold 700, sin itálica.
- **H3**: `#055A9E`, SemiBold 600, itálica.
- **NORMAL_TEXT**: negro puro, Regular 400, sin itálica.
- **Líneas en mayúsculas** (detectadas automáticamente): `#077BDE`, Bold 700.
- Los estilos nombrados del documento se actualizan para que nuevos párrafos hereden Montserrat sin re-ejecutar el script.

## Cómo modificar `apply_styles.py`

### Cambiar el documento destino
Editar únicamente la constante `DOC_ID` en la línea correspondiente del archivo. Actualizar también `DOC_ID` en `update_dates.py` si aplica.

### Cambiar un color
1. Identificar qué constante corresponde (`BLUE_H1H2`, `BLUE_H3` o `BLACK`).
2. Convertir el color hex a componentes RGB divididos entre 255.
3. Reemplazar **solo** los valores numéricos dentro del dict correspondiente.
4. Los mismos valores deben actualizarse en `build_named_style_requests()` si el color aparece allí.

### Cambiar la fuente
Reemplazar todas las ocurrencias de `"Montserrat"` por el nuevo nombre de fuente (la fuente debe estar disponible en Google Docs).

### Agregar un nuevo nivel de heading
Agregar una entrada en `build_named_style_requests()` y una condición `elif` en el loop principal de `apply_styles()`.

## Parámetros de fechas actuales (`update_dates.py`)

```python
DOC_ID = "13OeKBKdRtsLYBhN-ro0cGLVTW_NkQgg1eSzaBZpaIuU"
TOKEN_FILE = "token_styles.json"   # mismo token que apply_styles.py
```

El dict `DATE_MAP` contiene pares `(fecha_antigua, fecha_nueva)` en formato `DD/MM/AAAA`.

El dict `TEXT_MAP` contiene pares `(texto_antiguo, texto_nuevo)` para cadenas de texto libre.

## Cómo modificar `update_dates.py`

### Actualizar fechas de sprint
1. En `DATE_MAP`, reemplazar el lado izquierdo (fecha antigua) con las fechas actualmente en el documento y el lado derecho con las fechas nuevas deseadas.
2. Respetar el orden cronológico de los pares.
3. Incluir feriados como comentarios (`# nombre_feriado`) para documentar los saltos.

### Agregar reemplazos de texto libre
Agregar entradas a `TEXT_MAP` con el formato `("texto_a_reemplazar", "texto_nuevo")`.

### Mecanismo de doble fase (no romper)
`update_dates.py` usa **placeholders intermedios** (`%%D00%%`, `%%D01%%`, …) para evitar que una fecha nueva coincida con una fecha antigua en la misma pasada. Este patrón **debe preservarse** al modificar el script.

## Entorno de ejecución

- **Virtualenv**: `.venv` en la raíz del proyecto.
- **Activar**: `source .venv/Scripts/activate` (Windows/Git Bash).
- **Dependencias**: `google-auth`, `google-auth-oauthlib`, `google-api-python-client`.

## Workflow al editar y ejecutar

1. Leer el archivo que se va a modificar con `read_file` antes de editar.
2. Aplicar el cambio con `replace_string_in_file` o `multi_replace_string_in_file`.
3. Verificar errores con `get_errors`.
4. Ejecutar el script en terminal con el virtualenv activo:

```bash
source .venv/Scripts/activate && python apply_styles.py
```

```bash
source .venv/Scripts/activate && python update_dates.py
```

5. Confirmar en la salida el mensaje `✅ ... correctamente.`

## Errores comunes

| Error | Causa probable | Solución |
|---|---|---|
| `google.auth.exceptions.RefreshError` | Token expirado o revocado | Borrar `token_styles.json` y volver a ejecutar (abrirá el browser para re-autenticar) |
| `HttpError 400` en batchUpdate | `startIndex >= endIndex` en algún párrafo vacío | El guard `if start >= end: continue` ya lo previene; verificar que no se haya eliminado |
| Fuente no aplicada en tablas | El rango del documento no incluye celdas | Verificar que `collect_paragraphs` recorra `tableRows → tableCells` |
