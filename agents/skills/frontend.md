# SKILL: Frontend Development (2026)

Leer esta skill COMPLETA antes de escribir la primera línea cuando el proyecto tenga
HTML, CSS, JavaScript, React, Vue, Phaser u otro frontend.

---

## 1. IDENTIFICAR EL TIPO DE PROYECTO

Leer el spec de techlead y clasificar:

| Si el spec menciona... | Tipo |
|---|---|
| "landing", "portfolio", "web simple", sin framework | → **Web estática** |
| "React", "Vue", "Svelte", "SPA", "componentes" | → **App Vite** |
| "juego", "game", "Phaser", "canvas", "sprites", "tilemap" | → **Juego Phaser** |
| "API", "endpoint", "Express", "servidor", "backend" | → **API Node** |

Si el spec no especifica, usar la opción más simple que resuelva el pedido.
Más simple = menos dependencias = menos cosas que pueden fallar.

---

## 2. SETUP Y ESTRUCTURA POR TIPO

### WEB ESTÁTICA

Sin instalación. Directo al código.

```
proyecto/
├── index.html
├── css/
│   └── styles.css
├── js/
│   └── main.js
└── assets/
    ├── images/
    └── fonts/
```

Preview: `npx serve . -p 3000`

---

### APP CON VITE (React)

```bash
npm create vite@latest <nombre> -- --template react
cd <nombre>
npm install
```

Para que corra en puerto 3000, agregar en `vite.config.js`:
```js
export default {
  server: { port: 3000 }
}
```

Luego: `npm run dev`

Estructura de `src/`:
```
src/
├── components/    ← piezas reutilizables (Button, Card, etc.)
├── pages/         ← vistas completas (Home, About, etc.)
├── hooks/         ← lógica reutilizable (useData, useForm, etc.)
├── utils/         ← funciones helper puras
└── assets/        ← imágenes/fuentes importadas en código
```

Assets que se usan por URL (ej: imágenes en CSS) → van en `public/`, no en `src/assets/`.

---

### JUEGO PHASER 3

**Opción A — CDN** (para proyectos simples, sin build, preferida):
```html
<!-- en index.html -->
<script src="https://cdn.jsdelivr.net/npm/phaser@3/dist/phaser.min.js"></script>
```

```
juego/
├── index.html
├── js/
│   ├── main.js              ← config del juego + arranque
│   ├── scenes/
│   │   ├── BootScene.js     ← carga TODOS los assets aquí
│   │   ├── MenuScene.js     ← pantalla de inicio (opcional)
│   │   ├── GameScene.js     ← lógica principal
│   │   └── GameOverScene.js ← pantalla de fin
│   └── objects/
│       ├── Player.js        ← clase del jugador
│       └── Enemy.js         ← clase de enemigos
└── assets/
    ├── images/
    ├── spritesheets/        ← atlases de sprites
    └── audio/
```

**Opción B — npm** (si el spec pide estructura más compleja):
```bash
npm create @phaserjs/game@latest
```

**Patrón de `main.js`:**
```js
const config = {
  type: Phaser.AUTO,
  width: 800,
  height: 600,
  scale: {
    mode: Phaser.Scale.FIT,        // responsive automático
    autoCenter: Phaser.Scale.CENTER_BOTH
  },
  physics: {
    default: 'arcade',
    arcade: { gravity: { y: 300 }, debug: false }
  },
  scene: [BootScene, MenuScene, GameScene, GameOverScene]
};
new Phaser.Game(config);
```

**Patrón de `BootScene.js`:**
```js
class BootScene extends Phaser.Scene {
  constructor() { super({ key: 'BootScene' }); }
  preload() {
    // Cargar TODOS los assets aquí, no en GameScene
    this.load.image('player', 'assets/images/player.png');
    this.load.spritesheet('explosion', 'assets/spritesheets/explosion.png',
      { frameWidth: 64, frameHeight: 64 });
    this.load.audio('jump', 'assets/audio/jump.ogg');
  }
  create() { this.scene.start('MenuScene'); }
}
```

Preview: `npx serve . -p 3000`

---

### API NODE/EXPRESS

```bash
npm init -y
npm install express cors dotenv
```

```
api/
├── server.js
├── routes/
│   └── index.js
├── .env
└── .gitignore    ← incluir: node_modules, .env
```

**`server.js` base:**
```js
const express = require('express');
const cors = require('cors');
require('dotenv').config();

const app = express();
app.use(cors());
app.use(express.json());

app.get('/health', (req, res) => res.json({ status: 'ok' }));

app.use('/api', require('./routes/index'));

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`API corriendo en puerto ${PORT}`));
```

Preview: `node server.js`

---

## 3. CSS — QUÉ USAR SEGÚN EL TIPO

| Tipo | CSS recomendado |
|---|---|
| Web estática | CSS vanilla con variables |
| App Vite/React | Tailwind CSS v4 |
| Juego Phaser | No aplica (todo es canvas) |
| API Node | No aplica |

---

### CSS VANILLA — Patrón base

