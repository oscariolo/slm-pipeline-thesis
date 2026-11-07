#!/usr/bin/env bash
# Uso: ask.sh <nombre_nota> "<pregunta>"   (guarda la respuesta en notes/<nombre_nota>.md)
N=/home/santiago/Desktop/Santi/universidad/slm-pipeline-thesis/notes
cd /home/santiago/.claude/skills/notebooklm || exit 1
timeout 400 python3 scripts/run.py ask_question.py --question "$2" --notebook-id observabilidad-slm-dtic > "$N/$1.md" 2>&1
echo "$1 rc=$? bytes=$(wc -c < "$N/$1.md")"
