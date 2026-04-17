# Sistema Vibecoding Híbrido

## Dos modos de trabajo

Claude opera en dos modos distintos. El usuario elige explícitamente cuál usar:

| Modo | Cuándo usarlo | Cómo activarlo |
|------|--------------|----------------|
| **Claude normal** | Preguntas, fixes puntuales, revisiones, chat técnico | Por defecto — simplemente habla |
| **Orquestador** | Proyectos completos de software de principio a fin | Di explícitamente: *"activa el pipeline"*, *"modo orquestador"*, o *"nuevo proyecto completo: X"* |

Cuando se activa el modo orquestador, Claude adopta el comportamiento definido en `~/.claude/agents/orquestador.md` — pipeline de 5 fases, delegación a subagentes, sin hacer trabajo real inline.

## Arquitectura

Este sistema usa un **orquestador central** (1 coordinador + 24 subagentes = 25 entidades). Los subagentes solo responden al orquestador, nunca entre sí.

### Pipeline (5 fases)
```
Fase 1  Planificación      → project-manager-senior
Fase 2  Arquitectura       → ux-architect (parametric CSS) → ui-designer (behavioral specs) + security-engineer (paralelo)
  └─ Paso 1.5: Visual Direction Checkpoint — pausa para consultar al usuario sobre decisiones visuales clave
Fase 2B Assets visuales    → brand-agent → (pausa aprobación) → logo-agent + image-agent (paralelo) → video-agent
Fase 3  Dev ↔ QA Loop     → dev-agents (aplican design decision tree) ↔ evidence-collector (3 reintentos)
Fase 4  Certificación      → seo-discovery + api-tester + performance-benchmarker + reality-checker
Fase 5  Publicación        → git (confirmación) → deployer (confirmación)

Modo Modificación → análisis → planificación ligera → mini Fase 3+QA (para proyectos ya completados)
```

### Visual Direction Checkpoint (Fase 2, Paso 1.5)
Pausa entre ux-architect y ui-designer donde el usuario elige estilo visual, hero, navegación, galería, nivel de animación, mood y efectos especiales. Detalles en `pipeline-reference.md`.

### Model routing (Opus / Sonnet)

| Modelo | Agentes | Criterio |
|--------|---------|----------|
| **Opus** | orquestador, project-manager-senior, security-engineer, game-designer, reality-checker | Decisiones arquitectonicas complejas, planificacion, threat modeling, certificacion final |
| **Sonnet** | Todos los demas (20 agentes) | Ejecucion de tareas definidas, QA, utilidades, creativos |

Cada agente tiene `model:` en su frontmatter YAML. El orquestador lo respeta al hacer spawn.

### Regla de oro
El orquestador **NUNCA** hace trabajo real (no lee código, no escribe código, no analiza arquitectura). Solo coordina. Cada token inline es contexto perdido.

## Gestión de contexto

### Reglas de protección de contexto
- **Handoffs mínimos**: subagentes devuelven solo STATUS + archivos + issues. Nunca código completo.
- **Screenshots a disco**: QA guarda en `/tmp/qa/` y pasa solo rutas, nunca imágenes inline.
- **No duplicar en contexto**: si la info está en Engram, pasar solo el topic_key, no el contenido.

### Engram (memoria persistente)
- **Lectura siempre en 2 pasos**: `mem_search` → `mem_get_observation` (nunca usar preview truncada)
- **Escritura siempre con topic_key**: evita duplicados en reintentos
- **Actualizar, no duplicar**: usar `mem_update(observation_id, nuevo)` si el cajón ya existe
- **Dual-write critico**: `{proyecto}/estado` y `{proyecto}/tareas` se guardan SIEMPRE en Engram + disco (`{project_dir}/.pipeline/`)
- **Proactive saves**: subagentes guardan descubrimientos no obvios con topic key `{proyecto}/discovery-{desc}`

### Lectura Engram — bloque canonico (referencia para todos los agentes)
```
# Leer de Engram (2 pasos OBLIGATORIOS — nunca usar preview truncada)
result = mem_search("{proyecto}/{cajon}")
if result.observation_id:
    full = mem_get_observation(result.observation_id)
    # usar full.content — NUNCA result.preview
else:
    # cajon no existe — informar al orquestador
```

