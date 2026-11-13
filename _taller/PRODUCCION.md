# Producción diaria del contenido (tarea automática de las 6:13 a. m.)

**Meta:** antes de las **8:00 a. m. (America/Caracas)** la carpeta `contenido/` tiene el contenido NUEVO de hoy:
`video.mp4` · `flyer1.jpg` · `flyer2.jpg` · `flyer3.jpg` · `texto.txt` (mismos nombres; reemplazan a los de ayer).
**Estándar:** que parezca hecho por un diseñador profesional de la marca, distinto a los días anteriores y útil para el cliente.

## 1. Plan del día (obligatorio)
```bash
python3 _taller/plan_del_dia.py            # imprime el brief de hoy (no guarda)
```
El plan decide, rotando lo que hace más tiempo no se usa:
- **Video:** ángulo (tema), estilo de animación (10 estilos) y duración sugerida.
- **Música:** estilo (`electro` · `dembow` · `gaitera` · `lofi` · `house` · `trap`), bpm, tono y semilla.
- **3 flyers:** ángulo, layout (12 layouts) y paleta (6 paletas), cada uno de un grupo distinto.
- **Tono** del copy y **fecha especial** si la hay (Navidad, Día de la Madre, Feria en el Zulia, Día del Internet, etc.).
Síguelo. Puedes cambiar UN elemento si hay una razón de calidad clara (anótalo en el historial).

## 2. Escribir las piezas en `_taller/hoy/` (carpeta ignorada por git)
Cada HTML empieza así (rutas relativas a `_taller/hoy/`):
```html
<link rel="stylesheet" href="../base.css"><script src="../marca.js"></script>
```
- `base.css`: colores, degradados, tipografía (`.t-xxl … .t-eti`), `.tarjeta`, `.pill`, `.seguro`.
- `marca.js` → `GN.marca(tema)`, `GN.logo(px)`, `GN.legal(tema, y)`, `GN.contacto("atencion"|"soporte")`, `GN.waIcono()`, `GN.hilos({...})`, `GN.DATOS` (todos los datos oficiales: úsalos en vez de escribirlos a mano) y ayudas de video (`GN.prog`, `GN.eOut`, `GN.eBack`, `GN.entra`, `GN.pop`, `GN.escribir`, `GN.contar`).
- Ejemplos de calidad en `ejemplo/` (flyers: número gigante, lista de pasos, burbujas; video: hilo de luz + conteo). Son **referencia técnica y de nivel**, no plantillas: el diseño de hoy debe ser otro.

### Video (`hoy/video.html`, 12–15 s, 1080×1920, 30 fps)
- `window.render(t)` dibuja el cuadro exacto del segundo `t` (nada de animaciones CSS ni `setTimeout`).
- Estructura: **gancho en el primer segundo** → 2–3 escenas de desarrollo → cierre con `GN.contacto(...)` y logo. RIF/CONATEL (`GN.legal`) visibles en **todas** las escenas.
- Movimiento con intención: entradas con easing, nada estático más de 1,5 s, transiciones propias del estilo del plan.
- `hoy/pistas.json` con los **tiempos reales** de tu animación (cortes, conteos, pops, deslizes) + `estilo`, `bpm`, `tono`, `semilla` del plan. Alinea los cortes al compás: `intro_hasta + k × 60/bpm`.
```bash
python3 _taller/audio.py _taller/hoy/pistas.json /tmp/audio.wav
bash _taller/hacer_video.sh _taller/hoy/video.html <segundos> /tmp/audio.wav contenido/video.mp4
```
`render_video.mjs` revisa solo cada 0,5 s: textos fuera del lienzo o de la zona segura y RIF/CONATEL presentes. **Corrige todo aviso ⚠.**

### Flyers (`hoy/flyer1.html … flyer3.html`, 1080×1920)
```bash
node _taller/render_flyers.mjs _taller/hoy/flyer1.html _taller/hoy/flyer2.html _taller/hoy/flyer3.html contenido
```
Cada flyer imprime `revisión OK` o los problemas. **Corrige todo aviso ⚠.**

### Texto del estado (`contenido/texto.txt`)
Formato WhatsApp (`*negrita*`, `_cursiva_`), 4–9 líneas, coherente con el tema y el tono del plan. Siempre: los dos WhatsApp y @guajiranetwork.

## 3. Control de calidad (no se publica sin pasarlo)
Arma una hoja de contacto (3 flyers + 6 cuadros del video) y mírala con Read:
```bash
for t in 0.8 2.5 4.5 7 10 12; do ffmpeg -loglevel error -y -ss $t -i contenido/video.mp4 -frames:v 1 /tmp/c_$t.png; done
python3 -c "from PIL import Image; import glob; ims=[Image.open(f).resize((270,480)) for f in sorted(glob.glob('contenido/flyer*.jpg'))+sorted(glob.glob('/tmp/c_*.png'))]; c=Image.new('RGB',(270*len(ims),480)); [c.paste(im,(i*270,0)) for i,im in enumerate(ims)]; c.save('/tmp/hoja.png')"
```
Puntúa cada pieza de 1 a 5 y **rehaz la que saque menos de 4** en cualquier punto:
1. **Una idea** clara que se entiende en 2 segundos.
2. **Jerarquía**: lo más importante es lo más grande; máximo ~20 palabras visibles.
3. **Marca**: logo exacto, paleta, Poppins, hilo de fibra usado con gusto.
4. **Datos exactos** (solo MARCA.md) y **ortografía** perfecta (tildes, ¿¡ !?).
5. **Legal**: RIF y CONATEL legibles; nada fuera de la zona segura (y 220–1700).
6. **Distinto** a los últimos 7 días (mira `historial.md`): otro layout, otra composición, otro gancho.
7. **Video**: ritmo (algo pasa cada 0,5–1,5 s), sonido sincronizado con los movimientos, final limpio.

## 4. Publicar
```bash
python3 _taller/plan_del_dia.py --guardar      # registra lo usado (alimenta la rotación)
```
Agrega la fila de hoy al inicio de `historial.md` (temas, estilo de video, música, layouts y una nota de lo que funcionó).
```bash
git add contenido _taller/historial.md _taller/plan_usado.json
git commit -m "Contenido del AAAA-MM-DD" && git -c push.negotiate=true push origin main
```
Si algo no se puede producir con calidad, **no subas nada roto**: deja lo de ayer y explica qué falló.