```css
/* ── Design tokens en :root ─────────────────── */
:root {
  /* Colores */
  --color-primary:   #3b82f6;
  --color-secondary: #8b5cf6;
  --color-bg:        #ffffff;
  --color-text:      #1a1a1a;
  --color-muted:     #6b7280;
  --color-border:    #e5e7eb;

  /* Espaciado */
  --space-xs:  0.25rem;
  --space-sm:  0.5rem;
  --space-md:  1rem;
  --space-lg:  2rem;
  --space-xl:  4rem;

  /* Tipografía */
  --font-size-sm:   0.875rem;
  --font-size-base: 1rem;
  --font-size-lg:   1.25rem;
  --font-size-xl:   1.5rem;
  --font-size-2xl:  2rem;

  /* Bordes y sombras */
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 16px;
}

/* ── Regla de layout: Grid para página, Flex para componentes ── */

/* Grid → estructura de la página (2D) */
.layout {
  display: grid;
  grid-template-columns: 1fr;       /* mobile-first */
  gap: var(--space-md);
}

@media (min-width: 768px) {
  .layout {
    grid-template-columns: 250px 1fr; /* sidebar + contenido */
  }
}

/* Flexbox → alineación dentro de componentes (1D) */
.card {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: var(--space-md);
  border-radius: var(--radius-md);
}

/* ── Mobile first siempre ─────────────────── */
/* Escribir estilos base para móvil, luego agregar @media para tablet/desktop */
```

---

### TAILWIND v4 — Setup en Vite

```bash
npm install tailwindcss @tailwindcss/vite
```

En `vite.config.js`:
```js
import tailwindcss from '@tailwindcss/vite';
export default {
  plugins: [tailwindcss()],
  server: { port: 3000 }
}
```

En `src/index.css`:
```css
@import "tailwindcss";

/* Tokens personalizados con @theme (v4, sin tailwind.config.js) */
@theme {
  --color-primary: #3b82f6;
  --color-secondary: #8b5cf6;
  --font-sans: 'Inter', sans-serif;
}
```

Usarlo en componentes:
```jsx
<button className="bg-primary text-white px-4 py-2 rounded-md hover:opacity-90">
  Acción
</button>
```

---

## 4. ASSETS — REGLAS

### Organización
```
assets/
├── images/       ← PNG, JPG, SVG, WebP
├── spritesheets/ ← atlases de sprites (Phaser)
├── audio/        ← OGG preferido (mejor compatibilidad), MP3 como fallback
└── fonts/        ← solo si son fuentes locales (no Google Fonts)
```

### Formatos recomendados
- Fotografías → **WebP** (30-50% más liviano que JPG)
- Íconos/logos → **SVG** (escalable, sin pérdida)
- Sprites de juego → **PNG** (transparencia)
- Audio → **OGG** principal + **MP3** fallback

### En Phaser: sprite sheets vs imágenes sueltas
```
50 imágenes sueltas → 50 draw calls → ~45 FPS
1 sprite sheet con 50 sprites → 1-5 draw calls → 60 FPS
```
Siempre preferir sprite sheets para personajes, tiles y efectos.

### En Vite:
- Imágenes usadas en JSX/CSS → `src/assets/` (Vite las optimiza)
- Imágenes referenciadas por URL (ej: en Phaser o CSS dinámico) → `public/`

---

## 5. PERFORMANCE ESENCIAL

```html
<!-- Imágenes principales (visibles al cargar) → cargar con prioridad -->
<img src="hero.webp" alt="Hero" fetchpriority="high">

<!-- Imágenes fuera de pantalla → lazy load -->
<img src="foto.webp" alt="Descripción" loading="lazy">

<!-- JavaScript → siempre defer para no bloquear el render -->
<script src="main.js" defer></script>
```

- Nunca dejar `console.log` en el código final
- Imágenes: comprimir antes de agregar (WebP < 200KB por imagen)
- CSS: evitar `!important`, evitar selectores ultra-específicos
- Fuentes: máximo 2 familias tipográficas por proyecto

---

## 6. ACCESIBILIDAD ESENCIAL

```html
<!-- HTML semántico siempre -->
<header>, <main>, <section>, <nav>, <footer>, <article>

<!-- Todo input tiene label -->
<label for="email">Email</label>
<input type="email" id="email" name="email">

<!-- Imágenes: alt descriptivo (o vacío si son decorativas) -->
<img src="logo.png" alt="Logo de la empresa">
<img src="decoracion.png" alt="">  <!-- decorativa → alt vacío -->

<!-- Botones: texto descriptivo, no "click aquí" -->
<button type="button">Guardar cambios</button>
```

- Contraste mínimo texto/fondo: **4.5:1** (texto normal), **3:1** (texto grande)
- Todos los elementos interactivos deben ser accesibles con Tab
- No usar `<div>` como botón — usar `<button>`

---

## 7. ERRORES COMUNES Y SOLUCIÓN

| Error | Causa | Solución |
|---|---|---|
| `Cannot find module` | `npm install` no corrió | `npm install` |
| Assets no cargan en Phaser | Servidor no activo | `npx serve . -p 3000` |
| CORS error | Fetch sin servidor | Usar servidor local, no file:// |
| Puerto 3000 ocupado | Proceso anterior | Ver protocolo de puerto en builder.md |
| `Uncaught ReferenceError` | Script cargado antes del DOM | Agregar `defer` al `<script>` |
| Imágenes rotas en Vite | Assets en lugar incorrecto | Ver sección 4 (src/assets vs public/) |
| `vite: command not found` | Olvidó `npm install` | `npm install` primero |
| Phaser corre pero no muestra sprites | Assets no preloaded en BootScene | Mover todos los `this.load.*` a BootScene |
