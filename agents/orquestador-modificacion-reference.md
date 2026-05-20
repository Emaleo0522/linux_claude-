---
name: orquestador-modificacion-reference
description: Mini-pipeline completo para Modo Modificación (proyectos ya completados). AUDIT HERENCIA + 4 pasos + UI Audit Checklist 5 dimensiones + DAG State. Cargado por el orquestador SOLO cuando Boot Sequence detecta fase_actual=completado y el brief modifica. Extraído de orquestador.md el 2026-05-19 para reducir boot tokens en proyectos nuevos.
---

# Modo Modificación — Mini-pipeline completo

> **Cuándo cargar este archivo**: el orquestador lo lee SOLO cuando se cumplen ambas condiciones:
> 1. Boot Sequence detectó `mem_search("{proyecto}/estado")` con `fase_actual: "completado"` o `fase_actual: 5`
> 2. El brief del usuario incluye verbos de modificación: "agrega X a {proyecto}", "quita Y", "modifica Z", "mejorá", "actualizá", "redesign", "fix"
>
> Si ambas condiciones NO se cumplen → proyecto nuevo, ignorar este archivo y arrancar Fase 1.

---

## Detección (recordatorio — lo hace el Boot Sequence)

El orquestador detecta modo modificación si:
- Existe `{proyecto}/estado` en Engram con `fase_actual: "completado"` o `fase_actual: 5`
- El usuario referencia un proyecto existente + pide cambios específicos
- El usuario dice "agrega X a [proyecto]", "quita Y", "modifica Z"

## Mini-pipeline (4 pasos)

```
0. AUDIT HERENCIA (NUEVO — obligatorio antes de tocar código) — El orquestador detecta
   defaults heredados que violan reglas vigentes de la arquitectura ANTES de modificar nada.
   - Identificar archivos CSS/HTML/JSX clave del proyecto (heurística: globals.css,
     styles.css, layout.tsx, index.html, tailwind.config).
   - Ejecutar `bash ~/.claude/hooks/pre-return-audit.sh --files="<archivos>"` sobre ellos.
   - El hook devuelve YAML con WARN/FAIL por regla universal (container ≤1280 = SaaS feel,
     fuentes declaradas sin <link>, anchor scroll sin scroll-padding, navbar mobile sin
     hamburger, prefers-reduced-motion ausente cuando hay >5 animaciones).
   - Si hay FAIL/WARN → reportar al usuario con formato:
     "Antes de modificar, detecté N violaciones heredadas: [lista]. ¿Las fixeo dentro del
      scope, las dejo para otra iteración, o las ignoramos explícitamente?"
   - Esperar decisión. NO avanzar al Paso 1 sin OK del usuario.
   - Razón: evita el "drag pattern" — arrastrar defaults heredados sin auditarlos. Ver
     `webcodexatlas/audit-2026-05-14` en Engram (caso paradigmático: --max:1180 arrastrado).

1. ANÁLISIS — El orquestador (no un subagente) evalúa:
   - ¿Qué cajones de Engram existen para este proyecto?
   - ¿El cambio requiere nueva arquitectura (nueva DB table, nuevo servicio) o solo UI/lógica?
   - ¿Afecta design system, seguridad, o solo implementación?

2. PLANIFICACIÓN LIGERA — Generar tareas inline (sin PM):
   - Si son ≤3 tareas simples: el orquestador las define directamente
   - Si son >3 tareas o requieren análisis de scope: delegar a project-manager-senior con contexto del proyecto existente
   - Actualizar `{proyecto}/tareas` en Engram (append, no sobrescribir)
   - Numerar tareas continuando desde la última (ej: si había 12 tareas, las nuevas son 13, 14...)

3. EJECUCIÓN — Mini Fase 3 + QA:
   - Mismo loop dev→QA que Fase 3 normal
   - Usa los cajones de Engram existentes (css-foundation, design-system, security-spec)
   - Si el cambio requiere actualizar arquitectura:
     a) Cambio de UI/design → re-delegar a ui-designer para actualizar design-system
     b) Nuevo endpoint → backend-architect + actualizar api-spec
     c) Cambio de seguridad → security-engineer para actualizar security-spec
   - NO re-ejecutar Fase 2 completa — solo los agentes afectados
```

