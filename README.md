# Claude Vibecoding System

**An autonomous multi-agent system for building complete software projects from idea to deployment.**

A central orchestrator coordinates 24 specialized AI sub-agents (25 entities total) through a 5-phase pipeline: planning, architecture, development with visual QA, certification, and deployment. 13 reactive hooks enforce security, quality gates, and cost tracking in real time. Persistent memory via Engram MCP enables session continuity and cross-agent coordination.

Compatible with **Linux (Claude Code CLI)** and **Windows (Claude Desktop)**. The system operates in **Spanish** (commands, prompts, and agent communication), though it builds projects in any language.

---

## What Can You Build

| Project Type | Example | Agents Used |
|-------------|---------|-------------|
| **Landing pages & portfolios** | Restaurant website, photographer portfolio, product launch page | frontend-developer, brand-agent, image-agent |
| **Web applications** | Dashboard, SaaS MVP, admin panel, e-commerce | frontend-developer + backend-architect |
| **Mobile apps** | iOS/Android app with Expo | mobile-developer |
| **Browser games** | 2D platformer, puzzle game, arcade | game-designer + xr-immersive-developer |
| **APIs & backends** | REST/tRPC API, webhook handler, background jobs | backend-architect |
| **Full-stack projects** | App with auth, database, API, and frontend | All dev agents as needed |

Every project gets the full pipeline: planned tasks, designed architecture, implemented code with visual QA per task, SEO + performance certification, and deployment to Vercel (web) or EAS Build (mobile).

---

## Key Features

- **25 specialized agents** -- 1 orchestrator + 24 sub-agents, each with defined tools and responsibilities
- **13 technical references** -- shared protocol, auth, animation, design systems, creative coding, pipeline details, and more
- **5-phase pipeline** -- Planning, Architecture, Dev+QA loop, Certification, Deployment
- **13 reactive hooks** -- Security blocks, quality gates, cost tracking, context management
- **Persistent memory** -- Engram MCP for cross-session state, DAG-based progress tracking
- **Visual agent office** -- Pixel Bridge (optional pixel art visualization of agent activity)
- **Adaptive stack** -- Next.js, React Native, Phaser.js, Hono, Drizzle, and more, chosen per project
- **Creative pipeline** -- AI-generated brand identity, logos, images, and video with fallback chains

---

## Pipeline

```
Phase 1: Planning        -> Step 0: Intent Clarifier (mandatory for new projects)
                          -> project-manager-senior
Phase 2: Architecture    -> ux-architect -> (Visual Direction Checkpoint) -> ui-designer + security-engineer
Phase 2B: Visual Assets  -> brand-agent -> (user approval) -> logo + image -> video
Phase 3: Dev <-> QA Loop -> dev-agents <-> evidence-collector (max 3 retries)
Phase 4: Certification   -> seo + api-tester + performance + reality-checker
Phase 5: Deployment      -> git -> deployer (with user confirmation)
```

### Intent Clarifier (Phase 1, Step 0 — NEW 2026-04-19)

Before planning, the orchestrator evaluates if the user brief is clear or vague using a clarity score heuristic (word count + design vocabulary + references + concrete features + audience mentioned). For vague briefs, it asks 6 multiple-choice questions with options:

- **Q1 Project type**: landing / website / webapp / mobile / API / game
- **Q2 Industry**: top 5 matches from `search.js` (161 indexed industries) + "other"
- **Q3 Visual vibe** (MANDATORY): editorial premium / swiss minimal / soft luxury / neo-brutalism / immersive cinematic / playful illustrated / Y2K revival / monochrome industrial
- **Q4 Visual reference** (optional): Figma URL / image path / "like {site}" / brand name / none
- **Q5 Originality** (MANDATORY): conservative / balanced / experimental — calibrates design variance + motion intensity dials
- **Q6 Audience**: B2B / B2C / creatives / Gen Z / luxury / other

**No bypass**: the orchestrator refuses "you decide" — at minimum Q3 + Q5 must be answered explicitly. This prevents the pipeline from defaulting to generic "SaaS teal + Inter" outputs when the user doesn't have design vocabulary. Result stored in Engram as `{project}/intent` with `mood_preset`, `dials_suggested`, `anti_patterns_HIGH` inherited from `style-presets.csv` row.

### Anti-Generic Guardrails (NEW 2026-04-19)

Executable guardrails prevent generic "SaaS template" outputs:

- **brand.json schema v2**: `mood_vector` (8 quantitative dimensions 0-10), `reference_ids`, `anti_patterns_HIGH` as executable blocklist, `typography_pair` with rationale
- **ui-designer Step 0e — SaaS Teal Default Detector**: 6 rules T1-T6 that BLOCK before returning:
  - T1 No teal/cyan primary (HSL hue 175-205, sat>40) except swiss-minimal mood
  - T2 No Inter/Roboto/Open Sans/Lato/Arial/SF Pro/Segoe UI as heading
  - T3 Typographic contrast mandatory (heading.family ≠ body.family) except swiss-minimal
  - T4 No generic hero structure (centered + 2 CTAs + 3 feature cards) outside swiss/dashboard moods
  - T5 Border radius coherent with mood (brutalism=0-2px, luxury=8-16px warm, etc.)
  - T6 Shadow coherent with mood (brutalism=offset-hard, luxury=subtle-warm, y2k=chrome)