### Perfil personal del usuario
El **orquestador** ejecuta `mem_context(scope="personal")` como **paso 0 del Boot Sequence**. Los hooks NO pueden llamar MCPs. En modo Claude normal, llamar `mem_context(scope="personal")` manualmente al inicio.

### Resiliencia Engram
- **Disk fallback**: si Engram falla → `{project_dir}/.pipeline/{cajon}.md`. Orquestador busca Engram primero, luego disco.
- **Cajones críticos** (estado, tareas, css-foundation, design-system, security-spec, gdd): si no están en Engram ni disco → STATUS fallido con BLOQUEADORES.
- **Retry counter**: el orquestador posee `intento_actual` (no el subagente), persistido en DAG State.

> **Detalles completos** (Boot Sequence, carga progresiva del DAG State, continuidad entre sesiones, topic keys completa, pre-compact snapshot): ver `orquestador.md`

## Hook System (13 hooks, auditados 2026-04-12 — 11/11 HEALTHY)

Hooks interceptan tool calls en tiempo real. Configurados en `~/.claude/settings.json`. Scripts en `~/.claude/hooks/`.

| Hook | Accion |
|------|--------|
| `block-no-verify` | **BLOQUEA** git --no-verify, git push --force, rm -rf, git reset --hard, DROP TABLE, chmod 777, curl\|sh |
| `config-protection` | **BLOQUEA** secrets (.env, .pem, .key). **ADVIERTE** configs de linting |
| `quality-gate` | **ADVIERTE** debugger, .only(), @ts-ignore, secrets hardcodeados |
| `console-log-warning` | **ADVIERTE** console.log/warn/error en produccion (ignora tests) |
| `suggest-compact` | **ADVIERTE** cada ~50 tool calls (async) |
| `pre-compact-engram` | **GUARDA** snapshot a disco antes de compactar (v2.2) |
| `cost-tracker` | **REGISTRA** tool calls por categoria (async) |
| `session-summary` | **LOGUEA** actividad en JSONL (async) |
| `engram-sync` | **SINCRONIZA** Engram con GitHub al parar sesion (async, 60s) |
| `session-start-context` | **CARGA** contexto de sesion anterior al iniciar |

**Comportamiento**: Exit 2 = BLOCK | Exit 0 + stderr = WARN | Fail-open (nunca rompe el flujo)

**Utilidades manuales**: `node ~/.claude/hooks/audit-system.js` (health check) | `cost-report.js` (uso de tools) | `learning-index.js` (discoveries)

## Herramientas, referencias y protocolo de subagentes
> Tabla completa de tools por agente, referencias tecnicas (12 archivos), MCPs externos, protocolo compartido y coordinacion cross-agent: ver `pipeline-reference.md`

- **Protocolo compartido**: `~/.claude/agents/agent-protocol.md` (Engram 2-pasos, topic_key obligatorio, Return Envelope estandar)
- **Design Intelligence Engine**: `~/.claude/design-data/` (search.js + 8 CSVs, 161 industrias). El motor informa, no decide. Anti-patterns HIGH son obligatorios.

## Reglas clave
- Solo el **orquestador** guarda DAG State en Engram
- Los subagentes guardan sus propios resultados en Engram con topic keys del proyecto
- Solo **evidence-collector** y **reality-checker** hacen QA visual
- Solo **git** hace commits/push — nunca un agente dev
- Solo **deployer** despliega (Vercel para web, EAS Build para mobile)
- git y deployer actúan **solo con confirmación del usuario** — pero si el mensaje original ya incluía "sube", "git", "deploy", "push", "publica" o similar, eso **ya es la confirmación**. No volver a preguntar.
- Si el orquestador devuelve una pregunta de confirmación sobre una acción que el usuario ya autorizó en su mensaje, main Claude debe continuar el agente con `SendMessage` respondiendo la respuesta implícita — no dejar el agente suspendido.
- Cada tarea dev pasa por **evidence-collector** antes de avanzar (máx 3 reintentos)
- **El orquestador NO activa git hasta que evidence-collector retorna PASS** — nunca saltear QA antes de push, aunque el tiempo apremia. Los bugs silenciosos (Mixed Content, fallback invisible) solo se detectan con QA.
- **codepen-explorer solo busca y extrae** — nunca adapta ni construye. Guarda código temporal en `{project_dir}/.codepen-temp/{slug}/`. frontend-developer lee de ahí y adapta al proyecto/brand.
- **Bóveda CodePen** (`~/.claude/codepen-vault/`) — solo guarda efectos aprobados por el usuario. Engram tiene metadata buscable (`codepen-vault/{slug}`), disco tiene el código.
- **Checkpoint post-efectos en Fase 3** — si se usaron efectos de CodePen, mostrar página completa al usuario antes de pasar a Fase 4 para que pueda pedir cambios.

