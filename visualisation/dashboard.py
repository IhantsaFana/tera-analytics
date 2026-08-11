import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import numpy as np

from config import seuil_oms
from .common import finaliser, style


def graphique_dashboard(df, stats, moyenne_journaliere, mode="show"):
    """Construit un dashboard riche avec plusieurs graphiques explicatifs."""
    style()
    profil_horaire_df = df.groupby("hour")["pm25"].agg(["mean", "std"]).round(2)
    profil_mensuel_df = df.groupby("month")["pm25"].agg(["mean", "std"]).round(2)

    sample = df.sample(n=min(len(df), 50000), random_state=42)
    monthly_exceedance = (
        df.groupby("month")["pm25"]
        .apply(lambda s: (s > seuil_oms).mean() * 100)
        .round(1)
        .rename("pct_au_dessus_oms")
    )
    hourly_exceedance = (
        df.groupby("hour")["pm25"]
        .apply(lambda s: (s > seuil_oms).mean() * 100)
        .round(1)
    )
    peak_hour = profil_horaire_df["mean"].idxmax()
    peak_hour_value = profil_horaire_df.loc[peak_hour, "mean"]
    peak_month = profil_mensuel_df["mean"].idxmax()
    peak_month_value = profil_mensuel_df.loc[peak_month, "mean"]
    daily_exceedance_pct = (moyenne_journaliere["pm25_mean"] > seuil_oms).mean() * 100
    percentile_95 = np.percentile(sample["pm25"], 95)

    fig = plt.figure(figsize=(22, 15))
    fig.suptitle("Dashboard qualité de l'air — Antananarivo", fontsize=18, fontweight="bold")

    fig.text(
        0.5,
        0.965,
        (
            "Analyse clé\n"
            f"• Moyenne PM2.5 : {round(df['pm25'].mean(), 2)} µg/m³\n"
            f"• Seuil OMS dépassé sur {daily_exceedance_pct:.1f}% des jours\n"
            f"• Pic de pollution à {peak_hour}h ({peak_hour_value:.1f} µg/m³)\n"
            f"• Mois le plus pollué : {['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun', 'Jul', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc'][peak_month - 1]} ({peak_month_value:.1f} µg/m³)"
        ),
        ha="center",
        va="top",
        fontsize=10.5,
        linespacing=1.4,
        bbox={"boxstyle": "round", "facecolor": "#f7f7f7", "edgecolor": "#cccccc", "pad": 0.6},
    )

    gs = fig.add_gridspec(3, 3, hspace=0.35, wspace=0.22)

    ax = fig.add_subplot(gs[0, 0])
    ax.plot(profil_horaire_df.index, profil_horaire_df["mean"], marker="o", color="#1f77b4")
    ax.axhline(seuil_oms, color="red", linestyle="--", label=f"OMS ({seuil_oms} µg/m³)")
    ax.annotate(
        f"Pic à {peak_hour}h",
        xy=(peak_hour, peak_hour_value),
        xytext=(peak_hour + 1.5, peak_hour_value + 2),
        arrowprops=dict(arrowstyle="->", color="black"),
        fontsize=8,
    )
    ax.set(xlabel="Heure", ylabel="PM2.5 (µg/m³)", title="Cycle diurne")
    ax.legend(loc="best")

    ax = fig.add_subplot(gs[0, 1])
    mois = ["Jan", "Fév", "Mar", "Avr", "Mai", "Jun", "Jul", "Aoû", "Sep", "Oct", "Nov", "Déc"]
    ax.bar(profil_mensuel_df.index, profil_mensuel_df["mean"], color="#2ca02c")
    ax.axhline(seuil_oms, color="red", linestyle="--", label=f"OMS ({seuil_oms} µg/m³)")
    ax.set_xticks(profil_mensuel_df.index)
    ax.set_xticklabels([mois[i - 1] for i in profil_mensuel_df.index])
    ax.annotate(
        f"Max : {mois[peak_month - 1]}",
        xy=(peak_month, peak_month_value),
        xytext=(peak_month + 0.2, peak_month_value + 1.5),
        arrowprops=dict(arrowstyle="->", color="black"),
        fontsize=8,
    )
    ax.set(xlabel="Mois", ylabel="PM2.5 (µg/m³)", title="Variation saisonnière")
    ax.legend(loc="best")

    ax = fig.add_subplot(gs[0, 2])
    ax.plot(pd.to_datetime(moyenne_journaliere["date"]), moyenne_journaliere["pm25_mean"], linewidth=0.8, color="#d62728")
    ax.axhline(seuil_oms, color="red", linestyle="--", label=f"OMS ({seuil_oms} µg/m³)")
    ax.set(xlabel="Date", ylabel="PM2.5 moyen (µg/m³)", title="Évolution journalière")
    ax.legend(loc="best")

    ax = fig.add_subplot(gs[1, 0])
    top_capteurs = stats.head(8).copy()
    labels = [f"{sensor_id} ({install_id})" for sensor_id, install_id in top_capteurs.index]
    ax.barh(labels, top_capteurs["mean"], color="#ff7f0e")
    ax.axvline(seuil_oms, color="red", linestyle="--", label=f"OMS ({seuil_oms} µg/m³)")
    ax.set(xlabel="PM2.5 moyen (µg/m³)", title="Top capteurs les plus pollués")
    ax.legend(loc="best")

    ax = fig.add_subplot(gs[1, 1])
    ax.hist(sample["pm25"], bins=40, color="#9467bd", edgecolor="black", alpha=0.8)
    ax.axvline(df["pm25"].mean(), color="black", linestyle="--", label="Moyenne")
    ax.axvline(percentile_95, color="darkorange", linestyle=":", label=f"P95 ({percentile_95:.1f})")
    ax.text(percentile_95 + 1, ax.get_ylim()[1] * 0.9, f"P95 = {percentile_95:.1f}", color="darkorange", fontsize=8)
    ax.set(xlabel="PM2.5 (µg/m³)", ylabel="Fréquence", title="Distribution des concentrations")
    ax.legend(loc="best")

    ax = fig.add_subplot(gs[1, 2])
    sns.boxplot(data=sample, x="month", y="pm25", color="#8c564b", ax=ax)
    ax.set(xlabel="Mois", ylabel="PM2.5 (µg/m³)", title="Variabilité mensuelle")

    ax = fig.add_subplot(gs[2, 0])
    sns.boxplot(data=sample, x="hour", y="pm25", color="#17becf", ax=ax)
    ax.set(xlabel="Heure", ylabel="PM2.5 (µg/m³)", title="Variabilité horaire")

    ax = fig.add_subplot(gs[2, 1])
    ax.scatter(sample["pm1"], sample["pm25"], alpha=0.15, s=10, color="#17becf")
    ax.set(xlabel="PM1 (µg/m³)", ylabel="PM2.5 (µg/m³)", title="Relation PM1 vs PM2.5")
    ax.plot([sample["pm1"].min(), sample["pm1"].max()], [sample["pm1"].min(), sample["pm1"].max()], color="red", linestyle="--")

    ax = fig.add_subplot(gs[2, 2])
    monthly_exceedance.plot(kind="bar", ax=ax, color="#bcbd22")
    ax.set(xlabel="Mois", ylabel="Pourcentage de dépassement (%)", title="Taux de dépassement par mois")
    ax.axhline(seuil_oms, color="red", linestyle="--", label="Seuil OMS")
    for container in ax.containers:
        ax.bar_label(container, fmt="%.1f", padding=3, fontsize=8)
    ax.legend(loc="best")

    fig.subplots_adjust(top=0.90, bottom=0.05, left=0.05, right=0.98, hspace=0.35, wspace=0.22)
    return finaliser(fig, "dashboard", mode)
