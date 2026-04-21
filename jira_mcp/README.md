# Jira MCP

Servidor MCP (Model Context Protocol) interno para interactuar con Jira Cloud.
Permite al agente de IA listar, crear, editar y gestionar issues directamente desde el chat.

---

## Configuración paso a paso

### Paso 1 — Obtener la URL de tu instancia de Jira

1. Iniciar sesión en [https://www.atlassian.com/](https://www.atlassian.com/)
2. En el panel de Atlassian, hacer clic en el producto **Jira Software**
3. La URL del navegador tendrá el formato `https://TU_DOMINIO.atlassian.net`
4. Copiar esa URL completa — es el valor de `JIRA_HOST`

---

### Paso 2 — Generar el API Token de Jira

1. Ir a [https://id.atlassian.com/manage-profile/security/api-tokens](https://id.atlassian.com/manage-profile/security/api-tokens)
2. Hacer clic en **Crear token de API**
3. Poner un nombre descriptivo (ej: `PPS-MCP`) y hacer clic en **Crear**
4. Copiar el token generado **en ese momento** — no se puede ver de nuevo después

> ⚠️ El token tiene los mismos permisos que tu cuenta de Jira. Guardarlo únicamente
> en `.env.local` y nunca subirlo al repositorio.

---

### Paso 3 — Configurar las variables de entorno

1. Copiar el archivo de ejemplo:
   ```bash
   cp .env.example .env.local
   ```
2. Abrir `.env.local` y completar con los valores obtenidos en los pasos anteriores:
   ```bash
   JIRA_HOST=https://TU_DOMINIO.atlassian.net
   JIRA_EMAIL=el_email_con_el_que_iniciás_sesión_en_jira@example.com
   JIRA_API_TOKEN=el_token_copiado_en_el_paso_2
   ```
3. Guardar el archivo. No hace falta reiniciar nada — el launcher carga `.env.local`
   automáticamente cada vez que VS Code inicia el servidor.

---

### Paso 4 — Variable opcional: proyecto por defecto

Si tu instancia de Jira tiene un solo proyecto, el servidor lo detecta automáticamente.
Si tiene varios, podés fijar uno para que sea el default cuando no se especifica en el pedido:

```bash
# Agregar en .env.local
JIRA_DEFAULT_PROJECT=CLAVE_DEL_PROYECTO
```

La clave del proyecto es la sigla que aparece antes del número en cada issue
(ej: en `PPS-42`, la clave es `PPS`).

---

### Paso 5 — Verificar que el servidor arranca

Reiniciar el servidor `jira_mcp` desde VS Code (panel MCP → ícono de recarga).

Si el servidor aparece como **Running**, la configuración es correcta.
Desde el chat del agente ya podés usar las herramientas de Jira.

Si aparece error, revisar:
- Que `JIRA_HOST` tenga el formato correcto (`https://dominio.atlassian.net`, sin barra al final)
- Que `JIRA_EMAIL` sea exactamente el email con el que iniciás sesión en Atlassian
- Que el token no tenga espacios ni saltos de línea al pegarlo

---

## Herramientas disponibles

### `get_projects`
Devuelve la lista de proyectos disponibles en la instancia de Jira.

---

### `list_issues`
Lista issues usando una query JQL. Si no se envía `jql`, usa el proyecto por defecto.

| Parámetro | Tipo | Requerido | Descripción |
|---|---|---|---|
| `jql` | string | No | Query JQL (ej: `project = PPS AND status = "In Progress"`) |
| `max_results` | integer | No | Máximo de resultados (default: 50) |

---

### `create_issue`
Crea un nuevo issue. Si no se envía `project`, usa el proyecto por defecto.

| Parámetro | Tipo | Requerido | Descripción |
|---|---|---|---|
| `issue_type` | string | **Sí** | Tipo: `Story`, `Task`, `Bug`, `Epic`, `Sub-task` |
| `summary` | string | **Sí** | Título del issue |
| `description` | string | No | Descripción del issue |
| `project` | string | No | Clave del proyecto (ej: `PPS`) |

---

### `get_issue`
Obtiene todos los detalles de un issue por su clave.

| Parámetro | Tipo | Requerido | Descripción |
|---|---|---|---|
| `issue_key` | string | **Sí** | Clave del issue (ej: `PPS-42`) |

---

### `edit_issue`
Edita el título y/o descripción de un issue existente.

| Parámetro | Tipo | Requerido | Descripción |
|---|---|---|---|
| `issue_key` | string | **Sí** | Clave del issue |
| `summary` | string | No | Nuevo título |
| `description` | string | No | Nueva descripción |

---

### `transition_issue`
Cambia el estado de un issue usando el nombre o ID de la transición.

| Parámetro | Tipo | Requerido | Descripción |
|---|---|---|---|
| `issue_key` | string | **Sí** | Clave del issue |
| `transition` | string | **Sí** | Nombre o ID de transición (ej: `In Progress`, `Done`) |
| `comment` | string | No | Comentario opcional al transicionar |

> Si el nombre de transición no existe, la respuesta incluye `available_transitions`
> con los nombres e IDs válidos para ese issue.

---

### `assign_issue`
Asigna un responsable a un issue.

| Parámetro | Tipo | Requerido | Descripción |
|---|---|---|---|
| `issue_key` | string | **Sí** | Clave del issue |
| `assignee` | string | **Sí** | `accountId` del usuario en Jira Cloud |

> El `accountId` se puede obtener desde `get_issue` (campo `assignee`) o desde
> el perfil del usuario en Jira: `https://TU_DOMINIO.atlassian.net/jira/people`.

---

### `add_comment`
Agrega un comentario a un issue.

| Parámetro | Tipo | Requerido | Descripción |
|---|---|---|---|
| `issue_key` | string | **Sí** | Clave del issue |
| `comment` | string | **Sí** | Texto del comentario |

---

## Archivos del módulo

```
jira_mcp/
├── __init__.py   # Marca el paquete Python
├── server.py     # Servidor MCP (JSON-RPC 2.0)
└── README.md     # Esta documentación
```
