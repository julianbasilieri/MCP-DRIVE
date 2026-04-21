---
name: formato-escritura-issues
description: Estandar de redaccion para issues en Jira. Define estructura obligatoria, estilo de escritura y checklist de calidad antes de crear o actualizar un issue.
---

# Formato de Escritura de Issues

Este skill define como redactar issues en este proyecto.

## Idioma y tono

- Idioma obligatorio: espanol.
- Tono obligatorio: profesional.
- Evitar ambiguedad, terminos vagos y descripciones incompletas.

## Estructura obligatoria

Todo issue debe incluir estas secciones:

1. Titulo claro
2. Descripcion breve
3. Criterios de aceptacion en formato Given/When/Then
4. Prioridad
5. Estimacion (Story Points u horas)

## Requisito adicional para bugs

Si el tipo es `Bug`, agregar tambien:

1. Pasos de reproduccion

## Reglas del titulo

- Debe ser simple, especifico y facilmente diferenciable.
- Debe permitir distinguir el issue sin leer toda la descripcion.
- Evitar prefijos genericos como "Arreglo", "Mejora", "Cambios varios" sin contexto.

## Plantilla recomendada

### Titulo

- Una sola linea clara y concreta.

### Descripcion breve

- Contexto minimo del problema o necesidad.
- Resultado esperado en terminos funcionales.

### Criterios de aceptacion (Given/When/Then)

- Given: estado inicial.
- When: accion o evento.
- Then: resultado verificable.

### Prioridad

- Definir nivel explicito (por ejemplo: Baja, Media, Alta, Critica).

### Estimacion

- Informar Story Points u horas, segun corresponda.

### Pasos de reproduccion (solo Bug)

- Secuencia ordenada y reproducible.
- Resultado actual observado.
- Resultado esperado.

## Checklist obligatorio de validacion

Antes de crear o actualizar un issue, validar:

- El titulo es claro y diferenciable.
- La descripcion breve explica que se necesita.
- Hay criterios Given/When/Then verificables.
- Se asigno prioridad explicita.
- Se incluyo estimacion.
- Si es `Bug`, tiene pasos de reproduccion completos.
- El texto no contiene ambiguedades ni frases vagas.

## Criterios de rechazo

No publicar el issue si falta cualquiera de estos puntos:

- Titulo claro.
- Criterios Given/When/Then.
- Prioridad.
- Estimacion.
- Pasos de reproduccion en bugs.
