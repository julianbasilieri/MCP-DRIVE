# Jira MCP

Servidor MCP (Model Context Protocol) interno para interactuar con Jira Cloud.
Permite al agente de IA listar, crear, editar y gestionar issues directamente desde el chat.

---

## Configuración

### Variables de entorno requeridas

Definir en `.env` o `.env.local` en la raíz del proyecto:

```bash
JIRA_HOST=https://TU_DOMINIO.atlassian.net
JIRA_EMAIL=tu_email@example.com
JIRA_API_TOKEN=tu_api_token
```

> ⚠️ Nunca pongas el token en `.vscode/mcp.json`. El launcher `scripts/run_jira_mcp.py`
> carga las variables desde `.env` / `.env.local` automáticamente.

### Variable opcional

```bash
# Fuerza un proyecto por defecto. Si no se define, el servidor autodetecta
# el único proyecto disponible o el que tenga "scrum" en el nombre/clave.
JIRA_DEFAULT_PROJECT=CLAVE_DEL_PROYECTO
```

### Obtener el API Token de Jira

1. Ir a [https://id.atlassian.com/manage-profile/security/api-tokens](https://id.atlassian.com/manage-profile/security/api-tokens)
2. Crear un nuevo token → copiar el valor
3. Pegarlo en `JIRA_API_TOKEN` dentro de `.env.local`

### Cómo arranca el servidor

El servidor es lanzado por VS Code a través de `.vscode/mcp.json`:

```json
"jira_mcp": {
  "type": "stdio",
  "command": "./.venv/Scripts/python.exe",
  "args": ["scripts/run_jira_mcp.py"]
}
```

Para probarlo manualmente:

```bash
python scripts/run_jira_mcp.py
```

Para correr la suite de pruebas de integración:

```bash
python scripts/test_jira_mcp.py
```

---

## Herramientas disponibles

### `get_projects`
Devuelve la lista de proyectos disponibles en Jira.

```json
{}
```

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
| `issue_type` | string | **Sí** | Tipo de issue: `Story`, `Task`, `Bug`, `Epic`, `Sub-task` |
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

> Si la transición no existe, la respuesta incluye `available_transitions` con las opciones válidas.

---

### `assign_issue`
Asigna un responsable a un issue.

| Parámetro | Tipo | Requerido | Descripción |
|---|---|---|---|
| `issue_key` | string | **Sí** | Clave del issue |
| `assignee` | string | **Sí** | `accountId` del usuario en Jira Cloud |

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
