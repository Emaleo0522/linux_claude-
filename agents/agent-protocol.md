---
name: agent-protocol
description: Protocolo compartido para TODOS los subagentes del sistema vibecoding. Engram, Return Envelope, reglas universales.
model: sonnet
---

# Protocolo de Subagentes — Referencia Compartida

Este archivo define los patrones que TODO subagente debe seguir. No dupliques este contenido en tu archivo — referéncialo.

---

## 1. Engram — Lectura (2 pasos OBLIGATORIOS)

NUNCA uses el preview de `mem_search` como dato final. Siempre completa los 2 pasos:

```
Paso 1: resultado = mem_search("{proyecto}/{cajon}")
        → retorna: preview TRUNCADO + observation_id

Paso 2: completo = mem_get_observation(observation_id)
        → retorna: contenido COMPLETO

Usar SOLO completo.content — NUNCA resultado.preview
```

Si `mem_search` no retorna observation_id → el cajón no existe. Manejo universal:

1. **Cajón critico** (inputs que necesitas para trabajar: `estado`, `tareas`, `css-foundation`, `design-system`, `security-spec`, `gdd`):
   - Buscar fallback en disco: `{project_dir}/.pipeline/{cajon}.md`
   - Si existe en disco: usar contenido del archivo y continuar
   - Si NO existe en disco: informar en Return Envelope `STATUS: fallido` con `BLOQUEADORES: [{cajon} no encontrado en Engram ni disco]`
   - NUNCA inventar datos ni usar defaults silenciosos para cajones criticos

2. **Cajón importante (re-delegable)** (`api-spec`):
   - Informar al orquestador que el cajón no existe — el orquestador re-delegará al agente productor (ej: backend-architect para api-spec)
   - NO continuar con defaults silenciosos para estos cajones; el orquestador decide si re-delegar o proceder sin él
   - Informar en NOTAS: "Cajón {cajon} no encontrado, requiere re-delegación"

3. **Cajón opcional** (`branding`, `discovery-*`):
   - Continuar con defaults razonables o sin esa información
   - Informar en NOTAS: "Cajón {cajon} no encontrado, usando defaults"

4. **Cajón de QA** (`qa-{N}`):
   - Marcar como "no validada" — no asumir PASS ni FAIL

---

## 2. Engram — Escritura (SIEMPRE con topic_key)

### Primera vez (crear observación):
```
mem_save(
  title: "{proyecto} — {descripción corta}",
  content: "{contenido estructurado}",
  type: "architecture",  // o decision, bugfix, pattern, discovery
  topic_key: "{proyecto}/{mi-cajon}",
  project: "{proyecto}"
)
```

### Actualizar observación existente:
```
Paso 1: mem_search("{proyecto}/{mi-cajon}") → obtener observation_id
Paso 2: mem_get_observation(observation_id) → leer contenido COMPLETO actual
Paso 3: Merge tu contenido nuevo con el existente (no sobrescribir ciegamente)
Paso 4: mem_update(observation_id, contenido_mergeado)
```

**REGLA**: `topic_key` es OBLIGATORIO en todo `mem_save`. Sin él, los reintentos crean duplicados.

### Manejo de error `ambiguous_project` (Engram v1.15.9+)

Si `mem_save({proyecto}/...)` retorna error con código `ambiguous_project` o mensaje `Project %q is not backed by known context`:

1. **NO retry inmediato con mismo payload** — fallaría idéntico

2. **Diagnóstico — ¿el proyecto existe en el DB o no?**:
   - Si `engram projects list` LO contiene → proyecto existe, problema es cwd ambiguity → **Path A (recovery_token)**
   - Si `engram projects list` NO lo contiene → proyecto nuevo → **Path B (CLI bootstrap)**

3. **Path A — recovery_token (proyecto existe pero MCP no lo resuelve)**:
   El error trae `recovery_token` y `available_projects` en el envelope. Reintentar UNA vez:
   ```
   mem_save(
     title: "...",
     content: "...",
     type: "...",
     topic_key: "{proyecto}/...",
     project: "{proyecto}",
     project_choice_reason: "user_selected_after_ambiguous_project",
     recovery_token: "{token-recibido-en-error}"
   )
   ```
   Requiere que `{proyecto}` esté en `available_projects` del error (cwd-scoped). Si no está → no es path A, ir a path B.

