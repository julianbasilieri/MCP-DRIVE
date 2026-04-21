---
name: jerarquia-issues
description: Define la jerarquia oficial de issues para este proyecto y como mapear cada tipo en Jira. Usar siempre que se cree, edite o valide la estructura de trabajo.
---

# Jerarquia de Issues

Este skill fija el orden jerarquico para evitar inconsistencias en el backlog.

## Orden oficial

1. Epic
2. Story / Feature
3. Task / Bug
4. Sub-task

## Reglas obligatorias

- `Feature` y `Story` estan en el mismo nivel jerarquico.
- `Task` y `Bug` estan en el mismo nivel jerarquico.
- No crear `Sub-task` sin issue padre de nivel superior.
- No saltar niveles al descomponer trabajo. Si un item es grande, primero dividir en `Story` o `Feature`.
- Si hay duda entre `Story` y `Task`:
- Usar `Story` para valor funcional visible al usuario.
- Usar `Task` para trabajo tecnico interno sin valor funcional directo.
- Si hay duda entre `Bug` y `Task`:
- Usar `Bug` si corrige comportamiento incorrecto existente.
- Usar `Task` si es implementacion nueva o mejora tecnica no regresiva.

## Uso en Jira

- `Epic`: iniciativa grande o capacidad amplia.
- `Story` / `Feature`: requerimiento funcional que aporta valor.
- `Task`: trabajo tecnico o actividad operativa.
- `Bug`: defecto detectado.
- `Sub-task`: parte concreta de ejecucion dentro de un issue padre.

## Checklist obligatorio antes de crear un issue

- El tipo elegido respeta el orden oficial.
- El issue no pertenece a un nivel inferior por error.
- Si es `Sub-task`, existe y esta definido el issue padre.
- Si es `Bug`, existe evidencia de fallo actual.
- Si es `Feature`, confirmar que no corresponde a `Epic` por alcance.

## Regla de desempate rapido

- Alcance transversal o muy amplio: `Epic`.
- Funcionalidad entregable al usuario: `Story` o `Feature`.
- Trabajo tecnico puntual: `Task`.
- Correccion de defecto: `Bug`.
- Trabajo atomico dependiente de otro issue: `Sub-task`.