- **frontend-developer Pre-return Audit**: 5 grep commands on generated code:
  - No hardcoded `text-teal-/bg-teal-/cyan-*` in non-dashboard files
  - No `font-family: Inter/Roboto/...` as heading in hero/landing
  - Hero has `<img>/<video>/<Image>` when `visual-direction.hero ≠ text-only`
  - Shadow coherent with mood (brutalism requires offset-hard)
  - Motion tier matches `motion_intensity` dial (≤3 = CSS only, 4-6 = Framer, ≥7 = GSAP)

Both agents return `AUTO_AUDIT` in Return Envelope so reality-checker can verify upstream.

### QA Hardening — 9 layers of defense against false positives (NEW 2026-04-19)

Previous audit revealed the QA could approve projects with broken auth + generic design (case VetConnect). Now:

1. **evidence-collector Step 4b**: Verifies upstream AUTO_AUDIT from ui-designer + frontend-developer PASS before screenshots
2. **evidence-collector Step 4c — Visual Fidelity**: LLM-as-judge compares screenshot vs `visual-direction.reference_for_qa` on 5 dimensions (palette, typography, composition, mood, density). Threshold ≥7/10 for PASS. Mood Vector divergence L1 ≤10. Anti-derivative guardrail.
3. **evidence-collector Step 4d — E2E flows**: Mandatory user journeys for auth/CRUD/forms tasks (signup → email verify → login → dashboard → action → logout). Error states (wrong password, expired token, rate limit, offline fallback).
4. **evidence-collector Step 4e — Network inspection**: Mandatory (was optional). Detects Mixed Content, status 0, local leaks (localhost calls from deployed frontend).
5. **evidence-collector Step 4f**: Tests against `deploy_url` if available (Netlify/Vercel), not just localhost.
6. **reality-checker Step 2B — False Positive Guardrail**: Re-executes 2-3 random `qa-{N}` PASS tasks. If reality's re-run fails, evidence-collector's PASS was false.
7. **reality-checker Step 4B — Mixed Content DYNAMIC**: Browser-level runtime inspection (not static grep). Detects undefined env vars like `NEXT_PUBLIC_API_URL` causing silent localhost fallback.
8. **reality-checker Step 8 — Design Tools Usage Audit**: Verifies intent exists with full schema, visual-direction has extraction_status, brand.json is schema v2, all AUTO_AUDITs PASS.
9. **reality-checker Step 9 — Evidence Trail Mandatory**: Every PASS cites specific evidence (screenshot path, request URL, log line). No more "looks good to me".

Plus: **api-tester ESCALATES** if `api-spec` is missing (no silent fallback to `tareas.md`), **performance-benchmarker** uses PageSpeed Insights on `deploy_url` when available.

---

## Agent Catalog

| Phase | Agent | Role |
|:-----:|-------|------|
| * | `orquestador` | Central coordinator, manages all 5 phases, never does real work |
| 1 | `project-manager-senior` | Converts ideas into granular tasks with acceptance criteria |
| 2 | `ux-architect` | CSS foundation: tokens, layout, themes, breakpoints |
| 2 | `ui-designer` | Visual design system, components, WCAG AA accessibility |
| 2 | `security-engineer` | STRIDE threat model, OWASP Top 10, security headers |
| 2B | `brand-agent` | Brand identity: palette, typography, tone, personality |
| 2B | `image-agent` | Hero images via Gemini/HuggingFace FLUX.1 |
| 2B | `logo-agent` | SVG logos (FLUX.1 + vtracer vectorization) |
| 2B | `video-agent` | Background videos (Replicate LTXVideo / CSS fallback) |
| 3 | `frontend-developer` | React/Vue/TS, Tailwind, shadcn/ui, Zustand, TanStack Query |
| 3 | `backend-architect` | Hono/Express, Drizzle/Prisma, tRPC, PostgreSQL, Better Auth |
| 3 | `rapid-prototyper` | Multi-stack MVPs for fast validation |
| 3 | `mobile-developer` | React Native + Expo SDK 52+, NativeWind 4, Expo Router |
| 3 | `game-designer` | Game Design Document: mechanics, loops, economy, balance |
| 3 | `xr-immersive-developer` | Phaser.js, PixiJS, Canvas API, WebGL standalone games |
| 3 | `codepen-explorer` | Searches and extracts visual effects from CodePen via Playwright |
| 3 | `build-resolver` | Diagnoses and fixes build failures automatically |
| 3 | `evidence-collector` | Visual QA with Playwright MCP, screenshots across 3 viewports |
| 4 | `seo-discovery` | SEO audit, meta tags, JSON-LD, sitemap, llms.txt, AI discovery |
| 4 | `api-tester` | Endpoint coverage, OWASP API Top 10, P95 latency |
| 4 | `performance-benchmarker` | Core Web Vitals, Lighthouse, bundle analysis |
| 4 | `reality-checker` | Final pre-production gate with visual evidence |
| 5 | `git` | Commit + push to GitHub, branch management |
| 5 | `deployer` | Deploy to Vercel + Git Integration for auto-deploy |
| -- | `self-auditor` | Validates system health: agents, hooks, settings, protocols |

### Technical References (13 files)

