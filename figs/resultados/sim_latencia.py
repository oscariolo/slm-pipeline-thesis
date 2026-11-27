"""Figura de la sección 4.5.4: latencia mediana de detección en función del ritmo de llegada.

Recalcula el modelo de colas de simulation/analyze_experiment.py sobre las ejecuciones en modo de
velocidad máxima, con cada tiempo de proceso limitado a 30 s (sección 3.8.4: excluye la pausa de
unas tres horas del equipo del modelo base). Un panel por modelo, una línea por método; los ritmos
inestables (tiempo medio de proceso mayor que el intervalo entre lotes) se marcan con una cruz.

Uso (desde slm-pipeline-thesis/):
  ../Tesis/scripts/.venv/bin/python figs/resultados/sim_latencia.py [../Tesis/scripts]
"""
import statistics
import sys

from _estilo import OI, SCRIPTS, plt, save, setup

sys.path.insert(0, str(SCRIPTS))
import simulation.analyze_experiment as ae  # noqa: E402

EXP = SCRIPTS / "analysis/experiments/qwen35_stream_qwen3emb06b_batchinj"
CAP_S = 30.0
RATES = [5, 10, 20, 30]
MODELS = [("qwen35", "Modelo base"), ("qwen35_logft", "Modelo ajustado")]
SERIES = [  # (carpeta de la ejecución, etiqueta, color, estilo)
    ("slm", "SLM solo", "#000000", ":"),
    ("batch_0.99", "Caché por lote 0.99", OI[0], "-"),
    ("event_exact", "Caché por evento exacta", OI[3], "--"),
    ("event_0.97", "Caché por evento 0.97", OI[2], "-"),
    ("event_0.85", "Caché por evento 0.85", OI[5], "-"),
    ("fastpath_0.99", "Vía rápida 0.99", OI[1], "-."),
]

_raw_service = ae.service_time


def capped_service(batch):
    s = _raw_service(batch)
    return None if s is None else min(s, CAP_S)


ae.service_time = capped_service  # queue_model_latencies usa esta función del módulo


def main():
    setup()
    fig, axes = plt.subplots(1, 2, figsize=(6.3, 3.3), sharey=True)
    for ax, (model, title) in zip(axes, MODELS):
        for run_name, label, color, style in SERIES:
            run = ae.load_run(EXP / model / run_name)
            xs, ys, unstable = [], [], []
            for rate in RATES:
                lat, _, stable = ae.queue_model_latencies(run, float(rate))
                med = statistics.median(lat)
                xs.append(rate)
                ys.append(med)
                if not stable:
                    unstable.append((rate, med))
            ax.plot(xs, ys, style, color=color, lw=2.4 if run_name == "event_0.97" else 1.3,
                    marker="s" if run_name == "event_0.97" else "o", ms=4.5 if run_name == "event_0.97" else 3, label=label)
            if unstable:
                ax.plot(*zip(*unstable), "x", color=color, ms=7, mew=1.6)
            print(model, run_name, " ".join(f"{x}:{y:.1f}{'*' if (x, y) in unstable else ''}" for x, y in zip(xs, ys)))
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xticks(RATES, [str(r) for r in RATES])
        ax.minorticks_off()
        ax.set_title(title)
        ax.set_xlabel("Ritmo de llegada (eventos/s)")
        ax.grid(alpha=0.25, lw=0.5, which="major")
    axes[0].set_ylabel("Latencia mediana de detección (s)")
    axes[0].plot([], [], "x", color="black", ms=7, mew=1.6, label="Ritmo inestable (cola creciente)")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=3, frameon=False, bbox_to_anchor=(0.5, -0.02))
    fig.tight_layout(rect=(0, 0.14, 1, 1))
    save(fig, "sim_latencia")


if __name__ == "__main__":
    main()