## Stack, Design Systems y Componentes
> Tabla completa del stack adaptable, Nothing Design System, y 21st.dev: ver `pipeline-reference.md`

- **Stack**: el orquestador decide en Fase 1. Defaults: Next.js (apps), Vite+React (landing), Hono (backend), Drizzle (ORM), Zustand (state)
- **Nothing Design**: opcional, solo si el usuario lo pide. Referencia en `nothing-design-reference.md`
- **21st.dev**: componentes community via Context7 MCP. Inspiracion + base, no copy-paste. Adaptar siempre al brand

## Autenticación estándar — Better Auth
- **Better Auth** es el sistema de auth por defecto para todos los proyectos nuevos
- Referencia completa: `~/.claude/agents/better-auth-reference.md`
- Agentes que lo usan: backend-architect (server), frontend-developer (client), rapid-prototyper (full-stack)
- Solo usar Clerk/Supabase Auth/JWT custom si el proyecto ya los tiene implementados

### Reglas críticas (validadas en producción)
- **Migración NO es automática**: siempre agregar `"migrate": "npx @better-auth/cli migrate"` al `package.json` y ejecutarlo antes del primer `npm run dev`
- **Next.js 16+**: usar `proxy.ts` con `export async function proxy()` — el archivo `middleware.ts` está deprecado

### Better Auth + Supabase + Vercel + Next.js 16
- **Referencia completa con código y checklist**: `~/.claude/agents/better-auth-reference.md` § "Better Auth + Supabase + Vercel"
- **Reglas clave**: postgres.js (no pg), Transaction Pooler (puerto 6543), `prepare: false`, dynamic imports en route handler, `toCleanRequest()` para Request limpio, `getSessionCookie` con `cookiePrefix`

## Agentes creativos — Assets visuales
> Detalles completos (orden, gates, env vars, cost tracking): ver `pipeline-reference.md` § "Agentes creativos"

- **Orden**: brand-agent -> (aprobacion) -> logo-agent + image-agent (paralelo) -> video-agent
- **brand-agent SIEMPRE primero** — sin `brand.json` ningun agente creativo funciona
- **NO auto-generar assets sin confirmacion del usuario**
- Env vars: `GEMINI_API_KEY` o `HF_TOKEN` (imagen), `REPLICATE_API_TOKEN` (video)

## Best Practices Cross-Cutting (validadas en producción)

> Las best practices de SEO, performance web, accesibilidad, WebGL safety y Mixed Content ya están integradas en los agentes que las aplican (frontend-developer.md, seo-discovery.md, evidence-collector.md, xr-immersive-developer.md). Esta sección solo contiene patterns que NO están en ningún agente.

### Vercel — Sitios Estáticos
- **`Cache-Control: max-age=0` es el default de Vercel**. Para browser caching, crear `vercel.json` con headers: `max-age=604800` para `/assets/**`, `max-age=3600` para `/js/**` y `/css/**`
- **Security headers via `vercel.json`**: agregar X-Content-Type-Options (nosniff), X-Frame-Options (SAMEORIGIN), Referrer-Policy, Permissions-Policy bajo `"source": "/(.*)"`. Vercel no los agrega por defecto.
- **Admin panel en sitio estático**: `X-Robots-Tag: noindex, nofollow` + `Cache-Control: no-store` para `/admin.html`

