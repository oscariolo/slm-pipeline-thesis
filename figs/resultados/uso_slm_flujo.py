"""Figura de la sección 4.5.3: uso del SLM a lo largo del flujo.

Lee growth.csv (generado por simulation/analyze_experiment.py) y grafica, por ventanas de
200 lotes, el porcentaje de lotes enviados al SLM frente a los lotes procesados, con un
panel por modelo (base y ajustado).

Uso (desde slm-pipeline-thesis/):
  ../Tesis/TesisPipelineDev/scripts/.venv/bin/python figs/resultados/uso_slm_flujo.py \
      ../Tesis/TesisPipelineDev/scripts/analysis/experiments/qwen35_stream_qwen3emb06b_batchinj/report/growth.csv
"""
import csv
import sys
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SERIES = [  # (config en growth.csv, etiqueta, color, estilo)
    ("slm", "SLM solo", "#000000", ":"),
    ("batch:0.99", "Caché por lote 0.99", "#1f77b4", "-"),
    ("event:exact", "Caché por evento exacta", "#d62728", "--"),
    ("event:0.97", "Caché por evento 0.97", "#2ca02c", "-"),
    ("event:0.85", "Caché por evento 0.85", "#9467bd", "-"),
    ("fastpath:0.99", "Vía rápida 0.99", "#8c564b", "-."),
]
MODELS = [("qwen35", "Modelo base"), ("qwen35_logft", "Modelo ajustado")]


def load(path):
    data = defaultdict(list)  # (model, config) -> [(lotes procesados, % al SLM)]
    with open(path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            end = int(row["first_batch"]) + int(row["batches"])
            data[(row["model"], row["config"])].append((end, 100 * float(row["slm_share"])))
    for key in data:
        data[key].sort()
    return data


def main(growth_csv, out_pdf):
    data = load(growth_csv)
    plt.rcParams.update({"font.size": 11})
    fig, axes = plt.subplots(1, 2, figsize=(9, 4.2), sharey=True)
    for ax, (model, title) in zip(axes, MODELS):
        for config, label, color, style in SERIES:
            pts = data.get((model, config))
            if not pts:
                raise SystemExit(f"Falta {model} / {config} en {growth_csv}")
            xs, ys = zip(*pts)
            ax.plot(xs, ys, style, color=color, label=label, marker="o", markersize=2.5, linewidth=1.3)
        ax.set_title(title)
        ax.set_xlabel("Lotes procesados")
        ax.set_ylim(0, 105)
        ax.grid(alpha=0.3)
    axes[0].set_ylabel("Lotes enviados al SLM en la ventana (%)")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=3, frameon=False, bbox_to_anchor=(0.5, -0.02))
    fig.tight_layout(rect=(0, 0.12, 1, 1))
    fig.savefig(out_pdf, bbox_inches="tight")
    print("guardado", out_pdf)


if __name__ == "__main__":
    growth = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else str(Path(__file__).with_name("uso_slm_flujo.pdf"))
    main(growth, out)