4. **Path B — CLI bootstrap (proyecto nuevo, no existe en DB)**:
   Cuando `available_projects` NO contiene `{proyecto}` y `engram projects list` tampoco:
   ```bash
   engram save "bootstrap" "first save under project={proyecto}" \
     --project {proyecto} --scope personal --type discovery
   ```
   El CLI crea el proyecto en el DB al vuelo. El MCP no puede (validación estricta).

   Después del bootstrap, `mem_save` y `mem_search` desde MCP con `project="{proyecto}"` explícito funcionan, aunque `available_projects` siga sin listarlo (esa lista es cwd-scoped, no el full DB).

5. **Para cross-PC sync** del nuevo proyecto: agregar `{proyecto}` a `ENGRAM_CLOUD_ALLOWED_PROJECTS` en `/opt/engram-cloud/.env` del server cloud (SSH). Sin esto, los saves quedan locales en cada PC sin replicar.

6. **Si ambos paths fallan** → Return Envelope con `BLOQUEADORES: project '{proyecto}' no enrolled — orquestador debe correr CLI bootstrap antes de re-delegar`

**Validado 2026-05-16** con `vibefx` (no en whitelist, no en cwd-scan): SSH whitelist + CLI bootstrap = full operability en una sesión.

### Fallback a disco (si Engram no responde)

Si `mem_save` o `mem_update` falla (timeout, MCP no disponible, error):

1. Escribir el contenido a `{project_dir}/.pipeline/{cajon}.md` (crear directorio si no existe)
2. Continuar la tarea normalmente — no bloquearse por fallo de Engram
3. Informar en el Return Envelope: `NOTAS: Engram write failed, fallback to disk: .pipeline/{cajon}.md`

Al retomar un proyecto, el orquestador busca primero en Engram. Si no encuentra, busca en `.pipeline/`.

**NOTA**: Este fallback es un patrón que cada agente implementa individualmente (los agentes son prompts, no código — no hay forma de compartir un módulo). El patrón es simple: try mem_save → catch → fs.writeFile. No crear una utilidad compartida por esto.

---

## 3. Return Envelope — Formato estándar

Todo subagente retorna al orquestador con este formato EXACTO:

```
STATUS: completado | fallido | PASS | FAIL | CERTIFIED | NEEDS WORK
TAREA: {descripción corta de lo que se hizo}
ARCHIVOS: [lista de paths creados/modificados]
ENGRAM: {proyecto}/{mi-cajon} (topic_key usado)
SERVIDOR: puerto {N} (solo si levantaste servidor)
VERIFICACION: typo | layout | config | none
VISUAL_IMPACT: high | medium | low | none   ← obligatorio en agentes que tocan UI/CSS
BLOQUEADORES: [lista] (solo si hay impedimentos para continuar)
NOTAS: {texto libre, máx 3 líneas}
```

- **STATUS** es el primer campo, siempre
- **ARCHIVOS** lista paths SIEMPRE relativos al proyecto (ej: `src/app/page.tsx`, NO `/home/user/project/src/app/page.tsx`)
- **ENGRAM** indica el cajón donde guardaste tu resultado
- **VERIFICACION** indica qué nivel de verificación requiere el cambio (ver tabla abajo)
- **VISUAL_IMPACT** dispara checkpoint humano (ver tabla abajo). Obligatorio en frontend-developer, ui-designer, brand-agent, image-agent, logo-agent, xr-immersive-developer. Opcional pero recomendado en cualquier agente que toque archivos `.css|.html|.tsx|.jsx|.vue|.svelte`.
- Omitir campos vacíos (no poner "SERVIDOR: N/A")

### Tabla de valores para VERIFICACION