| File | Content |
|------|---------|
| `agent-protocol` | Shared protocol: Engram 2-step reads, Return Envelope, universal rules |
| `better-auth-reference` | Better Auth 1.5 + Supabase + Vercel integration |
| `better-gsap-reference` | GSAP Tier 3: useGSAP, ScrollTrigger, SplitText, Next.js gotchas |
| `react-patterns-reference` | React 19, Next.js 15/16, Tailwind 4, Zustand 5 |
| `redis-patterns-reference` | Cache-aside, Pub/Sub, HyperLogLog, cursor pagination |
| `pocketbase-reference` | PocketBase boolean gotchas, rules, auth, Docker, HTTPS |
| `devops-vps-reference` | Mixed Content HTTPS, Oracle Cloud, nginx, Let's Encrypt |
| `nothing-design-reference` | Nothing Design System v3.0.0 -- tokens, components, platform mapping |
| `scroll-storytelling-reference` | Lenis, GSAP ScrollTrigger pinning, snap, horizontal scroll, parallax |
| `advanced-effects-reference` | Lottie, Rive, cursor effects, magnetic buttons, micro-interactions |
| `creative-coding-reference` | p5.js, GLSL shaders, generative art, particle systems |
| `reactive-audio-reference` | Tone.js, Web Audio API, audio visualization, sound design |
| `pipeline-reference` | Pipeline-specific details: tools per agent, stack table, VD checkpoint, DI engine, Nothing Design, 21st.dev, creative agents |

---

## Hook System

13 reactive hooks intercept tool calls in real time. Configured in `~/.claude/settings.json`, scripts live in `~/.claude/hooks/`.

| Hook | Type | Matcher | Action |
|------|------|---------|--------|
| `block-no-verify` | PreToolUse | Bash | **BLOCKS** git --no-verify, git push --force, rm -rf, git reset --hard, DROP TABLE, chmod 777, curl\|sh |
| `config-protection` | PreToolUse | Write/Edit | **BLOCKS** edits to .env, .pem, .key, credentials. **WARNS** on linting config changes |
| `quality-gate` | PostToolUse | Write/Edit | **WARNS** on debugger, .only(), @ts-ignore, hardcoded secrets |
| `console-log-warning` | PostToolUse | Write/Edit | **WARNS** on console.log/warn/error in production code (ignores tests) |
| `suggest-compact` | PostToolUse | global | **WARNS** every ~50 tool calls with pipeline phase context (async) |
| `pre-compact-engram` | PreCompact | lifecycle | **SAVES** snapshot to disk via trigger file, Boot Sequence dual-writes DAG State on next interaction (v2.3) |
| `cost-tracker` | PostToolUse | global | **LOGS** each tool call with category, sub-agent, model (async) |
| `session-summary` | Stop | lifecycle | **LOGS** session activity in JSONL for recovery (async) |
| `engram-sync` | Stop | lifecycle | **SYNCS** Engram memories to GitHub automatically (async, 60s timeout) |
| `session-start-context` | Notification | lifecycle | **LOADS** previous session context + hook health check at startup |
| `audit-system` | Manual | -- | Validates system integrity: agents, hooks, settings, protocols |
| `cost-report` | Manual | -- | Tool usage breakdown by category, sub-agent, frequency |
| `learning-index` | Manual | -- | Local discovery index with auto-tagging by technology |
| `frontend-audit.sh` | Utility (bash) | invoked by agent | Pre-return anti-generic audit — deterministic grep checks for SaaS teal, heading fonts, hero media, motion coherence, shadow coherence |

---

## Installation

### Prerequisites

Before starting, you need:

