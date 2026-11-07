#!/usr/bin/env bash
# Uso:
#   ./run_night.sh test   -> prueba corta (permisos, carpeta externa, NotebookLM)
#   ./run_night.sh        -> corrida completa con reintentos y progreso en vivo
cd "$(dirname "$0")" || exit 1

EXT=/home/santiago/Desktop/Santi/universidad/Tesis/TesisPipelineDev
COMMON=(--add-dir "$EXT" --permission-mode acceptEdits
        --output-format stream-json --verbose --include-partial-messages)

# Muestra en vivo el texto de Claude y las herramientas que usa.
live() {
  jq -rj --unbuffered '
    if .type=="stream_event" and .event.type=="content_block_delta" and .event.delta.type=="text_delta"
      then .event.delta.text
    elif .type=="stream_event" and .event.type=="content_block_start" and .event.content_block.type=="tool_use"
      then "\n\u001b[36m[herramienta: \(.event.content_block.name)]\u001b[0m\n"
    elif .type=="result" then "\n\n=== FIN: \(.subtype) ===\n"
    else empty end'
}

if [ "$1" = "test" ]; then
  claude -p "PRUEBA CORTA, no escribas capítulos. 1) Lee $EXT/ThesisSources/MainObjectives.txt y resume el objetivo general en una línea. 2) Usa el skill notebooklm (notebook 'Observabilidad SLM DTIC'; usa python3, no existe 'python') y haz UNA pregunta corta: 'Resume en 3 líneas de qué trata este notebook'. 3) Crea notes/test.md con ambas respuestas. 4) Ejecuta 'latexmk -pdf -interaction=nonstopmode TFG.tex' y dime si compiló. 5) Intenta escribir un archivo en $EXT/test_no_debe_existir.txt (debe ser DENEGADO; confírmalo)." \
    "${COMMON[@]}" | live
  exit 0
fi

claude -p "$(cat PROMPT.md)" "${COMMON[@]}" | live

until grep -q "TESIS COMPLETA" PROGRESS.md 2>/dev/null; do
  echo -e "\n[$(date +%H:%M)] No terminó (¿límite de uso?). Reintento en 30 min..."
  sleep 1800
  claude -p --continue "Lee PROGRESS.md y continúa con el siguiente capítulo pendiente, siguiendo las reglas del prompt original. Cuando todo esté terminado escribe TESIS COMPLETA en PROGRESS.md." \
    "${COMMON[@]}" | live
done
echo "Listo: TESIS COMPLETA."
