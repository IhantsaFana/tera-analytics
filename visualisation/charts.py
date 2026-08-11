import pandas as pd
import matplotlib.pyplot as plt

from config import seuil_oms
from .common import finaliser, style


def graphique_profil_horaire(profil, mode="show"):
    style()
    fig, ax = plt.subplots()
    ax.plot(profil.index, profil["mean"], marker="o")
    ax.axhline(seuil_oms, color="red", linestyle="--", label=f"OMS ({seuil_oms} µg/m³)")
    ax.set(xlabel="Heure", ylabel="PM2.5 (µg/m³)", title="Cycle diurne — Antananarivo")
    ax.legend()
    fig.tight_layout()
    return finaliser(fig, "profil_horaire", mode)


def graphique_profil_mensuel(profil, mode="show"):
    style()
    mois = ["Jan", "Fév", "Mar", "Avr", "Mai", "Jun", "Jul", "Aoû", "Sep", "Oct", "Nov", "Déc"]
    fig, ax = plt.subplots()
    ax.bar(profil.index, profil["mean"])
    ax.axhline(seuil_oms, color="red", linestyle="--", label=f"OMS ({seuil_oms} µg/m³)")
    ax.set_xticks(profil.index)
    ax.set_xticklabels([mois[i - 1] for i in profil.index])
    ax.set(xlabel="Mois", ylabel="PM2.5 (µg/m³)", title="Variation saisonnière — Antananarivo")
    ax.legend()
    fig.tight_layout()
    return finaliser(fig, "profil_mensuel", mode)


def graphique_capteurs(stats, mode="show"):
    style()
    fig, ax = plt.subplots(figsize=(10, 7))
    labels = stats.index.get_level_values("id_install")
    ax.barh(labels, stats["mean"])
    ax.axvline(seuil_oms, color="red", linestyle="--", label=f"OMS ({seuil_oms} µg/m³)")
    ax.set(xlabel="PM2.5 moyen (µg/m³)", title="Comparaison par capteur")
    ax.legend()
    fig.tight_layout()
    return finaliser(fig, "capteurs", mode)


def graphique_serie_temporelle(moyenne_journaliere, mode="show"):
    style()
    fig, ax = plt.subplots(figsize=(14, 5))
    ax.plot(pd.to_datetime(moyenne_journaliere["date"]), moyenne_journaliere["pm25_mean"], linewidth=0.8)
    ax.axhline(seuil_oms, color="red", linestyle="--", label=f"OMS ({seuil_oms} µg/m³)")
    ax.set(xlabel="Date", ylabel="PM2.5 moyen (µg/m³)", title="Évolution journalière — Antananarivo")
    ax.legend()
    fig.tight_layout()
    return finaliser(fig, "serie_temporelle", mode)
