# Producción diaria del contenido (para la tarea automática de las 6 a. m.)

Meta: antes de las **8:00 a. m. (America/Caracas)** la carpeta `contenido/` del repositorio debe tener el contenido NUEVO de hoy:
`video.mp4` · `flyer1.jpg` · `flyer2.jpg` · `flyer3.jpg` · `texto.txt`
(se reemplazan los de ayer con los mismos nombres; la app los muestra sola).

## Pasos
1. Leer `MARCA.md` (datos y reglas) y `historial.md` (lo que ya se hizo; NO repetir tema ni diseño de los últimos 7 días).
2. Elegir el tema del día: 1 para el video + 3 distintos para los flyers. Si hoy es día 1–3 del mes, uno de los flyers puede ser recordatorio de pago. Si hay una fecha especial real cercana, se puede usar.
3. **Video** (12–15 s, 1080×1920, 30 fps):
   - Escribir un HTML nuevo (`/tmp/dia/video.html`) que exponga `window.render(t)` y dibuje el cuadro exacto para el segundo `t` (sin animaciones CSS: todo calculado desde `t`). Ver `ejemplo/video-anim.html` como referencia técnica, pero el diseño, el ritmo, las transiciones y el texto deben ser **nuevos cada día**.
   - 3–5 escenas, logo exacto, RIF y CONATEL visibles en todas, cierre con los WhatsApp.
   - Escribir `/tmp/dia/pistas.json` con los tiempos reales de los cortes, conteos, pops y entradas (ver cabecera de `audio.py`); `semilla` = fecha AAAAMMDD; variar `tono` y `bpm`.
   - `python3 _taller/audio.py /tmp/dia/pistas.json /tmp/dia/audio.wav`
   - `bash _taller/hacer_video.sh /tmp/dia/video.html <segundos> /tmp/dia/audio.wav contenido/video.mp4`
   - Revisar 4–5 cuadros (`ffmpeg -ss T -i contenido/video.mp4 -frames:v 1 x.png` y mirarlos): textos completos, nada cortado, legal legible.
4. **Flyers**: escribir 3 HTML nuevos de 1080×1920 (`/tmp/dia/flyer1.html` …), con diseños distintos entre sí y distintos a los de días anteriores (`ejemplo/flyer*.html` solo como referencia técnica).
   - `node _taller/render_flyers.mjs /tmp/dia/flyer1.html /tmp/dia/flyer2.html /tmp/dia/flyer3.html contenido`
   - Mirar los 3 JPG: ortografía, datos exactos, logo, RIF y CONATEL, nada fuera de la zona segura.
5. **texto.txt**: texto para la descripción del estado, coherente con el tema del día (formato WhatsApp: `*negrita*`, `_cursiva_`), siempre con las dos líneas de WhatsApp y @guajiranetwork.
6. Agregar una línea al inicio de la tabla de `historial.md` con la fecha y los temas/estilos usados.
7. Commit y push a `main` (GitHub Pages publica desde `main`):
   `git add -A && git commit -m "Contenido del AAAA-MM-DD" && git -c push.negotiate=true push origin main`
8. Si algo falla y no se puede producir contenido correcto, NO subir nada roto: dejar el de ayer y avisar.

## Herramientas
- `render_video.mjs` — HTML con `render(t)` → cuadros PNG (Chrome headless, `/usr/bin/google-chrome`).
- `hacer_video.sh` — cuadros + audio → MP4 H.264 CRF 16 + AAC 256k (máxima calidad).
- `audio.py` — música y efectos sintetizados, sin voz, sincronizados con `pistas.json`.
- `render_flyers.mjs` — 3 HTML → `flyer1.jpg … flyer3.jpg` (JPG calidad 95).
- La carpeta `_taller/` no se publica en la web (GitHub Pages ignora las carpetas que empiezan con `_`).
