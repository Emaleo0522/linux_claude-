#!/usr/bin/env python3
"""
Servidor Excalidraw para el agente DIAGRAMMER.
Uso: python3 excalidraw_serve.py <ruta_archivo.excalidraw>

Endpoints:
  GET /         → viewer HTML del diagrama
  GET /health   → {"status": "ok"}
  GET /shutdown → cierra el servidor y el navegador (window.close)
"""
import sys, json, os, signal, threading
import http.server

PORT = 8765

def render_svg(elements):
    parts = []
    arrow_colors = set()
    for el in elements:
        if el["type"] == "arrow":
            arrow_colors.add(el.get("strokeColor", "#000"))

    defs = "<defs>"
    for color in arrow_colors:
        cid = color.replace("#", "")
        defs += (
            f'<marker id="arr_{cid}" markerWidth="8" markerHeight="8" '
            f'refX="6" refY="3" orient="auto">'
            f'<path d="M0,0 L0,6 L8,3 z" fill="{color}"/></marker>'
        )
    defs += "</defs>"

    for el in elements:
        t = el["type"]
        x, y, w, h = el["x"], el["y"], el["width"], el["height"]
        stroke = el.get("strokeColor", "#000")
        fill = el.get("backgroundColor", "transparent")
        if fill == "transparent": fill = "none"
        sw = el.get("strokeWidth", 1)
        opacity = el.get("opacity", 100) / 100
        dash = "8,4" if el.get("strokeStyle") == "dashed" else "none"
        rx = "10" if el.get("roundness") else "0"

        if t == "rectangle":
            parts.append(
                f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
                f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}" '
                f'stroke-dasharray="{dash}" opacity="{opacity}"/>'
            )
        elif t == "text":
            color = el.get("strokeColor", "#000")
            fs = el.get("fontSize", 14)
            align = el.get("textAlign", "left")
            anchor = {"center": "middle", "left": "start", "right": "end"}.get(align, "start")
            tx = x + (w / 2 if align == "center" else 0)
            for i, line in enumerate(el.get("text", "").split("\n")):
                safe = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                parts.append(
                    f'<text x="{tx}" y="{y + fs + i * fs * 1.3}" '
                    f'font-family="monospace" font-size="{fs}" fill="{color}" '
                    f'text-anchor="{anchor}" opacity="{opacity}">{safe}</text>'
                )
        elif t == "arrow":
            pts = el.get("points", [])
            if len(pts) >= 2:
                abs_pts = [(el["x"] + p[0], el["y"] + p[1]) for p in pts]
                d = "M " + " L ".join(f"{p[0]},{p[1]}" for p in abs_pts)
                cid = stroke.replace("#", "")
                parts.append(
                    f'<path d="{d}" fill="none" stroke="{stroke}" stroke-width="{sw}" '
                    f'stroke-dasharray="{dash}" opacity="{opacity}" '
                    f'marker-end="url(#arr_{cid})"/>'
                )

    return defs + "".join(parts)


def build_html(excalidraw_path):
    with open(excalidraw_path) as f:
        data = json.load(f)

    elements = data["elements"]
    xs = [el["x"] for el in elements]
    ys = [el["y"] for el in elements]
    xs2 = [el["x"] + el["width"] for el in elements]
    ys2 = [el["y"] + el["height"] for el in elements]
    pad = 30
    vx, vy = min(xs) - pad, min(ys) - pad
    vw = max(xs2) - min(xs) + pad * 2
    vh = max(ys2) - min(ys) + pad * 2

    svg_content = render_svg(elements)
    filename = os.path.basename(excalidraw_path)

    return f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>{filename}</title>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ background: #1e1e2e; color: #cdd6f4; font-family: monospace; }}
    header {{ padding: 12px 20px; background: #181825; border-bottom: 1px solid #313244;
              display: flex; align-items: center; justify-content: space-between; }}
    header h1 {{ font-size: 14px; color: #89b4fa; }}
    header span {{ font-size: 12px; color: #6c7086; }}
    .canvas {{ padding: 20px; display: flex; justify-content: center; }}
    svg {{ background: #fff; border-radius: 8px;
           box-shadow: 0 4px 24px rgba(0,0,0,.4); max-width: 100%; }}
    .status {{ position: fixed; bottom: 12px; right: 16px; font-size: 11px;
               color: #a6e3a1; background: #181825; padding: 4px 10px;
               border-radius: 4px; border: 1px solid #313244; }}
  </style>
</head>
<body>
  <header>
    <h1>DIAGRAMMER — {filename}</h1>
    <span>{len(elements)} elementos</span>
  </header>
  <div class="canvas">
    <svg xmlns="http://www.w3.org/2000/svg"
         viewBox="{vx} {vy} {vw} {vh}"
         width="{min(vw, 1200)}" height="{min(vh, 700)}">
      {svg_content}
    </svg>
  </div>
  <div class="status" id="status">● servidor activo</div>
  <script>
    // Polling: si el servidor baja, cerrar la pestaña
    async function checkHealth() {{
      try {{
        const r = await fetch('/health');
        if (!r.ok) throw new Error();
        document.getElementById('status').textContent = '● servidor activo';
        document.getElementById('status').style.color = '#a6e3a1';
      }} catch(e) {{
        document.getElementById('status').textContent = '○ servidor cerrado';
        document.getElementById('status').style.color = '#f38ba8';
        setTimeout(() => window.close(), 1500);
      }}
    }}
    setInterval(checkHealth, 2000);
  </script>
</body>
</html>"""


class Handler(http.server.BaseHTTPRequestHandler):
    html_cache = ""

    def do_GET(self):
        if self.path == "/health":
            self._respond(200, "application/json", b'{"status":"ok"}')
        elif self.path == "/shutdown":
            self._respond(200, "text/plain", b"cerrando...")
            threading.Thread(target=self._shutdown).start()
        else:
            self._respond(200, "text/html; charset=utf-8", Handler.html_cache.encode())

    def _respond(self, code, ctype, body):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.end_headers()
        self.wfile.write(body)

    def _shutdown(self):
        import time
        time.sleep(0.3)
        os.kill(os.getpid(), signal.SIGTERM)

    def log_message(self, *a):
        pass


def main():
    if len(sys.argv) < 2:
        print("Uso: python3 excalidraw_serve.py <archivo.excalidraw>")
        sys.exit(1)

    path = sys.argv[1]
    if not os.path.exists(path):
        print(f"Archivo no encontrado: {path}")
        sys.exit(1)

    Handler.html_cache = build_html(path)

    server = http.server.HTTPServer(("", PORT), Handler)
    print(f"Servidor activo en http://localhost:{PORT}")
    print(f"Archivo: {path}")
    print("Para cerrar: curl http://localhost:8765/shutdown")

    def handle_sigterm(*_):
        server.server_close()
        sys.exit(0)

    signal.signal(signal.SIGTERM, handle_sigterm)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
