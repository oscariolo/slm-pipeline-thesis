"""Figura de la sección 4.5.1: detección y falsas alarmas frente a la proporción de lotes enviados al SLM.

Lee report/summary.csv del experimento de simulación (modo de velocidad máxima, 18 configuraciones
por modelo). Columnas: modelo base y ajustado; filas: incidentes detectados (de 216) y falsas
alarmas. Un punto por configuración, con color por método y el SLM solo como referencia en 100 %.

Uso (desde slm-pipeline-thesis/):
  ../Tesis/scripts/.venv/bin/python figs/resultados/sim_tradeoff.py [../Tesis/scripts]
"""
import csv

from _estilo import APPROACH, SCRIPTS, plt, save, setup

SUMMARY = SCRIPTS / "analysis/experiments/qwen35_stream_qwen3emb06b_batchinj/report/summary.csv"
MODELS = [("qwen35", "Modelo base"), ("qwen35_logft", "Modelo ajustado")]


def load():
    with open(SUMMARY, encoding="utf-8") as f:
        rows = [r for r in csv.DictReader(f) if r["mode"] == "throughput"]
    for model, _ in MODELS:
        n = sum(r["model"] == model for r in rows)
        assert n == 18, (model, n)
    return rows


def main():
    setup()
    rows = load()
    fig, axes = plt.subplots(2, 2, figsize=(6.3, 5.0), sharex=True, sharey="row")
    for col, (model, title) in enumerate(MODELS):
        sel = [r for r in rows if r["model"] == model]
        for row, (key, ylabel) in enumerate([("detected", "Incidentes detectados (de 216)"),
                                             ("fp", "Falsas alarmas")]):
            ax = axes[row][col]
            for approach, (label, color, marker) in APPROACH.items():
                pts = [r for r in sel if r["approach"] == approach]
                xs = [100 * float(r["slm_share"]) for r in pts]
                ys = [int(r[key]) for r in pts]
                ax.scatter(xs, ys, color=color, marker=marker, s=60 if approach == "slm" else 22,
                           edgecolor="black" if approach == "slm" else "none", lw=0.5, label=label, zorder=3)
                if approach in ("batch", "event"):  # une los umbrales de un mismo método
                    xy = sorted(zip(xs, ys))
                    ax.plot([p[0] for p in xy], [p[1] for p in xy], color=color, lw=0.8, alpha=0.6, zorder=2)
            ax.grid(alpha=0.25, lw=0.5)
            if row == 0:
                ax.set_title(title)
            else:
                ax.set_xlabel("Lotes enviados al SLM (%)")
            if col == 0:
                ax.set_ylabel(ylabel)
    axes[0][0].set_xlim(-3, 105)
    handles, labels = axes[0][0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=4, frameon=False, bbox_to_anchor=(0.5, -0.01))
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    save(fig, "sim_tradeoff")
    for r in rows:
        print(r["model"], r["config"], r["detected"], r["fp"], f"{100 * float(r['slm_share']):.1f}")


if __name__ == "__main__":
    main()
