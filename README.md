# Claude Code — Vibecoding Agent System

Sistema de agentes para Claude Code orientado a vibecoding: crear webs, apps y juegos indie sin saber programar.

## Instalación rápida

```bash
git clone git@github.com:Emaleo0522/linux_claude-.git
cd linux_claude-
chmod +x install.sh && ./install.sh
```

El script instala todo automáticamente: agentes, git, SSH, GitHub CLI.

## Agentes incluidos

| Agente | Rol |
|---|---|
| `orquestador` | Principal: recibe pedidos, divide en fases, delega y mantiene memoria |
| `techlead` | Define arquitectura, stack y estructura del proyecto |
| `builder` | Implementa el código y levanta preview local |
| `qa` | Prueba el resultado y valida que funcione |
| `deployer` | Publica en Vercel (usa MCP de Vercel) |
| `git` | Maneja repositorios: crear, commitear, pushear, eliminar |
| `diagrammer` | Genera diagramas Excalidraw y los muestra en el navegador |
| `librarian` | Busca documentación técnica con Context7 |
| `task-planner` | Convierte ideas en tareas concretas con Definition of Done |
| `ops` | Levanta y verifica servicios locales (Engram, preview, Excalidraw) |

## Flujo de trabajo

```
Tu idea → orquestador → task-planner → techlead → librarian (si hace falta)
                      → builder (implementa + preview) → qa (prueba)
                      → git (commit+push) → deployer (Vercel)
```

## Política de memoria

La memoria entre sesiones se maneja con **Engram**. Solo el orquestador guarda memoria.
Ver política completa en `agents/skills/engram_policy.md`.

## Política de herramientas

- Solo `librarian` puede usar Context7 MCP (documentación)
- Solo `orquestador` puede usar Engram MCP (memoria)
- Solo `deployer` puede usar Vercel MCP (deploy)

## Requisitos

- Linux (Ubuntu/Debian recomendado)
- Claude Code instalado
- Conexión a internet (para la instalación)

## Estructura

```
agents/
├── *.md              → definiciones de agentes
├── skills/
│   └── engram_policy.md
└── tools/
    └── excalidraw_serve.py
install.sh            → instalación automática
```
