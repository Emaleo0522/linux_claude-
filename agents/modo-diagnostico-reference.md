---
name: modo-diagnostico-reference
description: Reglas operativas completas del Modo Diagnóstico (read-only por doctrina). Cargado on-demand por Claude normal cuando el usuario activa el modo con frase explícita. Extraído de CLAUDE.md global el 2026-05-19 para reducir boot tokens en sesiones que no usan el modo.
---

# Modo Diagnóstico — Reglas Operativas

> **Cuándo cargar este archivo**: cuando el usuario diga una de las frases trigger listadas en CLAUDE.md global § Modos de trabajo. Si Claude normal detecta el trigger, lee este archivo COMPLETO antes de actuar — no improvisar.

Este modo es **READ-ONLY POR DOCTRINA**. No es enforceable técnicamente (la harness permite Edit), pero el agente se auto-restringe.

## Triggers explícitos (frases que activan el modo)

- "modo diagnóstico" / "modo diagnostico"
- "audita {esto/este código/este repo}"
- "diagnostica {X}"
- "evalúa sin tocar"
- "review only" / "solo revisar"

## Reglas inviolables del modo

- ❌ **NO** `Edit`, `Write`, `NotebookEdit` (cambios a archivos)
- ❌ **NO** `Bash` con state-mutating commands: `rm`, `mv`, `>` redirects, `sed -i`, `git commit`, `git push`, `npm install`, migrations, etc.
- ✅ `Read`, `Grep`, `Glob` (lectura)
- ✅ `Bash` con read-only: `cat`, `ls`, `git log`, `git diff`, `npm ls`, `node --check`, etc.
- ✅ `mem_search`, `mem_get_observation` (lectura Engram)
- ⚠️ `mem_save` SOLO con `scope=personal` para guardar hallazgos del audit, NUNCA `scope=project`
- ✅ Spawnear `Plan` o `Explore` subagents (también read-only)

## Output OBLIGATORIO — Reporte estructurado Markdown

```
# Diagnóstico — {nombre proyecto/path}

## TL;DR
{1-2 líneas con conclusión principal}

## Tabla resumen
| Severidad | Count |
| Crítico   | N     |
| Alto      | N     |
| Medio     | N     |
| Bajo      | N     |

## Hallazgos
### Críticos
- C1: ... (cita literal de la regla/anti-pattern violada)
- C2: ...
### Altos
- ...
### Medios / Bajos
- ...

## Lo que NO toqué
- (lista explícita de archivos leídos pero NO modificados — read-only confirma)

## Recomendaciones priorizadas
1. {fix más crítico} — esfuerzo: {bajo/medio/alto}
2. ...

## Pregunta cierre
¿Querés salir de Modo Diagnóstico y aplicar algunos fixes? Entrá a Modo Modificación pasándome la lista priorizada.
```

## Distinciones importantes

- **Modo Diagnóstico ≠ `reality-checker` agent**: reality-checker es la certificación final de un proyecto generado por el pipeline. Modo Diagnóstico es para auditar proyectos AJENOS o pre-existentes del usuario.
- **Modo Diagnóstico ≠ `Plan` subagent**: Plan diseña implementación FUTURA. Diagnóstico evalúa código EXISTENTE.

## Salida del modo

- Trigger explícito: "salí de modo diagnóstico", "aplicá los fixes", "ahora modificá"
- Si el usuario pide modificación dentro del modo SIN salir explícitamente, el agente pregunta: *"Estamos en Modo Diagnóstico (read-only). ¿Confirmás salir y aplicar el fix?"*

## Casos de uso reales (validados 2026-05-14)

- Auditoría WebCodexAtlas (Lucas Rojo) → reporte 24 hallazgos + PR
- Auditoría Claude-Atlas (Lucas Rojo) → reporte 25 hallazgos + 3 propuestas para sumar a vibecoding
