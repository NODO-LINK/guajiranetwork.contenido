# Guajira Network · Centro de Contenido (sin Firebase)

## Instalar (una sola vez)
1. Este repositorio ya tiene todo instalado:
   ```
   (raíz del repositorio)
   ├── index.html
   ├── manifest.json
   ├── sw.js
   ├── icons/
   └── contenido/
       ├── video.mp4
       ├── flyer1.jpg
       ├── flyer2.jpg
       ├── flyer3.jpg
       └── texto.txt   (opcional)
   ```
2. La app está en **https://nodo-link.github.io/guajiranetwork.contenido/**
3. APK: entra a **pwabuilder.com**, pega esa dirección → *Package for stores* → *Android* → descarga e instala el `.apk` en el teléfono del gestor.

## Cada día (2 minutos)
1. En GitHub abre la carpeta `contenido/` → **Add file → Upload files**.
2. Arrastra el video y los 3 flyers **con estos nombres exactos**: `video.mp4`, `flyer1.jpg`, `flyer2.jpg`, `flyer3.jpg` (los flyers también pueden ser `.png`).
3. **Commit changes.** GitHub reemplaza los archivos de ayer por los de hoy, así no se acumulan. En 1 o 2 minutos el gestor los ve al abrir la app o tocar ↻.

- Si quieres cambiar el texto de los estados, edita `texto.txt`. Funcionan `*negrita*` y `_cursiva_` como en WhatsApp.
- GitHub web acepta archivos de hasta **25 MB** cada uno. Un video de estado de 30 a 60 s en 1080×1920 entra sin problema.
- Si no subes nada, la app le avisa al gestor que el contenido de hoy todavía no llega.

## Calidad
La app descarga y comparte **el archivo original, byte por byte, sin recomprimir**. Al publicar el estado, el gestor debe tocar el botón **HD** de WhatsApp (arriba, en la pantalla de edición) para que WhatsApp no lo comprima.