## Qué NO se re-ejecuta

- Fase 1 completa (ya existe el proyecto)
- Fase 2 completa (solo agentes afectados por el cambio)
- Fase 2B (assets creativos) — salvo que el usuario pida nuevos assets
- Fase 4 completa — solo re-ejecutar reality-checker si los cambios son sustanciales

## UI Audit Checklist (para cambios visuales/UX)

Cuando el cambio afecta UI o el usuario pide "redesign", "mejorar el diseño", "se ve genérico", "más premium" — el orquestador corre un audit estructurado **antes** de delegar a ui-designer/frontend-developer:

### 1. Spacing audit

- ¿El spacing es coherente con `visual_density` declarado en `{proyecto}/visual-direction`? Si dice density ≤3 pero hay `py-4` en heros → FIX
- ¿Hay stacks verticales con gap inconsistente (mezcla `space-y-2`, `gap-4`, `mt-8`)? → unificar en token
- ¿Los componentes respetan la escala de spacing del design-system o hay valores mágicos?

### 2. Typography hierarchy audit

- ¿Hay más de 4 font-sizes en uso? (indica jerarquía rota)
- ¿El heading font y body font del preset/brand.json se aplican consistentemente o hay Inter por defecto en todos lados?
- ¿`line-height` de párrafos largos es 1.5-1.75? (legibilidad)
- ¿Hay headings sin `tracking` ajustado (display fonts necesitan letter-spacing negativo)?

### 3. Motion coherence audit

- ¿El `motion_intensity` del proyecto coincide con lo implementado? Si dice 2 pero hay GSAP ScrollTrigger → cortar o escalar abajo
- ¿Existe `@media (prefers-reduced-motion: reduce)` con fallbacks? (obligatorio si motion ≥ 4)
- ¿Las curvas de easing son coherentes (todas `cubic-bezier` similares o todo linear)?
- ¿Hay animaciones en elementos sin propósito (divs decorativos animados)?

### 4. Color coherence audit

- ¿Los colores usados existen en brand.json o son hex mágicos en el código?
- ¿Contraste WCAG AA mínimo (4.5:1 texto normal, 3:1 grande) en todos los pares fondo/texto?
- ¿Los colores del preset/design-system se respetan o hay drift (ej: 5 tonos de gris distintos)?

### 5. Layout variance audit

- ¿El `design_variance` coincide con lo implementado? Si dice 2 pero hay rotated elements → FIX
- ¿Todas las secciones son `py-20 max-w-7xl mx-auto` clones o hay variación intencional?
- Anti-pattern: "cada sección es un div centrado" cuando el preset pide variance ≥ 5

### Flujo del checklist

1. Orquestador corre el checklist contra el proyecto (lee Engram + scan de archivos clave)
2. Genera `{proyecto}/ui-audit-{timestamp}` en Engram con findings (PASS/FAIL por dimensión)
3. Si FAIL en ≥2 dimensiones → delegar a ui-designer para actualizar design-system, luego frontend-developer para aplicar
4. Si FAIL en 1 dimensión → delegar directo a frontend-developer con el finding concreto
5. QA vía evidence-collector valida que el fix cerró el finding

## Cuándo escalar a pipeline completo

Si el cambio es tan grande que equivale a rehacer el proyecto (>50% de tareas nuevas, cambio de stack, nueva DB):
- Informar al usuario: "Este cambio es tan sustancial que recomiendo tratarlo como un proyecto nuevo. ¿Continuamos con el pipeline completo?"
- Si acepta → pipeline normal de 5 fases

## DAG State en modo modificación

- `fase_actual: "modificacion"`
- `modificacion_tareas: [13, 14, 15]` (IDs de las nuevas tareas)
- `modificacion_origen: "completado"` (fase desde la que se inició la modificación)
- Al completar → volver a `fase_actual: "completado"`
