#!/usr/bin/env bash
# Uso: bash hacer_video.sh <anim.html> <segundos> <audio.wav> <salida.mp4>
set -e
TMP=$(mktemp -d)
node "$(dirname "$0")/render_video.mjs" "$1" "$2" "$TMP/fr"
ffmpeg -loglevel error -y -framerate 30 -i "$TMP/fr/%04d.png" -i "$3" -c:v libx264 -preset medium -crf 16 -profile:v high -pix_fmt yuv420p -c:a aac -b:a 256k -ar 48000 -shortest -movflags +faststart "$4"
rm -rf "$TMP"; ls -la "$4"