### CSS Patterns (validados en producción)
- **`::after` para background images**: pseudo-elemento con `position: absolute; inset: 0; z-index: 0; pointer-events: none`. Hijos con `position: relative; z-index: 1`.
- **`max()` para secciones full-width centradas**: `padding: Xpx max(24px, calc((100vw - 1200px) / 2))` — reemplaza `max-width + margin: auto`.
- **`translateX` en `position: fixed` puede fijar scroll horizontal**: usar `translateY` para animar toasts/modales fuera del viewport.
- **Clases genéricas colisionan entre admin y sitio público**: usar IDs específicos o clases prefijadas para paneles admin.

### Bundle Size Gates
- **bundlewatch** en `package.json`: main < 250KB gzip, vendor < 150KB gzip, páginas < 50KB gzip. Gate en Fase 4.

### QA & Certificación (reglas que NO están en agentes)
- Testear contra **build de producción** (`npm run build && npm start`), no dev server
- SEO Score mínimo 85/100 para certificación
- **Playwright solo corre Chromium** — issues Safari/Webkit NO detectados. Para WebGL, aplicar safety patterns ANTES de Fase 4.

### Referencias externas
- **PocketBase**: `pocketbase-reference.md` | **DevOps VPS**: `devops-vps-reference.md`

## Overrides Windows — Diferencias con Linux/Claude Code

> **SOLO APLICA en Windows/Claude Desktop.** En Linux/Claude Code CLI, ignorar esta seccion completa.

### Servidores de desarrollo (agentes: frontend-developer, backend-architect, rapid-prototyper, xr-immersive-developer)

**NUNCA** arrancar servidores con `npm run dev` via Bash directamente.
**SIEMPRE** usar `preview_start` del Claude Preview MCP.

Pasos obligatorios:
1. Crear o verificar `.claude/launch.json` en el directorio de trabajo con la configuracion del proyecto
2. Llamar `preview_start` con el nombre definido en `launch.json`
3. Usar `preview_logs` para verificar que arranco sin errores
4. Pasar la URL (`http://localhost:{puerto}`) al agente de QA

Formato de `.claude/launch.json` en Windows:
```json
{
  "version": "0.0.1",
  "configurations": [
    {
      "name": "nombre-proyecto",
      "runtimeExecutable": "cmd",
      "runtimeArgs": ["/c", "cd nombre-proyecto && npm run dev"],
      "port": 3000
    }
  ]
}
```

> **Motivo**: En Claude Desktop/Windows, `npm` no esta disponible directamente en el PATH del entorno de herramientas. `cmd /c` resuelve el PATH correctamente.

### Comandos de una sola vez (instalar deps, migrar DB, build)
Estos si se ejecutan via Bash normal:
```bash
cd nombre-proyecto && npm install
cd nombre-proyecto && npm run migrate
cd nombre-proyecto && npm run build
```

### Puertos en Windows
- Matar procesos: `netstat -ano | findstr :PORT` + `taskkill /PID <pid> /F`
- Linux equivalente: `lsof -ti:PORT | xargs kill -9`

### Next.js — Versiones
- Usar **Next.js 15 o 16** (no 14)
- Next.js 16+: `proxy.ts` en raiz del proyecto (no `middleware.ts`)

### Preview verification — proporcionalidad

El hook `stop` dispara `verification_workflow` cuando se edita código con un preview server activo. Aplicar con criterio según el tipo de cambio:

| Tipo de cambio | Verificación requerida |
|----------------|----------------------|
| Layout, UI, estilos, lógica nueva | Workflow completo: snapshot → navigate → screenshot |
| Texto/copy en estado visible (hero, nav, botones) | `preview_eval` único para confirmar el texto nuevo existe |
| Typo en empty state / texto condicional | `preview_eval` único: `document.body.innerText.includes("texto_correcto")` — si retorna `true`, PASS sin navegación ni snapshot |
| Cambio en archivo no-UI (config, tipos, API routes) | Saltar verificación completamente |

**Regla clave**: un typo fix en un string estático NO requiere navegar, hacer snapshot ni tomar screenshot. Un solo `preview_eval` de búsqueda de texto es suficiente y correcto.

## Herramientas de diseno
- **Figma/FigJam**: Solo usar cuando el usuario comparte una URL de Figma o lo pide explicitamente
