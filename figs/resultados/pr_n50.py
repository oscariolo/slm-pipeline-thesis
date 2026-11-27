"""Figura de la sección 4.1: curvas de precisión-recall de los ocho SLM con N = 50.

Lee eval_invalid_as_wrong/eval_report.json de cada modelo (lotes fallidos contados como fallos, igual
que la tabla tab:res_n50) y superpone las curvas, con la AP y el MCC de cada modelo en la leyenda.

Uso (desde slm-pipeline-thesis/):
  ../Tesis/scripts/.venv/bin/python figs/resultados/pr_n50.py [../Tesis/scripts]
"""
import json

from _estilo import GREY, MODEL_COLORS, MODEL_NAMES, SCRIPTS, plt, save, setup

N50 = SCRIPTS / "analysis/batch_size_matrix/n50"


def main():
    setup()
    rows = []
    for folder, name in MODEL_NAMES.items():
        rep = json.loads((N50 / folder / "eval_invalid_as_wrong" / "eval_report.json").read_text())
        assert rep["total_samples"] == 4463, (name, rep["total_samples"])
        rows.append((name, rep))
    rows.sort(key=lambda r: -r[1]["matthews_corrcoef"])  # mismo orden que la tabla

    fig, ax = plt.subplots(figsize=(6.3, 3.6))
    for name, rep in rows:
        pr = rep["pr_curve"]
        ax.plot(pr["recall"], pr["precision"], color=MODEL_COLORS[name], lw=1.4,
                drawstyle="steps-post",
                label=f"{name} (AP {rep['average_precision']:.3f}; MCC {rep['matthews_corrcoef']:.3f})")
    base = 130 / 4463
    ax.axhline(base, color=GREY, ls="--", lw=1, label=f"Clasificador al azar ({base:.3f})")
    ax.set_xlim(0, 1.0)
    ax.set_ylim(0, 1.02)
    ax.set_xlabel("Recall")
    ax.set_ylabel("Precisión")
    ax.grid(alpha=0.25, lw=0.5)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.15), ncol=2, frameon=False)
    save(fig, "pr_n50")


if __name__ == "__main__":
    main()
