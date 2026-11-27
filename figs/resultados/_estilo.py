"""Estilo común de las figuras de resultados (tamaño real para \\textwidth ≈ 6.3 in) y rutas del proyecto."""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

THESIS = Path(__file__).resolve().parents[2]
SCRIPTS = Path(sys.argv[1]) if len(sys.argv) > 1 else THESIS.parent / "Tesis" / "scripts"
OUT_DIR = Path(__file__).resolve().parent

# Okabe-Ito (seguro para daltonismo)
OI = ["#0072B2", "#D55E00", "#009E73", "#CC79A7", "#E69F00", "#56B4E9", "#999933", "#000000"]  # amarillo -> oliva (contraste)
GREY = "#8c8c8c"

MODEL_NAMES = {
    "hf.co-unsloth-Qwen3.5-9B-GGUF-Q6_K": "Qwen3.5-9B",
    "ibm-granite-granite-4.1-3b": "Granite-4.1-3B",
    "microsoft-Phi-3.5-mini-instruct": "Phi-3.5-mini",
    "google-gemma-3-4b-it": "Gemma-3-4B",
    "hf.co-inclusionAI-Ling-3.0-tiny-GGUF-Q4_K_M": "Ling-3.0-tiny",
    "hf.co-mistralai-Ministral-3-3B-Instruct-2512-GGUF-BF16": "Ministral-3-3B",
    "hf.co-mradermacher-llama-3.2-1B-log-analyzer-GGUF-Q4_K_M": "Llama-3.2-1B log-analyzer",
    "HuggingFaceTB-SmolLM2-1.7B-Instruct": "SmolLM2-1.7B-Instruct",
}
# Un color fijo por modelo en todas las figuras
MODEL_COLORS = dict(zip(MODEL_NAMES.values(), OI))

APPROACH = {  # enfoque de caché -> (etiqueta, color, marcador)
    "slm": ("SLM solo", "#000000", "*"),
    "batch": ("Caché por lote", OI[0], "o"),
    "event": ("Caché por evento", OI[2], "s"),
    "fastpath": ("Vía rápida", OI[1], "^"),
}


def setup():
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Arimo", "Liberation Sans", "Arial", "DejaVu Sans"],
        "font.size": 9,
        "axes.titlesize": 9.5,
        "axes.labelsize": 9,
        "legend.fontsize": 7.5,
        "xtick.labelsize": 8,
        "ytick.labelsize": 8,
        "axes.linewidth": 0.8,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "pdf.fonttype": 42,
    })


def save(fig, name):
    path = OUT_DIR / f"{name}.pdf"
    fig.savefig(path, bbox_inches="tight")
    print("guardado", path)
    return path
