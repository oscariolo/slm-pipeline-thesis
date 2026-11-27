"""Figura de la sección 4.3: kappa de Cohen de cada modelo con N = 30 y N = 20 frente a sus respuestas con N = 50.

Lee chance.csv de analysis/significance/self_consistency__n30 y __n20 (kappa y su IC del 95 %).
Un renglón por modelo, ordenado por el kappa con N = 30; línea vertical en kappa = 0 (azar).

Uso (desde slm-pipeline-thesis/):
  ../Tesis/scripts/.venv/bin/python figs/resultados/kappa_consistencia.py [../Tesis/scripts]
"""
import csv

from _estilo import GREY, MODEL_NAMES, OI, SCRIPTS, plt, save, setup

SIG = SCRIPTS / "analysis/significance"


def load(n):
    with open(SIG / f"self_consistency__n{n}" / "chance.csv", encoding="utf-8") as f:
        return {MODEL_NAMES[r["model"]]: (float(r["kappa"]), float(r["kappa_ci_low"]), float(r["kappa_ci_high"]),
                                          r["significant"] == "True") for r in csv.DictReader(f)}


def main():
    setup()
    k30, k20 = load(30), load(20)
    order = sorted(k30, key=lambda m: k30[m][0])  # de abajo hacia arriba
    fig, ax = plt.subplots(figsize=(6.3, 3.4))
    for offset, data, color, marker, label in [(0.15, k30, OI[0], "o", "$N = 30$"), (-0.15, k20, OI[1], "s", "$N = 20$")]:
        for i, m in enumerate(order):
            k, lo, hi, sig = data[m]
            ax.errorbar(k, i + offset, xerr=[[k - lo], [hi - k]], fmt=marker, color=color, ms=4.5, lw=1.1,
                        capsize=2.5, mfc=color if sig else "white", label=None)
    ax.axvline(0, color=GREY, ls="--", lw=1)
    ax.set_yticks(range(len(order)), order)
    ax.set_xlabel("Kappa de Cohen frente a la respuesta del mismo modelo con $N = 50$ (IC 95 %)")
    ax.grid(axis="x", alpha=0.25, lw=0.5)
    from matplotlib.lines import Line2D
    handles = [Line2D([], [], color=OI[0], marker="o", ls="", label="$N = 30$"),
               Line2D([], [], color=OI[1], marker="s", ls="", label="$N = 20$"),
               Line2D([], [], color=GREY, marker="o", mfc="white", ls="", label="no supera al azar (Holm)")]
    ax.legend(handles=handles, loc="lower right", frameon=False)
    save(fig, "kappa_consistencia")
    for m in reversed(order):
        print(f"{m:28s} n30 {k30[m][0]:.3f} [{k30[m][1]:.3f}, {k30[m][2]:.3f}] sig={k30[m][3]}   "
              f"n20 {k20[m][0]:.3f} [{k20[m][1]:.3f}, {k20[m][2]:.3f}] sig={k20[m][3]}")


if __name__ == "__main__":
    main()
