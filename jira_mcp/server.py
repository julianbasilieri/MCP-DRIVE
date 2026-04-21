#!/usr/bin/env python3
"""
MCP Server para Jira Cloud
Permite crear y ver issues en Jira
"""

import json
import sys
import os
import logging
from jira import JIRA

# Configurar logging para stderr
logging.basicConfig(
    stream=sys.stderr,
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class JiraMCPServer:
    def __init__(self):
        self.jira_host = os.getenv('JIRA_HOST', '').rstrip('/')
        self.jira_email = os.getenv('JIRA_EMAIL')
        self.jira_token = os.getenv('JIRA_API_TOKEN')
        self.default_project_key = os.getenv('JIRA_DEFAULT_PROJECT', '').strip().upper() or None
        self.jira = None
        self.request_id = 0
        
        logger.debug(f"Inicializando servidor con host: {self.jira_host}")
        
        if not all([self.jira_host, self.jira_email, self.jira_token]):
            raise ValueError("Faltan variables de entorno: JIRA_HOST, JIRA_EMAIL, JIRA_API_TOKEN")
        
        self.connect()
    
    def connect(self):
        """Conectar a Jira Cloud"""
        try:
            logger.debug("Conectando a Jira...")
            self.jira = JIRA(
                server=self.jira_host,
                basic_auth=(self.jira_email, self.jira_token),
                timeout=30
            )
            logger.debug("Conexión a Jira exitosa")
        except Exception as e:
            logger.error(f"No se pudo conectar a Jira: {e}")
            raise RuntimeError(f"No se pudo conectar a Jira: {e}")
    
    def get_projects(self):
        """Obtener lista de proyectos disponibles"""
        try:
            projects = self.jira.projects()
            return {
                "success": True,
                "projects": [
                    {
                        "key": p.key,
                        "name": p.name,
                    }
                    for p in projects
                ]
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _resolve_default_project_key(self):
        """Resolver proyecto por defecto sin pedirlo al usuario."""
        if self.default_project_key:
            return self.default_project_key

        projects = self.jira.projects()
        if not projects:
            raise RuntimeError("No hay proyectos disponibles en Jira para usar como default")

        scrum_projects = [
            p for p in projects
            if "scrum" in p.key.lower() or "scrum" in p.name.lower()
        ]

        if len(scrum_projects) == 1:
            self.default_project_key = scrum_projects[0].key
            logger.debug(f"Proyecto default autodetectado (SCRUM): {self.default_project_key}")
            return self.default_project_key

        if len(projects) == 1:
            self.default_project_key = projects[0].key
            logger.debug(f"Proyecto default autodetectado (único): {self.default_project_key}")
            return self.default_project_key

        raise RuntimeError(
            "No se pudo resolver un proyecto default único. "
            "Definí JIRA_DEFAULT_PROJECT en .env o enviá project explícitamente."
        )
    
    def list_issues(self, jql=None, max_results=50):
        """Listar issues"""
        if jql is None:
            project_key = self._resolve_default_project_key()
            jql = f"project = {project_key} ORDER BY updated DESC"
        try:
            issues = self.jira.search_issues(jql, maxResults=max_results)
            return {
                "success": True,
                "issues": [
                    {
                        "key": issue.key,
                        "summary": issue.fields.summary,
                        "status": issue.fields.status.name,
                        "assignee": issue.fields.assignee.displayName if issue.fields.assignee else None,
                        "priority": issue.fields.priority.name if issue.fields.priority else None,
                    }
                    for issue in issues
                ]
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def create_issue(self, issue_type, summary, description="", project=None):
        """Crear un nuevo issue"""
        try:
            project_key = project or self._resolve_default_project_key()
            issue_dict = {
                'project': {'key': project_key},
                'summary': summary,
                'description': description,
                'issuetype': {'name': issue_type},
            }
            issue = self.jira.create_issue(fields=issue_dict)
            return {
                "success": True,
                "key": issue.key,
                "message": f"Issue {issue.key} creado exitosamente"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_issue(self, issue_key):
        """Obtener detalles de un issue"""
        try:
            issue = self.jira.issue(issue_key)
            return {
                "success": True,
                "issue": {
                    "key": issue.key,
                    "summary": issue.fields.summary,
                    "description": issue.fields.description,
                    "status": issue.fields.status.name,
                    "assignee": issue.fields.assignee.displayName if issue.fields.assignee else None,
                    "priority": issue.fields.priority.name if issue.fields.priority else None,
                    "created": issue.fields.created,
                    "updated": issue.fields.updated,
                }
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def edit_issue(self, issue_key, summary=None, description=None):
        """Editar campos básicos de un issue"""
        try:
            fields = {}
            if summary is not None:
                fields["summary"] = summary
            if description is not None:
                fields["description"] = description

            if not fields:
                return {
                    "success": False,
                    "error": "Debes enviar al menos un campo para editar: summary o description",
                }

            issue = self.jira.issue(issue_key)
            issue.update(fields=fields)
            return {
                "success": True,
                "key": issue_key,
                "updated_fields": list(fields.keys()),
                "message": f"Issue {issue_key} editado exitosamente",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def transition_issue(self, issue_key, transition, comment=None):
        """Cambiar estado de un issue por id o nombre de transición"""
        try:
            transitions = self.jira.transitions(issue_key)
            transition_id = None

            for t in transitions:
                if str(t.get("id")) == str(transition):
                    transition_id = t.get("id")
                    break
                if str(t.get("name", "")).lower() == str(transition).lower():
                    transition_id = t.get("id")
                    break

            if transition_id is None:
                available = [
                    {"id": t.get("id"), "name": t.get("name")}
                    for t in transitions
                ]
                return {
                    "success": False,
                    "error": (
                        f"Transición no encontrada: {transition}. "
                        "Usa un id o nombre válido."
                    ),
                    "available_transitions": available,
                }

            self.jira.transition_issue(issue_key, transition_id)
            if comment:
                self.jira.add_comment(issue_key, comment)

            updated_issue = self.jira.issue(issue_key)
            return {
                "success": True,
                "key": issue_key,
                "new_status": updated_issue.fields.status.name,
                "transition_id": transition_id,
                "message": f"Issue {issue_key} transicionado exitosamente",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def assign_issue(self, issue_key, assignee):
        """Asignar responsable a un issue"""
        try:
            # Jira Cloud usa accountId, pero algunos entornos aceptan username.
            # Intentamos primero con el método oficial y luego con update de campo.
            try:
                self.jira.assign_issue(issue_key, assignee)
            except Exception:
                issue = self.jira.issue(issue_key)
                issue.update(fields={"assignee": {"accountId": assignee}})

            updated_issue = self.jira.issue(issue_key)
            assignee_name = (
                updated_issue.fields.assignee.displayName
                if updated_issue.fields.assignee
                else None
            )
            return {
                "success": True,
                "key": issue_key,
                "assignee": assignee_name,
                "message": f"Issue {issue_key} asignado exitosamente",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def add_comment(self, issue_key, comment):
        """Agregar comentario a un issue"""
        try:
            created_comment = self.jira.add_comment(issue_key, comment)
            return {
                "success": True,
                "key": issue_key,
                "comment_id": getattr(created_comment, "id", None),
                "message": f"Comentario agregado a {issue_key}",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def handle_initialize(self, request):
        """Responder al mensaje initialize de MCP"""
        return {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {
                        "listTools": {},
                        "callTool": {}
                    }
                },
                "serverInfo": {
                    "name": "Jira MCP Server",
                    "version": "1.0.0"
                }
            }
        }
    
    def handle_list_resources(self, request):
        """Responder a list_resources"""
        return {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "result": {
                "resources": []
            }
        }
    
    def handle_list_tools(self, request):
        """Responder a list_tools"""
        return {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "result": {
                "tools": [
                    {
                        "name": "get_projects",
                        "description": "Obtiene la lista de proyectos disponibles en Jira",
                        "inputSchema": {
                            "type": "object",
                            "properties": {}
                        }
                    },
                    {
                        "name": "list_issues",
                        "description": "Lista los issues de un proyecto",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "jql": {"type": "string", "description": "JQL query"},
                                "max_results": {"type": "integer", "description": "Máximo de resultados"}
                            }
                        }
                    },
                    {
                        "name": "create_issue",
                        "description": "Crea un nuevo issue (usa proyecto default si no se envía project)",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "project": {"type": "string"},
                                "issue_type": {"type": "string"},
                                "summary": {"type": "string"},
                                "description": {"type": "string"}
                            },
                            "required": ["issue_type", "summary"]
                        }
                    },
                    {
                        "name": "get_issue",
                        "description": "Obtiene detalles de un issue",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "issue_key": {"type": "string"}
                            },
                            "required": ["issue_key"]
                        }
                    },
                    {
                        "name": "edit_issue",
                        "description": "Edita summary y/o description de un issue",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "issue_key": {"type": "string"},
                                "summary": {"type": "string"},
                                "description": {"type": "string"}
                            },
                            "required": ["issue_key"]
                        }
                    },
                    {
                        "name": "transition_issue",
                        "description": "Cambia estado de un issue usando id o nombre de transición",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "issue_key": {"type": "string"},
                                "transition": {"type": "string"},
                                "comment": {"type": "string"}
                            },
                            "required": ["issue_key", "transition"]
                        }
                    },
                    {
                        "name": "assign_issue",
                        "description": "Asigna responsable a un issue (accountId o identificador compatible)",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "issue_key": {"type": "string"},
                                "assignee": {"type": "string"}
                            },
                            "required": ["issue_key", "assignee"]
                        }
                    },
                    {
                        "name": "add_comment",
                        "description": "Agrega un comentario a un issue",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "issue_key": {"type": "string"},
                                "comment": {"type": "string"}
                            },
                            "required": ["issue_key", "comment"]
                        }
                    }
                ]
            }
        }
    
    def handle_call_tool(self, request):
        """Responder a call_tool"""
        params = request.get("params", {})
        tool_name = params.get("name")
        tool_input = params.get("arguments", {})
        
        logger.debug(f"Ejecutando herramienta: {tool_name} con argumentos: {tool_input}")
        
        try:
            if tool_name == "get_projects":
                result = self.get_projects()
            elif tool_name == "list_issues":
                result = self.list_issues(**tool_input)
            elif tool_name == "create_issue":
                result = self.create_issue(**tool_input)
            elif tool_name == "get_issue":
                result = self.get_issue(tool_input.get("issue_key"))
            elif tool_name == "edit_issue":
                result = self.edit_issue(**tool_input)
            elif tool_name == "transition_issue":
                result = self.transition_issue(**tool_input)
            elif tool_name == "assign_issue":
                result = self.assign_issue(**tool_input)
            elif tool_name == "add_comment":
                result = self.add_comment(**tool_input)
            else:
                result = {"success": False, "error": f"Herramienta desconocida: {tool_name}"}
            
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(result, indent=2, ensure_ascii=False)
                        }
                    ]
                }
            }
        except Exception as e:
            logger.error(f"Error ejecutando {tool_name}: {e}", exc_info=True)
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "error": {
                    "code": -32603,
                    "message": f"Error interno: {str(e)}"
                }
            }
    
    def handle_request(self, request):
        """Procesar una solicitud MCP"""
        try:
            method = request.get("method")
            
            if method == "initialize":
                return self.handle_initialize(request)
            elif method == "resources/list":
                return self.handle_list_resources(request)
            elif method == "tools/list":
                return self.handle_list_tools(request)
            elif method == "tools/call":
                return self.handle_call_tool(request)
            else:
                logger.warning(f"Método desconocido: {method}")
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "error": {
                        "code": -32601,
                        "message": f"Método no encontrado: {method}"
                    }
                }
        except Exception as e:
            logger.error(f"Error procesando request: {e}", exc_info=True)
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "error": {
                    "code": -32603,
                    "message": f"Error interno del servidor: {str(e)}"
                }
            }
    
    def run(self):
        """Ejecutar el servidor MCP"""
        logger.info("Iniciando servidor MCP...")
        
        for line in sys.stdin:
            try:
                line = line.strip()
                if not line:
                    continue
                
                logger.debug(f"Recibido: {line}")
                
                request = json.loads(line)
                response = self.handle_request(request)
                
                logger.debug(f"Enviando: {json.dumps(response)}")
                print(json.dumps(response, ensure_ascii=False))
                sys.stdout.flush()
            except json.JSONDecodeError as e:
                logger.error(f"JSON inválido: {e}")
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32700,
                        "message": f"Parse error: {str(e)}"
                    }
                }
                print(json.dumps(error_response))
                sys.stdout.flush()
            except Exception as e:
                logger.error(f"Error no capturado: {e}", exc_info=True)
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32603,
                        "message": f"Error interno: {str(e)}"
                    }
                }
                print(json.dumps(error_response))
                sys.stdout.flush()


if __name__ == "__main__":
    try:
        server = JiraMCPServer()
        server.run()
    except Exception as e:
        error_msg = f"Error al iniciar MCP: {str(e)}"
        logger.error(error_msg, exc_info=True)
        print(json.dumps({"error": error_msg}), file=sys.stderr)
        sys.exit(1)
