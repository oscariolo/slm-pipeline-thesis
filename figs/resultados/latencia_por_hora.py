"""Figura de la sección 4.5.4: tráfico de logs y tiempo de llenado del lote según la hora del día.

Lee los eventos conservados por el prefiltro (processed_logs.jsonl), los ordena por su marca de
tiempo (hora local del servicio, UTC-5) y los agrupa de 50 en 50, como el ingestor. Panel superior:
eventos promedio por hora según la hora del día. Panel inferior: tiempo de llenado de los lotes
(del primer al evento 50) según la hora en que llegó su primer evento; mediana y rango intercuartílico.

Uso (desde slm-pipeline-thesis/):
  ../Tesis/TesisPipelineDev/scripts/.venv/bin/python figs/resultados/latencia_por_hora.py \
      ../Tesis/TesisPipelineDev/scripts/pseudo_labeling/data/ms_users/processed_logs.jsonl
"""
import json
import statistics
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

N = 50
BLUE, ORANGE, TEXT2, GREY = "#257de0", "#f47230", "#666666", "#ececec"


def main(logs, out_pdf):
    ts = sorted(datetime.fromisoformat(json.loads(l)["timestamp"]) for l in open(logs, encoding="utf-8") if l.strip())
    days = (ts[-1] - ts[0]).total_seconds() / 86400
    per_hour = np.zeros(24)
    for t in ts:
        per_hour[t.hour] += 1
    per_hour /= days
    fills = defaultdict(list)
    week = {"laborable": [], "fin de semana": []}
    for k in range(len(ts) // N):
        first, last = ts[k * N], ts[(k + 1) * N - 1]
        minutes = (last - first).total_seconds() / 60
        fills[first.hour].append(minutes)
        week["fin de semana" if first.weekday() >= 5 else "laborable"].append(minutes)
    hours = np.arange(24)
    med = np.array([np.median(fills[h]) for h in hours])
    q1 = np.array([np.percentile(fills[h], 25) for h in hours])
    q3 = np.array([np.percentile(fills[h], 75) for h in hours])

    plt.rcParams.update({"font.size": 11, "axes.spines.top": False, "axes.spines.right": False})
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6.6), sharex=True, gridspec_kw={"height_ratios": [1, 1.3]})
    for ax in (ax1, ax2):  # horario laboral (8 a 17 h)
        ax.axvspan(7.5, 17.5, color=GREY, alpha=0.5, linewidth=0, zorder=0)
    ax1.bar(hours, per_hour, width=0.8, color=BLUE, zorder=2)
    ax1.set_ylabel("Eventos por hora\n(promedio)")
    ax1.set_title("(a) Tráfico del servicio", loc="left", fontsize=11)
    ax1.grid(axis="y", alpha=0.3)
    ax1.set_axisbelow(True)

    ax2.fill_between(hours, q1, q3, color=ORANGE, alpha=0.2, linewidth=0, zorder=2,
                     label="50 % central de los lotes (percentiles 25 a 75)")
    ax2.plot(hours, med, color=ORANGE, linewidth=2, marker="o", markersize=5, zorder=3, label="Mediana")
    ax2.axhline(50 / (len(ts) / (days * 86400)) / 60, color=TEXT2, linewidth=1, linestyle="--", zorder=2,
                label="Con el ritmo promedio del servicio (0.179 eventos/s)")
    ax2.set_yscale("log")
    ax2.set_yticks([1, 2, 5, 10, 30, 60, 120])
    ax2.set_yticklabels(["1", "2", "5", "10", "30", "60", "120"])
    ax2.minorticks_off()
    ax2.text(12.5, 100, "Horario laboral (8 a 17 h)", ha="center", va="center", fontsize=9, color=TEXT2)
    ax2.set_ylabel("Tiempo de llenado\ndel lote (minutos)")
    ax2.set_title("(b) Tiempo que tarda un lote en reunir sus 50 eventos", loc="left", fontsize=11)
    ax2.set_xlabel("Hora del día en que llega el primer evento del lote")
    ax2.set_xticks(range(0, 24, 2))
    ax2.set_xticklabels([f"{h} h" for h in range(0, 24, 2)])
    ax2.set_xlim(-0.6, 23.6)
    ax2.grid(axis="y", alpha=0.3, which="major")
    ax2.legend(frameon=False, fontsize=9, loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=1)
    fig.tight_layout()
    fig.savefig(out_pdf, bbox_inches="tight")
    fig.savefig(Path(out_pdf).with_suffix(".png"), dpi=130, bbox_inches="tight")
    print("guardado", out_pdf)
    for h in hours:
        print(f"{h:2d}h  {per_hour[h]:7.1f} ev/h  lotes {len(fills[h]):4d}  llenado mediana {med[h]:6.1f} min  IQR {q1[h]:.1f}-{q3[h]:.1f}")
    for k, v in week.items():
        print(k, len(v), "lotes, mediana", round(statistics.median(v), 1), "min")


if __name__ == "__main__":
    out = sys.argv[2] if len(sys.argv) > 2 else str(Path(__file__).with_name("latencia_por_hora.pdf"))
    main(sys.argv[1], out)
