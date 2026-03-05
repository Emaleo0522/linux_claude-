#!/bin/bash
# ============================================================
# Claude Code — Vibecoding Agent System
# Script de instalación automática para Linux
# ============================================================

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

info()  { echo -e "${GREEN}[✓]${NC} $1"; }
warn()  { echo -e "${YELLOW}[!]${NC} $1"; }
error() { echo -e "${RED}[✗]${NC} $1"; exit 1; }

echo ""
echo "============================================"
echo "  Claude Code — Vibecoding Agent System"
echo "  Instalación automática"
echo "============================================"
echo ""

# ── 1. Verificar dependencias básicas ────────────────────
for cmd in git python3 curl; do
  command -v $cmd &>/dev/null || error "$cmd no está instalado. Instalalo con: sudo apt-get install $cmd"
done
info "Dependencias básicas: git, python3, curl"

# ── 2. Instalar gh CLI si no está ────────────────────────
if ! command -v gh &>/dev/null; then
  warn "gh CLI no encontrado. Instalando..."
  sudo apt-get update -qq && sudo apt-get install -y gh
  info "gh CLI instalado"
else
  info "gh CLI: $(gh --version | head -1)"
fi

# ── 3. Pedir datos del usuario ───────────────────────────
echo ""
echo "Necesito algunos datos para configurar git y GitHub."
echo ""

read -p "  Tu nombre (aparece en los commits, ej: Ema): " GIT_NAME
while [[ -z "$GIT_NAME" ]]; do
  read -p "  Nombre no puede estar vacío: " GIT_NAME
done

read -p "  Tu email de GitHub (ej: usuario@gmail.com): " GIT_EMAIL
while [[ -z "$GIT_EMAIL" ]]; do
  read -p "  Email no puede estar vacío: " GIT_EMAIL
done

read -p "  Tu usuario de GitHub (ej: MiUsuario): " GH_USER
while [[ -z "$GH_USER" ]]; do
  read -p "  Usuario no puede estar vacío: " GH_USER
done

# ── 4. Configurar git global ─────────────────────────────
git config --global user.name "$GIT_NAME"
git config --global user.email "$GIT_EMAIL"
git config --global init.defaultBranch main
info "Git configurado: $GIT_NAME <$GIT_EMAIL>"

# ── 5. Generar clave SSH si no existe ────────────────────
SSH_KEY="$HOME/.ssh/id_ed25519"
if [[ ! -f "$SSH_KEY" ]]; then
  mkdir -p ~/.ssh && chmod 700 ~/.ssh
  ssh-keygen -t ed25519 -C "$GIT_EMAIL" -f "$SSH_KEY" -N ""
  info "Clave SSH generada: $SSH_KEY"
else
  info "Clave SSH existente: $SSH_KEY"
fi

# ── 6. Instalar agentes en ~/.claude/agents/ ─────────────
CLAUDE_AGENTS="$HOME/.claude/agents"
mkdir -p "$CLAUDE_AGENTS/skills"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

cp "$SCRIPT_DIR/agents/"*.md "$CLAUDE_AGENTS/"
cp "$SCRIPT_DIR/agents/skills/engram_policy.md" "$CLAUDE_AGENTS/skills/"

AGENT_COUNT=$(ls "$CLAUDE_AGENTS/"*.md 2>/dev/null | wc -l)
info "Agentes instalados en $CLAUDE_AGENTS ($AGENT_COUNT agentes)"

# ── 7. Actualizar usuario de GitHub en agente git ────────
sed -i "s|<usuario>|$GH_USER|g" "$CLAUDE_AGENTS/git.md" 2>/dev/null || true

# ── 8. Autenticar gh CLI ─────────────────────────────────
echo ""
warn "Necesitás autenticar GitHub CLI. Se abrirá el navegador."
read -p "  Presioná Enter para continuar..."
gh auth login --web -p ssh || warn "Autenticación saltada. Podés correr 'gh auth login --web -p ssh' después."

# ── 9. Instrucciones para SSH ────────────────────────────
echo ""
echo "============================================"
echo "  ACCIÓN REQUERIDA — Agregar clave SSH"
echo "============================================"
echo ""
echo "Copiá esta clave y pegala en GitHub:"
echo ""
cat "$SSH_KEY.pub"
echo ""
echo "Pasos:"
echo "  1. Ir a github.com → tu foto → Settings"
echo "  2. SSH and GPG keys → New SSH key"
echo "  3. Título: 'Mi PC Linux'"
echo "  4. Pegar la clave → Add SSH key"
echo ""
warn "Si ya la agregaste antes, podés ignorar este paso."
read -p "  Presioná Enter cuando hayas agregado la clave..."

# ── 10. Verificar conexión SSH ───────────────────────────
if ssh -T git@github.com 2>&1 | grep -q "successfully authenticated"; then
  info "Conexión SSH con GitHub: OK"
else
  warn "No se pudo verificar SSH. Verificá manualmente con: ssh -T git@github.com"
fi

# ── Resumen ──────────────────────────────────────────────
echo ""
echo "============================================"
echo "  Instalación completada"
echo "============================================"
echo ""
info "Git:     $GIT_NAME <$GIT_EMAIL>"
info "GitHub:  $GH_USER"
info "Agentes: $CLAUDE_AGENTS ($AGENT_COUNT agentes)"
echo ""
echo "Para empezar, abrí Claude Code y escribí:"
echo "  @orquestador quiero crear [tu idea]"
echo ""
