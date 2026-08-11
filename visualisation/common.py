import os
import subprocess
import sys
from pathlib import Path

import matplotlib

if os.environ.get("DISPLAY") or sys.platform == "win32":
    for backend_name in ("TkAgg", "QtAgg", "MacOSX"):
        try:
            matplotlib.use(backend_name, force=True)
            break
        except Exception:
            continue
else:
    matplotlib.use("Agg", force=True)

import matplotlib.pyplot as plt
import seaborn as sns

from config import dossier_graphiques, seuil_oms


def style():
    sns.set_theme(style="whitegrid")
    plt.rcParams["figure.figsize"] = (12, 6)
    plt.rcParams["axes.titlesize"] = 10
    plt.rcParams["axes.labelsize"] = 9
    plt.rcParams["xtick.labelsize"] = 8
    plt.rcParams["ytick.labelsize"] = 8


def finaliser(fig, nom, mode="show"):
    """Affiche ou exporte la figure selon le mode."""
    chemin = dossier_graphiques / f"{nom}.png"
    chemin.parent.mkdir(parents=True, exist_ok=True)

    fig.savefig(chemin, dpi=200, bbox_inches="tight")

    if mode == "export" or not os.environ.get("DISPLAY"):
        plt.close(fig)
        return chemin

    try:
        plt.show(block=True)
    except Exception:
        try:
            subprocess.run(["xdg-open", str(chemin)], check=False)
        except Exception:
            fig.savefig(chemin, dpi=200, bbox_inches="tight")
    finally:
        plt.close(fig)

    return chemin
