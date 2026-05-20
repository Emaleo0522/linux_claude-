---
name: cross-claude-mailbox-reference
description: Protocolo asíncrono para comunicación cross-PC entre instancias de Claude vía Engram cloud. OPT-IN — solo se carga cuando el usuario activa explícitamente el mailbox check. Extraído de CLAUDE.md global el 2026-05-19 para reducir boot tokens en sesiones sin coordinación cross-PC.
---

# Cross-Claude Mailbox Protocol (2026-05-18)

> **Cuándo cargar este archivo**: cuando el usuario active el mailbox con frase explícita o inicie un workflow conocido cross-PC. Sin activación, NO ejecutar searches por default — el opt-in evita ~3-5K tokens diarios en checks vacíos.

Convención asíncrona para que dos instancias de Claude (ej. `pc004` Linux + `casa` Windows) se comuniquen vía engram cloud **sin requerir relay manual del usuario**. Reusa la infraestructura existente — no es un canal nuevo, solo convención sobre engram.

## Bucket dedicado

`cross-claude-mailbox` (en cloud whitelist).

## Convención de topic keys

- `mailbox/from-{pc-origen}/to-{pc-destino}/{YYYYMMDD-HHMMSS}-{slug}` → query
- `mailbox/from-{pc-origen}/to-{pc-destino}/{YYYYMMDD-HHMMSS}-{slug}-reply` → respuesta
- Notación de pc: `pc004` (Linux), `casa` (Windows). Ajustar si hay más instancias.

## Flujo (OPT-IN — NO ejecutar por default cada turn)

1. **Cuando el usuario lo activa explícitamente** con frases como *"chequeá el mailbox"*, *"¿hay mensajes de pc004?"*, *"revisá comunicaciones cross-PC"*, o cuando inicia un workflow conocido cross-PC (sync de cambios, ronda M2/M3, coordinación de pushes), ejecutar 1 search barato:
   ```
   pending = mem_search(query="to-{mi-pc}", project="cross-claude-mailbox", scope="personal", limit=5)
   ```
   **NO ejecutar este search por default en cada turn**: costaría ~50-100 tokens × ~50 turns/día = ~3-5k tokens diarios solo en checks de mailbox vacíos. El opt-in elimina ese overhead cuando no se está coordinando cross-PC. Cuando hay un workflow cross-PC activo, el usuario lo señaliza y ahí sí se chequea.
2. Si hay queries pendientes sin `*-reply` asociado → procesar antes de responder al usuario.
3. **Para CHECKS** (lecturas, greps, `engram doctor`, `mem_search`, `git status`, etc.) → ejecutar y guardar `*-reply` directamente.
4. **Para EDITS** (`Edit`, `Write`, `Bash` mutating, `SSH`, push, deploy) → **NO auto-aplicar**. Guardar `*-reply` con `requires_user_approval: true` y avisar al usuario en el turn actual.

## Schema de query

```yaml
title: "[mailbox] {pregunta corta}"
type: question
scope: personal
project: cross-claude-mailbox
topic_key: mailbox/from-{pc-origen}/to-{pc-destino}/{ts}-{slug}
content:
  from: {pc-origen}
  to: {pc-destino}
  query: "{pregunta concreta}"
  requires_edit: false  # true si la respuesta involucra edits
  requires_user_approval: false  # auto-true si requires_edit=true
```

## Schema de reply

```yaml
title: "[mailbox-reply] {tema}"
type: discovery
scope: personal
project: cross-claude-mailbox
topic_key: mailbox/from-{pc-respondiendo}/to-{pc-original}/{ts}-{slug}-reply
content:
  in_reply_to_topic_key: {topic_key de la query}
  result: "{respuesta concreta + outputs}"
  edits_required: []  # lista de archivos si aplica
  requires_user_approval: true|false
```

## Anti-patrones

- ❌ Auto-aplicar edits sugeridos por el otro Claude sin confirmación del usuario.
- ❌ Spammear el mailbox con queries triviales (cada mensaje cuesta engram storage).
- ❌ No identificarse en `from:` (ambigüedad cross-PC).
- ❌ Asumir que el reply va a llegar inmediato — el otro Claude solo responde cuando el usuario lo despierta en su PC.

## Limitación honesta

NO es realtime. El Claude destinatario solo "responde" cuando vos le escribís en su PC y dispara su mailbox check. Los mensajes persisten, no se pierden. Si necesitás realtime, escalar a MCP bridge custom (deferred).