| Platform | You need installed first | Download |
|----------|------------------------|----------|
| **Linux** | **Claude Code CLI**, git, Node.js | [Claude Code](https://docs.anthropic.com/en/docs/claude-code/overview) |
| **Windows** | **Claude Desktop**, Git for Windows (includes Git Bash), Node.js | [Claude Desktop](https://claude.ai/download), [Git](https://git-scm.com/download/win), [Node.js](https://nodejs.org) |

> **Important:** Claude Code (Linux) or Claude Desktop (Windows) must be installed first. This system extends Claude with agents and hooks -- it does not work without it.

### Linux (Claude Code)

Open a terminal and run:
```bash
git clone https://github.com/Emaleo0522/claude-vibecoding.git
cd claude-vibecoding
bash install/linux.sh
```

The script installs agents, hooks, CLAUDE.md, settings, and configures git/GitHub/Vercel authentication. Restart Claude Code when done.

### Windows (Claude Desktop)

Open **Git Bash** (installed with Git for Windows) and run:
```bash
git clone https://github.com/Emaleo0522/claude-vibecoding.git
cd claude-vibecoding
```

Then follow the step-by-step guide in [`install/windows.md`](install/windows.md). It walks you through everything with screenshots-friendly instructions.

### CLAUDE.md -- Where It Lives

CLAUDE.md contains all system instructions. Claude reads it automatically from the **working directory** (project folder).

| Platform | Installed to | Template | Notes |
|----------|-------------|----------|-------|
| **Linux** | `~/CLAUDE.md` (global) | `templates/global-claude.md` | Claude Code reads it from any directory |
| **Windows** | `~/CLAUDE.md` (global) | `templates/windows-claude.md` | Includes Windows overrides (preview servers, ports, launch.json) |

Both versions contain the same core system (pipeline, agents, hooks, Engram, stack). The Windows version adds the `Overrides Windows` section with `preview_start`, `cmd /c` wrappers, and port management via `netstat/taskkill`.

### Post-Install Verification

```bash
# Agents installed (should be 38: 25 agents + 13 references)
ls ~/.claude/agents/*.md | wc -l

# Hooks installed (should be 13)
ls ~/.claude/hooks/*.js | wc -l

# CLAUDE.md present
head -3 ~/CLAUDE.md

# Tools available
git --version && node --version && gh --version && vercel --version

# Full system health check (optional but recommended)
node ~/.claude/hooks/audit-system.js
```

---

## Configuration

### Engram MCP (required)

Engram is the persistent memory system that lets the orchestrator and agents remember decisions, progress, and context across sessions. Without it, every conversation starts from scratch.

It is configured automatically during installation via `settings.json`. On Windows, it also requires downloading the Engram binary separately (see `install/windows.md`).

### Engram Sync (optional)

The `engram-sync` hook automatically pushes Engram memories to a private GitHub repo when a session ends. This enables:
- **Cross-machine continuity** -- start on your desktop, resume on laptop
- **Backup** -- memories survive even if your local Engram DB is deleted

To set it up:
1. Create a private GitHub repo (e.g., `my-engram-sync`)
2. Initialize it in `~/.engram/`: `cd ~/.engram && git init && git remote add origin https://github.com/YOUR_USER/my-engram-sync.git`
3. The `engram-sync` hook (already installed) handles the rest automatically

### Creative Pipeline Environment Variables (optional)

Required only if your project uses AI-generated visual assets (Phase 2B: logos, images, videos).

| Variable | Service | Cost | How to get it |
|----------|---------|------|---------------|
| `GEMINI_API_KEY` | Google AI Studio | ~$0.02-0.04/image | [aistudio.google.com/apikey](https://aistudio.google.com/apikey) -- requires billing enabled |
| `HF_TOKEN` | HuggingFace | Free | [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) |
| `REPLICATE_API_TOKEN` | Replicate | ~$0.05/video | [replicate.com/account/api-tokens](https://replicate.com/account/api-tokens) |

At least one image key (`GEMINI_API_KEY` or `HF_TOKEN`) is needed for the creative pipeline. If both are set, Gemini is primary with HuggingFace as fallback.

**Where to put them:**
- **Linux:** Add to `~/.bashrc` or `~/.zshrc`: `export GEMINI_API_KEY="your-key-here"`
- **Windows:** Add to system environment variables (Settings -> System -> About -> Advanced system settings -> Environment Variables), or create a file at `~/.claude/.env` with one variable per line: `GEMINI_API_KEY=your-key-here`

### Pixel Bridge (optional)

A pixel art office where agents walk to their desks when assigned tasks, report back to the orchestrator, and idle when inactive. Purely visual, does not affect pipeline operation.

Install during `linux.sh` (prompted) or follow the instructions in `install/windows.md`.

---

## Usage

The system operates in two modes:

| Mode | When to Use | How to Activate |
|------|------------|----------------|
| **Normal** | Questions, fixes, reviews, technical chat | Default -- just talk |
| **Orchestrator** | Complete software projects end-to-end | Say: "modo orquestador", "activa el pipeline", or "nuevo proyecto completo: X" |

### Starting a Project

```
modo orquestador -- quiero crear [your idea]
```

The system handles everything: plans tasks, designs architecture, implements with visual QA (max 3 retries per task), certifies (SEO, API, performance, final gate), and deploys to Vercel -- with your confirmation before git push and deploy.

### Resuming a Project

```
retomar [project-name]
```

The orchestrator reads the DAG State from Engram and resumes exactly where it left off, without re-executing completed phases or re-asking decided questions.

### Modifying an Existing Project

```
retomar [project-name] -- quiero cambiar [description of changes]
```

Uses Modification Mode: skips planning and architecture, creates only new tasks, runs mini Phase 3 + QA.

### Example Prompts

```
modo orquestador -- quiero crear una landing page para una cafetería de especialidad
modo orquestador -- nuevo proyecto completo: dashboard de analytics con auth y base de datos
modo orquestador -- app mobile de delivery con React Native
modo orquestador -- juego 2D tipo plataformas en el navegador
retomar mi-proyecto -- agrega un blog con markdown
retomar mi-proyecto -- cambia la paleta de colores a tonos más oscuros
```

---

## Architecture

```
~/.claude/
|-- agents/            # 25 agents + 13 references = 38 files
|-- design-data/       # Design Intelligence Engine (search.js + 8 CSVs)
|-- hooks/             # 13 reactive hooks
|-- settings.json      # hook config + Engram MCP
|-- settings.local.json # agent permissions
|-- codepen-vault/     # approved CodePen effects
|-- pixel-bridge/      # optional visual system
{working-directory}/
|-- CLAUDE.md          # system instructions (auto-read by Claude from the project dir)
```

### Model Routing

| Model | Agents | Criteria |
|-------|--------|----------|
| **Opus** | orchestrator, project-manager-senior, security-engineer, game-designer, reality-checker | Complex architectural decisions, planning, threat modeling, final certification |
| **Sonnet** | All others (20 agents) | Defined task execution, QA, utilities, creative |

### Key Rules

- The orchestrator **never** does real work -- only coordinates
- Sub-agents return **only short summaries** (status + files + issues)
- Only `evidence-collector` and `reality-checker` perform visual QA
- Only `git` makes commits/pushes -- never a dev agent
- Only `deployer` deploys to Vercel
- `git` and `deployer` act **only with user confirmation**
- Each dev task passes through `evidence-collector` before advancing (max 3 retries)
- The orchestrator does not activate `git` until `evidence-collector` returns PASS

---

## Adaptive Stack

The orchestrator selects the stack in Phase 1 based on project requirements. There is no fixed stack.

| Layer | Options | Default Preference |
|-------|---------|--------------------|
| Frontend | Next.js, SvelteKit, Nuxt, Astro, Vite+React | Next.js (apps), Vite+React (landing) |
| Backend | Hono, Express, Fastify | Hono (edge-ready) |
| Database | PostgreSQL, SQLite, Supabase | PostgreSQL (prod), Supabase (MVP) |
| ORM | Drizzle, Prisma | Drizzle (type-safe, edge) |
| Auth | Better Auth | Always (unless project has existing auth) |
| Mobile | React Native + Expo SDK 52+ | Expo (iOS + Android from one repo) |
| Games 2D | Phaser.js 3, PixiJS, Canvas API | Phaser.js |
| Games 3D | Three.js, Babylon.js | Three.js |
| Animation | CSS (Tier 1), Framer Motion (Tier 2), GSAP (Tier 3) | Escalate by complexity |
| Scroll | Lenis + GSAP ScrollTrigger | Lenis (storytelling), GSAP (pinning) |
| Creative | p5.js, GLSL shaders, Canvas 2D | p5.js (2D), Three.js shaders (3D) |
| Audio | Tone.js, Web Audio API | Tone.js (complete), Web Audio (simple) |

---

## Design Intelligence Engine

A local BM25 search engine that provides industry-specific design recommendations. Built on data from [ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill), ported to Node.js.

**Location:** `~/.claude/design-data/` (search.js + 8 CSVs, ~410KB total)

| Dataset | Rows | Content |
|---------|------|---------|
| products | 161 | Product types with recommended style, palette, and landing pattern |
| styles | 84 | UI styles with CSS keywords, performance, accessibility |
| colors | 160 | 12+ semantic color tokens per industry |
| typography | 73 | Font pairings with Google Fonts URLs |
| ux-guidelines | 98 | UX best practices with severity (HIGH/MEDIUM/LOW) |
| landing | 34 | Landing patterns with section order and conversion data |
| ui-reasoning | 161 | Decision rules and anti-patterns per industry |
| charts | 25 | Chart types with accessibility and library recommendations |

**Used in Phase 2 by:**
- `ux-architect` -- style, colors, CSS keywords, design variables, anti-patterns
- `ui-designer` -- landing pattern, anti-patterns, chart guidance, key effects
- `brand-agent` -- palette by industry, typographic mood, anti-patterns

```bash
# Full design system recommendation (~500-800 tokens)
node ~/.claude/design-data/search.js "luxury spa" --design-system -p "MySpa"

# Specific domain queries
node ~/.claude/design-data/search.js "dashboard" --domain chart -n 3
node ~/.claude/design-data/search.js "accessibility" --domain ux -n 5
```

The engine **informs, it does not decide**. The user's brief and anti-convergence rules always take priority. Anti-patterns with HIGH severity are mandatory.

---

## Visual Direction Checkpoint

Between Phase 2 (architecture) and Phase 3 (development), the orchestrator pauses to present the user with structured visual choices. This ensures every project has a unique identity instead of generic defaults.

**8 categories presented:**

| Category | Options (examples) |
|----------|--------------------|
| Visual style | editorial, immersive, minimalist, bold/colorful, other |
| Hero section | static image, background video, animated background, parallax, slider, text-only |
| Navigation | transparent with blur, fixed solid, hamburger-only, sidebar, mega-menu |
| Gallery | masonry, carousel, lightbox, horizontal scroll, hover reveal |
| Animation level | subtle (CSS only), moderate (Framer Motion), immersive (FM + GSAP) |
| Mood | dark, light, mixed, high contrast |
| Typography | display/impactful, elegant/serif, technical/mono, neutral/functional |
| Special effects | custom cursor, text animations, smooth scroll, parallax, page transitions, particles |

The user's choices are saved in Engram and flow to `ui-designer` (behavioral specs) and `frontend-developer` (design decision tree). If a CodePen vault effect or 21st.dev component matches the chosen direction, it is presented as a concrete option.

### Design Dials (quantitative 1-10)

After the 8 qualitative categories, the orchestrator asks for three numeric dials (or infers them from the chosen style with sensible defaults). These translate directly into implementation decisions:

| Dial | Range | What it controls |
|------|-------|-----------------|
| `DESIGN_VARIANCE` | 1 (clean/centered) -> 10 (asymmetric/experimental) | Layout experimentation -- 1-3 symmetric 12-col grids, 4-6 asymmetric heros + split layouts, 7-10 broken grid + rotated elements + collage |
| `MOTION_INTENSITY` | 1 (static) -> 10 (magnetic/scroll-triggered) | Animation sophistication -- 1-3 CSS transitions only, 4-6 Framer Motion enter/exit + scroll reveals, 7-10 GSAP timelines + pinning + SplitText + magnetic cursor |
| `VISUAL_DENSITY` | 1 (spacious/luxury) -> 10 (dense/dashboard) | Content concentration -- 1-3 editorial whitespace, 4-6 balanced marketing, 7-10 data-heavy multi-column with tabular figures |

**Defaults by style:** editorial `variance:4 motion:3 density:3`, immersive `variance:7 motion:8 density:4`, minimalist `variance:2 motion:2 density:2`, bold/colorful `variance:6 motion:6 density:6`.

**Consumed by agents:** `ui-designer` adjusts behavioral specs, `frontend-developer` selects the correct animation Tier (1 CSS / 2 Framer Motion / 3 GSAP), `ux-architect` scales the spacing base. Anti-patterns HIGH from the Design Intelligence Engine always override the dials on conflict.

### Style Presets

If the user picks a named preset instead of answering dial-by-dial, all three values plus CSS tokens, fonts, border-radius and motion curves are seeded from `design-data/style-presets.csv` (10 presets). Examples: `soft-luxury`, `neo-brutalism`, `editorial-magazine`, `dashboard-dense`, `glass-morphism`, `cyber-neon`.

The preset is loaded by `ui-designer` (Paso 0b-bis) and `frontend-developer` injects the CSS tokens into `:root` of the global stylesheet. `brand.json` still wins on color conflicts -- the preset informs defaults, not identity.

---

## Design Quality System

The pipeline includes several mechanisms to ensure every project looks unique and professional, not generic.

### Anti-Convergence

`brand-agent` checks previous projects stored in Engram before generating a new brand identity. If a palette, font pairing, or visual style was used recently, it avoids repeating it. This prevents the "everything looks the same" problem common with AI-generated designs.

### Behavioral Specs

`ui-designer` creates a behavioral specification for each component based on the animation level chosen in the Visual Direction Checkpoint:

| Level | What it means | Example |
|-------|--------------|---------|
| **Subtle** | CSS transitions only | Button hover: `opacity: 0.9`, 200ms ease |
| **Moderate** | Framer Motion | Button hover: `scale(1.05)` + shadow lift |
| **Immersive** | Framer Motion + GSAP | Button hover: magnetic effect + glow + ripple |

These specs are stored in Engram (`{project}/design-system`) and enforced during QA: `evidence-collector` verifies that the implemented behavior matches the specified level. A mismatch (e.g., immersive spec but only CSS transitions) results in a `FAIL_SPEC`.

### Typography Sources

`brand-agent` selects fonts from two sources:

- **Google Fonts** -- default, broadest compatibility, free
- **Fontshare** -- curated premium-quality fonts for projects requiring a more distinctive typographic identity

The Design Intelligence Engine provides a `typography_mood` recommendation per industry (display, elegant, technical, neutral), but `brand-agent` makes the final font selection.

### Brand Inspiration On-Demand

When the user's brief explicitly references a known brand ("Linear feel", "Stripe docs style", "Apple vibe"), `brand-agent` fetches the corresponding design profile from the public [awesome-design-md](https://github.com/VoltAgent/awesome-design-md) repository (68+ brand DESIGN.md files: Apple, Stripe, Linear, Notion, Vercel, Figma, Cursor, OpenAI, Claude, Ferrari, Tesla, Spotify, Airbnb, Nike, etc.).

**Only abstract tokens are extracted** -- color hues, spacing scale, motion curves, typography mood. **Never extracted:** logos, brand signatures, exact layouts, distinctive imagery. A guardrail enforces that the final result looks *inspired*, not *cloned* -- if the project is recognizable as "a fake Linear" the brand is rejected and regenerated.

When the brief has no brand reference, this step is skipped entirely and `design-data/style-presets.csv` is used instead -- cheaper in tokens and zero derivative risk.

### UI Audit Checklist (Modification Mode)

When the user asks for a redesign or says "this looks generic", the orchestrator runs a structured audit before delegating to `ui-designer`/`frontend-developer`:

1. **Spacing audit** -- stack gap consistency, density coherence with declared dial
2. **Typography hierarchy audit** -- max 4 font-sizes, heading vs body font consistency, line-height 1.5-1.75 on body
3. **Motion coherence audit** -- implemented intensity matches dial, `prefers-reduced-motion` fallback present when motion >= 4
4. **Color coherence audit** -- all colors exist in brand.json, WCAG AA contrast, no "5 shades of gray" drift
5. **Layout variance audit** -- variance dial matches implementation, no "every section is a centered div" when variance >= 5

The audit produces concrete fix instructions, not vague suggestions.

---

## Modification Mode

For projects that have already been built and deployed, the pipeline supports a lightweight modification flow instead of re-running the full 5 phases.

```
retomar [project-name] -- quiero cambiar [what to modify]
```

**How it works:**
1. **Analysis** -- reads the existing DAG State and codebase to understand current state
2. **Light planning** -- creates only the new/changed tasks (no re-planning completed work)
3. **Mini Phase 3 + QA** -- implements changes with the same dev ↔ evidence-collector loop
4. **Deploy** -- pushes changes through git + deployer (with user confirmation)

Phases 1, 2, and 4 are skipped entirely. The system preserves all previous decisions (stack, design system, brand) and only touches what needs to change.

---

## QA System Details

### Visual QA (evidence-collector)

Every development task passes through visual QA before advancing. The QA agent:

1. Builds for production (`npm run build && npm start`)
2. Captures screenshots in 3 viewports: Desktop (1280x720), Tablet (768x1024), Mobile (375x667)
3. Tests interactive elements (clicks, form inputs, navigation)
4. Runs accessibility checks (axe-core -- 0 critical/serious violations required)
5. Checks browser console for errors (0 errors required for PASS)
6. Verifies behavioral specs match the design system

**PASS threshold:** Rating B- or better, zero console errors, zero critical accessibility violations.

### Failure Classification

When QA fails, the failure is classified to give targeted feedback:

| Type | Meaning | Action |
|------|---------|--------|
| **FAIL_CODE** | Code doesn't work -- errors, crashes, layout broken, feature missing | Dev agent fixes code |
| **FAIL_SPEC** | Code works but doesn't match the spec -- wrong animation level, incorrect interactions | Dev agent re-reads design system and adjusts |

Each task gets up to 3 retry attempts. After 3 failures, the orchestrator escalates to the user.

---

## Security Posture Check

Beyond real-time hooks (`config-protection`, `quality-gate`), `reality-checker` runs a retrospective security scan as **Step 6** of Phase 4 certification. This catches secrets and supply-chain issues that existed in the codebase before the pipeline started, or that hooks may have missed.

### 6.1 -- Secret Scan

Static scan against 9 secret patterns across `.ts/.tsx/.js/.jsx/.mjs/.cjs/.json/.yaml/.yml/.env` files (excluding `node_modules`, `.next`, `build`, `dist`, `__tests__`, `.env.example`, `docs`):

| Pattern | Example match |
|---------|---------------|
| AWS Access Key ID | `AKIA[0-9A-Z]{16}` |
| GitHub Personal Access Token | `ghp_[A-Za-z0-9]{36}` |
| GitHub OAuth / App Token | `(gho_\|ghu_\|ghs_\|ghr_)[A-Za-z0-9]{36}` |
| Stripe Live Key | `sk_live_[A-Za-z0-9]{24,}` |
| Slack Bot Token | `xox[baprs]-...` |
| Google API Key | `AIza[0-9A-Za-z_-]{35}` |
| OpenAI / Anthropic | `sk-[A-Za-z0-9]{32,}` / `sk-ant-[A-Za-z0-9_-]{32,}` |
| Private keys (RSA/EC/DSA/OPENSSH/PGP) | `-----BEGIN ... PRIVATE KEY-----` |
| JWT in source | `eyJ...eyJ...` three-segment pattern |

Any match in source code is a **BLOCKER**. The reporter outputs file + line + type only -- never the matched value, to avoid re-leaking the secret.

### 6.2 -- Lock File Integrity

Supply-chain checks executed per detected package manager (npm/pnpm/yarn/bun):

1. A lock file **must exist** when `package.json` is present (reproducible builds)
2. The lock file **must not be gitignored** (CI and collaborators need the same resolution)
3. For npm: `lockfile-lint` validates allowed hosts, HTTPS schemes, no `file://` resolutions (registry poisoning defense)
4. `npm audit` / `pnpm audit` / `yarn npm audit` with severity >= HIGH is a **BLOCKER** until the user either runs `audit fix` or documents the accepted risk in `security-notes`

The checks are defensive -- they complement what `security-engineer` declared in Phase 2 (threat model, headers, Better Auth config) rather than duplicating it. No new MCPs, no new dependencies -- everything uses tools already available (Bash + Grep + `npx lockfile-lint`).

---

## Authentication

**Better Auth** is the default authentication system for all new projects. It provides email/password, social login, and session management out of the box.

Key integration points:
- `backend-architect` sets up the server-side auth (routes, database tables, session config)
- `frontend-developer` implements the client-side auth (login forms, session provider, protected routes)
- `rapid-prototyper` handles full-stack auth in MVPs

The system includes a production-tested reference (`better-auth-reference.md`) covering Better Auth + Supabase + Vercel + Next.js 16, with specific patterns for connection pooling, middleware migration (proxy.ts), and cookie handling.

> If a project already uses Clerk, Supabase Auth, or custom JWT, those are preserved. Better Auth is only the default for new projects.

---

## 21st.dev Components

[21st.dev](https://21st.dev) is a community library of animated React components (17,600+ snippets). The system accesses it via **Context7 MCP** (Upstash) -- no API key required.

**How it works in the pipeline:**

1. **Phase 1** -- the orchestrator decides `component_source: "21st.dev"` in the DAG State based on project type (visual/animated projects benefit; dashboards typically don't)
2. **Visual Direction Checkpoint** -- if 21st.dev is active, available components matching the chosen style are presented as options
3. **Phase 3** -- `frontend-developer` queries Context7 for specific component types:

```
resolve-library-id("21st.dev")  ->  /websites/21st_dev_community_components
query-docs(library_id, "animated hero section")  ->  code snippets
```

**Key rules:**
- **Inspiration + base, never copy-paste** -- every component is adapted to the project's brand (colors, fonts, spacing)
- **No 21st.dev packages installed** -- code is extracted and integrated directly
- **Max 3 queries per task** -- to avoid context bloat
- **Fallback chain** -- if no suitable component found, falls through to CodePen vault or custom implementation

**Setup:** Context7 MCP is configured during installation (Linux: `claude mcp add context7`, Windows: `claude_desktop_config.json`). Permissions are pre-configured in `settings.local.json`.

---

## CodePen Vault

The system maintains a curated library of visual effects at `~/.claude/codepen-vault/`. The workflow:

1. **Discovery** -- `codepen-explorer` searches CodePen for effects matching the project's visual direction
2. **User approval** -- effects are presented to the user; only approved ones are saved to the vault
3. **Adaptation** -- `frontend-developer` reads from the vault and adapts the effect to the project's brand (colors, fonts, spacing)
4. **Post-effects checkpoint** -- after implementing effects, the full page is shown to the user before advancing to Phase 4

Vault metadata is stored in Engram (`codepen-vault/{slug}`) for cross-project searchability. The actual code lives on disk.

---

## Mobile Deployment (EAS Build)

For React Native + Expo projects, deployment uses **Expo Application Services (EAS)** instead of Vercel:

| Profile | Platform | Output | Cost |
|---------|----------|--------|------|
| `preview` | Android | APK (direct install) | Free (30 builds/month) |
| `preview` | iOS | IPA (requires TestFlight) | Requires Apple Developer ($99/year) |
| `production` | Android | AAB (Google Play) | Free |
| `production` | iOS | Signed IPA (App Store) | Requires Apple Developer |

The `deployer` agent handles EAS builds. Store submission (`eas submit`) requires explicit user confirmation and is never automatic.

---

## Pre-Authorization (PRE_AUTH)

When the user's original message includes words like "sube a git", "deploy", "push", or "publica", the system treats this as pre-authorization for git push and deployment. The `git` and `deployer` agents receive a `PRE_AUTH: true` flag and proceed without asking for confirmation again.

This avoids the friction of being asked "are you sure?" for an action the user explicitly requested. If the original message doesn't include deployment intent, confirmation is always requested.

---

## Pipeline Resilience

| Mechanism | What It Solves |
|-----------|---------------|
| **Phase Gates** | Verifies outputs from the previous phase exist before advancing. Re-delegates if missing. |
| **Error Recovery** | If an agent crashes without returning a result, the orchestrator checks Engram, recovers what it can, and re-delegates. |
| **Graceful Degradation** | If Engram is down, uses local disk as fallback. If Playwright is unavailable, performs code-only QA. |
| **Rejection Workflows** | Up to 3 retries for rejected creative assets with escalating strategy changes. |
| **NEEDS WORK Flow** | If reality-checker does not certify, the orchestrator returns to Phase 3 only for affected tasks. |

---

## Context Window Management (v2.2)

The system uses several mechanisms to protect the context window from bloat and ensure state survives compaction events.

### Progressive DAG State Loading

The DAG State (project progress tracker) can grow to 10+ KB for advanced projects. Instead of loading it fully on every interaction, the orchestrator uses 2 levels:

| Level | What it loads | Tokens | When |
|-------|--------------|--------|------|
| **Light boot** | Current phase, current task/total, stack (1-liner), last save timestamp | ~50-100 | Always on resume |
| **Full boot** | Entire DAG State (completed phases, failed tasks, certifications, all decisions) | ~500-2000 | Phase transitions, escalations, scope changes, certification |

The orchestrator reads the full DAG State once at startup to extract the light summary, then retains only the summary + the observation ID. It re-reads the full state on demand when decisions require it.

### PreCompact Save (v2.3)

When Claude's context is about to be compacted (context window nearing capacity), the `pre-compact-engram` hook intercepts the event and:

1. **Saves a session snapshot** to disk (tool count, working directory, pipeline status)
2. **Writes a trigger file** at `~/.claude/snapshots/compaction-pending.json`

On the next interaction, the orchestrator's Boot Sequence detects this trigger file and immediately:
1. Saves DAG State to Engram via `mem_update`
2. Writes DAG State to disk at `{project_dir}/.pipeline/estado.yaml`
3. Deletes the trigger file

After saving, compaction is safe -- the Boot Sequence recovers from Engram or disk.

> **v2.3 change:** Previous versions emitted instructions via stderr, which caused empty responses without tool calls. The trigger file pattern is reliable and non-blocking.

### Dual-Write Pattern

Critical state is always written to two locations:

```
Primary:  Engram MCP  ->  {proyecto}/estado  (searchable, cross-session)
Fallback: Local disk  ->  {project_dir}/.pipeline/estado.yaml
```

On recovery, the Boot Sequence checks Engram first, then falls back to disk. This survives MCP failures, network issues, and database locks.

### Token Budget Strategy

| Mechanism | Tokens Saved | How |
|-----------|-------------|-----|
| Light boot vs full boot | ~400-1900 per resume | Only load full DAG when decisions needed |
| Short return envelopes | ~500-2000 per delegation | Sub-agents return status + files + issues, never full code |
| Screenshots to disk | ~5000+ per QA cycle | Images saved as files, only paths passed in context |
| Selective drawer reads | ~200-500 per agent | Each agent reads only its relevant Engram drawers |
| PreCompact save-then-compact | 100% context recovery | State persisted before compaction, nothing lost |

---

## Credits

- [Engram](https://github.com/Gentleman-Programming/engram) by Gentleman Programming -- persistent memory MCP
- [pixel-agents](https://github.com/pablodelucca/pixel-agents) by @pablodelucca -- pixel art office (Pixel Bridge adapted from this)
- [Agency Agents](https://github.com/msitarzewski/agency-agents) -- specialized agents with metrics (inspiration)
- [Agent Teams Lite](https://github.com/Gentleman-Programming/agent-teams-lite) -- DAG State, minimal handoffs, Engram (inspiration)

---

## License

MIT
