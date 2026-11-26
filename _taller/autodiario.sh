#!/usr/bin/env bash
set -euo pipefail
export HOME=/home/ubuntu
export PATH=/usr/local/bin:/usr/bin:/bin:/usr/local/sbin:/usr/sbin:/sbin
export NODE_PATH=/home/ubuntu/.node-global/node_modules
export TZ=America/Caracas
REPO=/home/ubuntu/proyectos/guajiranetwork.contenido
PROMPT="$REPO/_taller/prompt-diario.md"
LOG=/home/ubuntu/proyectos/logs/contenido-diario.log
mkdir -p "$(dirname "$LOG")"
exec 9>/tmp/gn-contenido-diario.lock
flock -n 9 || { echo "$(date -Is) ya hay una ejecucion en curso" >> "$LOG"; exit 0; }
cd "$REPO"
git checkout -q main
git pull -q --rebase origin main
echo "$(date -Is) inicio" >> "$LOG"
set +e
opencode run --auto --dir "$REPO" --model build/big-pickle --title "Contenido diario GN $(date +%F)" -f "$PROMPT" -- "Ejecuta el contenido diario de hoy siguiendo el archivo adjunto. No hagas preguntas." >> "$LOG" 2>&1
rc=$?
set -e
echo "$(date -Is) fin rc=$rc" >> "$LOG"
exit "$rc"
