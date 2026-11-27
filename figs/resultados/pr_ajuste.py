"""Figura de la sección 4.4: curvas de precisión-recall de Qwen3.5-9B base y ajustado en los lotes de prueba.

Lee analysis/finetune/test_split/runs/{base,lora}/eval_report.json (curvas y AP) y los puntos de
operación de las cuatro variantes de la tabla tab:res_ajuste (base, base con umbral, ajustado y
ajustado con umbral; umbrales en thresholds.json).

Uso (desde slm-pipeline-thesis/):
  ../Tesis/scripts/.venv/bin/python figs/resultados/pr_ajuste.py [../Tesis/scripts]
"""
import json

from _estilo import GREY, OI, SCRIPTS, plt, save, setup

SPLIT = SCRIPTS / "analysis/finetune/test_split"


def report(name):
    return json.loads((SPLIT / "runs" / name / "eval_report.json").read_text())


def main():
    setup()
    thr = json.loads((SPLIT / "thresholds.json").read_text())
    fig, ax = plt.subplots(figsize=(5.2, 3.9))
    for name, label, color in [("base", "Base", OI[0]), ("lora", "Ajustado", OI[1])]:
        rep = report(name)
        assert rep["total_samples"] == 892, rep["total_samples"]
        pr = rep["pr_curve"]
        ax.plot(pr["recall"], pr["precision"], color=color, lw=1.5, drawstyle="steps-post",
                label=f"{label} (AP {rep['average_precision']:.3f})")
        direct, cut = rep, report(f"{name}__thr")
        ax.plot(direct["recall"], direct["precision"], "o", color=color, ms=6, mec="black", mew=0.6,
                label=f"{label}: respuesta directa")
        ax.plot(cut["recall"], cut["precision"], "D", color=color, ms=5.5, mfc="white", mew=1.4,
                label=f"{label}: umbral {thr[name]['threshold']:.3f}")
        print(name, "AP", round(rep["average_precision"], 3), "directa P/R", round(direct["precision"], 3),
              round(direct["recall"], 3), "umbral P/R", round(cut["precision"], 3), round(cut["recall"], 3))
    base = 29 / 892
    ax.axhline(base, color=GREY, ls="--", lw=1, label=f"Clasificador al azar ({base:.3f})")
    ax.set_xlim(0, 1.02)
    ax.set_ylim(0, 1.04)
    ax.set_xlabel("Recall")
    ax.set_ylabel("Precisión")
    ax.grid(alpha=0.25, lw=0.5)
    ax.legend(loc="lower left", frameon=False)
    save(fig, "pr_ajuste")


if __name__ == "__main__":
    main()