| Valor | Cuándo usarlo | Acción del orquestador |
|-------|--------------|----------------------|
| `layout` | Cambios de UI, estilos, componentes, lógica nueva | Workflow completo: snapshot → navigate → screenshot |
| `typo` | Corrección de texto/copy en string estático, empty state, texto condicional | Un solo `preview_eval`: `document.body.innerText.includes("texto_nuevo")` → si `true`, PASS |
| `config` | Cambios en archivos no-UI: configs, tipos, API routes, env vars | Saltar verificación completamente |
| `none` | Sin servidor de preview activo, o cambio no observable en browser | Saltar verificación completamente |

### Tabla de valores para VISUAL_IMPACT (dispara checkpoint humano)

| Valor | Cuándo usarlo | Acción del orquestador |
|-------|--------------|----------------------|
| `high` | Hero/landing redesign, identidad visual nueva, animaciones principales, layout estructural mayor, decisión visual interpretable (multi-opción válida) | **OBLIGATORIO**: mostrar screenshot/preview al usuario con recomendación antes de marcar tarea completa. Ver § "Checkpoint humano" en `~/.claude/CLAUDE.md` |
| `medium` | Sección secundaria nueva, componentes visibles, ajustes de tipografía/color en zonas no críticas | Opcional: mostrar al usuario si fue la segunda iteración del mismo elemento |
| `low` | Microajustes (spacing, focus rings, dark mode tweaks, sombras secundarias) | No checkpoint. Solo mencionar en NOTAS si vale la pena |
| `none` | Sin impacto visual (config, types, lógica interna, refactor de selectores sin cambio visible) | Saltar checkpoint |

**Regla clave**: si tuviste **2+ iteraciones sobre el mismo elemento** en la misma sesión, escalar a `high` aunque inicialmente parezca `medium` — es señal de local minimum y necesita ojo humano.

**Agentes utilitarios** (codepen-explorer) pueden usar STATUS operacionales adicionales:
`OK | SAVED | FOUND | NOT_FOUND | BLOCKED` — siempre dentro del mismo formato de envelope.

---

## 4. Proactive Saves (descubrimientos)

Si durante tu trabajo descubres algo no obvio (gotcha, incompatibilidad, patrón útil), guárdalo inmediatamente:

```
mem_save(
  title: "{proyecto} — {descubrimiento corto}",
  content: "**What**: {qué descubriste}\n**Why**: {por qué importa}\n**Where**: {archivos afectados}",
  type: "discovery",
  topic_key: "{proyecto}/discovery-{slug-descriptivo}",
  project: "{proyecto}"
)
```

No esperes al final de la tarea. Guarda al momento.

**NOTA**: Los discoveries se guardan para búsqueda futura via `mem_search`. No hay un agente agregador — el orquestador o el usuario pueden buscar discoveries con `mem_search("{proyecto}/discovery")` cuando necesiten contexto. También accesibles via `node ~/.claude/hooks/learning-index.js --search=keyword`.

---

## 5. Reglas universales (todos los subagentes)

1. **No arrancar servidores con Bash** → usar `preview_start` (solo aplica en Windows/Claude Desktop; en Linux/Claude Code CLI, usar Bash normalmente)
2. **No hacer git commit/push** → solo el agente `git` hace esto
3. **No deployar** → solo el agente `deployer` hace esto
4. **No usar imágenes de placeholder** (picsum.photos, lorem picsum, etc.) → usar assets reales del proyecto o generar con agentes creativos
5. **Asumir que no hay proceso corriendo en el puerto** → verificar/matar antes de levantar servidor
6. **Resúmenes cortos al orquestador** → nunca código completo, nunca archivos enteros
7. **No duplicar lo que ya está en Engram** → pasar topic_key, no contenido

---

## 6. Límites universales (lo que NINGÚN subagente hace)

- No tomar decisiones de arquitectura que no te correspondan
- No modificar archivos fuera del scope de tu tarea
- No instalar dependencias no solicitadas
- No leer cajones de Engram que no necesitas (lee solo los listados en tu sección "Inputs")
- No crear archivos de documentación (README, CHANGELOG) salvo que la tarea lo pida
