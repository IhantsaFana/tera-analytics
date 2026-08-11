"""Application Streamlit - Dashboard interactif qualité de l'air."""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from pathlib import Path
import warnings

warnings.filterwarnings("ignore")

# Configuration Streamlit
st.set_page_config(
    page_title="Dashboard Qualité de l'Air - Antananarivo",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Style minimaliste
st.markdown("""
<style>
    .main { padding-top: 1rem; }
    .metric-container { margin-bottom: 1rem; }
    h1, h2, h3 { font-weight: 600; color: #1a1a1a; margin-top: 0; }
    [data-testid="stMetricValue"] { font-size: 1.5rem; font-weight: 700; }
    .stTabs [data-baseweb="tab-list"] button { font-weight: 500; padding: 0.5rem 1rem; }
</style>
""", unsafe_allow_html=True)

# Import des modules ETL
from etl.extract.extraire import extraire
from etl.transform.nettoyage import nettoyer
from etl.transform.analyse import (
    ajouter_features_temporelles,
    conformite_oms,
    moyenne_journaliere_ville,
    profil_horaire,
    profil_mensuel,
    stats_par_capteur,
)
from config import seuil_oms


@st.cache_resource
def load_data():
    """Charger et nettoyer les données une seule fois."""
    df = extraire()
    df = nettoyer(df)
    df = ajouter_features_temporelles(df)
    return df


@st.cache_data
def get_analysis(df):
    """Calculer les analyses."""
    moyenne_jour = moyenne_journaliere_ville(df)
    stats = stats_par_capteur(df)
    oms = conformite_oms(moyenne_jour)
    profil_h = profil_horaire(df)
    profil_m = profil_mensuel(df)
    return moyenne_jour, stats, oms, profil_h, profil_m


# Charger les données
with st.spinner("Chargement des données..."):
    df = load_data()
    moyenne_jour, stats, oms, profil_h, profil_m = get_analysis(df)

# Sidebar - Filtres

# Période
if "time" in df.columns:
    date_min = df["time"].dt.date.min()
    date_max = df["time"].dt.date.max()
    selected_dates = st.sidebar.date_input(
        "Période",
        value=(date_min, date_max),
        min_value=date_min,
        max_value=date_max,
    )

    if isinstance(selected_dates, tuple) and len(selected_dates) == 2:
        date_debut, date_fin = selected_dates
    else:
        date_debut, date_fin = date_min, date_max
else:
    date_debut, date_fin = None, None

# Sélectionner les capteurs
capteurs_uniques = sorted(df["id_install"].unique())
capteurs_selected = st.sidebar.multiselect(
    "Sélectionner les capteurs",
    capteurs_uniques,
    default=capteurs_uniques,
)

# Sélectionner les mois
mois_selected = st.sidebar.slider(
    "Plage de mois",
    1, 12, (1, 12)
)

# Sélectionner les heures
heures_selected = st.sidebar.slider(
    "Plage d'heures",
    0, 23, (0, 23)
)

# Filtrer les données
df_filtered = df[
    (df["id_install"].isin(capteurs_selected)) &
    (df["month"] >= mois_selected[0]) &
    (df["month"] <= mois_selected[1]) &
    (df["hour"] >= heures_selected[0]) &
    (df["hour"] <= heures_selected[1])
]

if date_debut is not None and date_fin is not None:
    df_filtered = df_filtered[
        (df_filtered["time"].dt.date >= date_debut) &
        (df_filtered["time"].dt.date <= date_fin)
    ]

st.sidebar.caption(f"{len(df_filtered):,} mesures affichées")

# Recalculer les analyses avec les données filtrées
if len(df_filtered) > 0:
    moyenne_jour_filtered = moyenne_journaliere_ville(df_filtered)
    stats_filtered = stats_par_capteur(df_filtered)
    oms_filtered = conformite_oms(moyenne_jour_filtered)
    profil_h_filtered = profil_horaire(df_filtered)
    profil_m_filtered = profil_mensuel(df_filtered)
else:
    st.error("Aucune donnée ne correspond aux filtres sélectionnés")
    st.stop()

st.title("Dashboard Qualité de l'Air")
st.markdown("#### Analyse PM2.5 — Antananarivo")

page = st.radio(
    "Navigation",
    ["Vue d'ensemble", "Analyse temporelle", "Capteurs", "Distribution"],
    horizontal=True,
)

st.markdown("---")

if page == "Vue d'ensemble":
    heure_pire = int(profil_h_filtered["mean"].idxmax())
    heure_pire_valeur = profil_h_filtered.loc[heure_pire, "mean"]
    if heure_pire <= 12:
        moment_pire = "matin"
    elif heure_pire <= 17:
        moment_pire = "midi"
    else:
        moment_pire = "soir"
    jour_pire = moyenne_jour_filtered.loc[moyenne_jour_filtered["pm25_mean"].idxmax(), "date"]
    jour_pire_valeur = moyenne_jour_filtered["pm25_mean"].max()
    min_val = df_filtered["pm25"].min()
    max_val = df_filtered["pm25"].max()

    st.subheader("Où est-ce le plus pollué ?")
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.metric("Heure la plus polluée", f"{heure_pire}h", f"{heure_pire_valeur:.2f} µg/m³")
    with col_b:
        st.metric("Moment le plus critique", moment_pire.capitalize(), f"{heure_pire_valeur:.2f} µg/m³")
    with col_c:
        st.metric("Jour le plus pollué", jour_pire.strftime("%d/%m/%Y"), f"{jour_pire_valeur:.2f} µg/m³")

    st.markdown("---")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("PM2.5 moyen", f"{oms_filtered['pm25_moyen']} µg/m³", delta=None)
    with col2:
        st.metric("Min / Max observé", f"{min_val:.2f} / {max_val:.2f} µg/m³")
    with col3:
        st.metric("Jours > OMS", f"{oms_filtered['jours_au_dessus_oms']}", delta=f"{oms_filtered['pct_au_dessus_oms']}%")

    if oms_filtered["pm25_moyen"] > seuil_oms:
        st.warning(f"La pollution moyenne observée ({oms_filtered['pm25_moyen']} µg/m³) dépasse le seuil OMS.")
    else:
        st.success("La pollution moyenne observée reste sous le seuil OMS.")

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Cycle diurne")
        fig_hourly = px.line(
            profil_h_filtered.reset_index(),
            x="hour",
            y="mean",
            title="Pollution par heure",
            labels={"hour": "Heure", "mean": "PM2.5 (µg/m³)"}
        )
        fig_hourly.add_hline(y=seuil_oms, line_dash="dash", line_color="red", annotation_text="OMS")
        st.plotly_chart(fig_hourly, width='stretch')
    with col2:
        st.subheader("Variation saisonnière")
        fig_monthly = px.bar(
            profil_m_filtered.reset_index(),
            x="month",
            y="mean",
            title="Pollution par mois",
            labels={"month": "Mois", "mean": "PM2.5 (µg/m³)"}
        )
        fig_monthly.add_hline(y=seuil_oms, line_dash="dash", line_color="red", annotation_text="OMS")
        st.plotly_chart(fig_monthly, width='stretch')

elif page == "Analyse temporelle":
    st.subheader("Analyse temporelle")
    fig_daily = px.line(
        moyenne_jour_filtered,
        x="date",
        y="pm25_mean",
        title="Moyenne PM2.5 par jour",
        labels={"date": "Date", "pm25_mean": "PM2.5 moyen (µg/m³)"}
    )
    fig_daily.add_hline(y=seuil_oms, line_dash="dash", line_color="red", annotation_text="OMS")
    st.plotly_chart(fig_daily, width='stretch')
    st.markdown("---")
    st.subheader("Heatmap horaire par mois")
    heatmap_data = df_filtered.groupby(["month", "hour"])["pm25"].mean().reset_index()
    heatmap_pivot = heatmap_data.pivot(index="hour", columns="month", values="pm25")
    fig_heatmap = px.imshow(
        heatmap_pivot,
        labels=dict(x="Mois", y="Heure", color="PM2.5 (µg/m³)"),
        color_continuous_scale="RdYlGn_r",
        aspect="auto"
    )
    st.plotly_chart(fig_heatmap, width='stretch')

elif page == "Capteurs":
    st.subheader("Comparaison capteurs")
    nb_capteurs_max = int(stats_filtered.shape[0])
    default_n = min(10, nb_capteurs_max)
    st.caption(f"Capteurs disponibles : {nb_capteurs_max}")
    top_n = st.slider("Nombre de capteurs à afficher", 1, nb_capteurs_max, default_n, key="slider_top_n")
    top_capteurs = stats_filtered.head(top_n).reset_index()
    top_capteurs["capteur"] = top_capteurs["id_sensor"].astype(str) + " (" + top_capteurs["id_install"] + ")"
    fig_capteurs = px.bar(
        top_capteurs,
        x="mean",
        y="capteur",
        orientation='h',
        title="Capteurs par pollution moyenne",
        labels={"mean": "PM2.5 moyen (µg/m³)", "capteur": "Capteur"}
    )
    fig_capteurs.add_vline(x=seuil_oms, line_dash="dash", line_color="red", annotation_text="OMS")
    st.plotly_chart(fig_capteurs, width='stretch')
    st.markdown("---")
    st.subheader("Statistiques par capteur")
    st.dataframe(top_capteurs[["capteur", "count", "mean", "median", "max"]].sort_values("mean", ascending=False), width='stretch')
    st.subheader("Détail d’un capteur")
    capteur_selection = st.selectbox(
        "Sélectionner un capteur à analyser",
        options=top_capteurs["id_install"].tolist(),
        key="select_capteur_detail"
    )
    donnees_capteur = df_filtered[df_filtered["id_install"] == capteur_selection]
    if not donnees_capteur.empty:
        moyenne_capteur = donnees_capteur["pm25"].mean()
        if moyenne_capteur > seuil_oms:
            st.warning(f"Le capteur {capteur_selection} présente une moyenne supérieure au seuil OMS.")
        else:
            st.success(f"Le capteur {capteur_selection} reste globalement sous le seuil OMS sur cette période.")
        evolution_capteur = (
            donnees_capteur.set_index("time")["pm25"].resample("D").mean().reset_index()
        )
        fig_capteur = px.line(
            evolution_capteur,
            x="time",
            y="pm25",
            title=f"Évolution du capteur {capteur_selection}",
            labels={"time": "Date", "pm25": "PM2.5 (µg/m³)"}
        )
        fig_capteur.add_hline(y=seuil_oms, line_dash="dash", line_color="red", annotation_text="OMS")
        st.plotly_chart(fig_capteur, width='stretch')

elif page == "Distribution":
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Distribution des concentrations")
        fig_hist = px.histogram(
            df_filtered,
            x="pm25",
            nbins=50,
            title="Histogramme PM2.5",
            labels={"pm25": "PM2.5 (µg/m³)", "count": "Fréquence"}
        )
        fig_hist.add_vline(x=df_filtered["pm25"].mean(), line_dash="dash", line_color="blue", annotation_text="Moyenne")
        fig_hist.add_vline(x=seuil_oms, line_dash="dash", line_color="red", annotation_text="OMS")
        st.plotly_chart(fig_hist, width='stretch')
    with col2:
        st.subheader("Boxplot par mois")
        fig_box = px.box(
            df_filtered,
            x="month",
            y="pm25",
            title="Variabilité mensuelle",
            labels={"month": "Mois", "pm25": "PM2.5 (µg/m³)"}
        )
        fig_box.add_hline(y=seuil_oms, line_dash="dash", line_color="red", annotation_text="OMS")
        st.plotly_chart(fig_box, width='stretch')
    p95 = np.percentile(df_filtered["pm25"].dropna(), 95)
    mediane = df_filtered["pm25"].median()
    ecart_type = df_filtered["pm25"].std()
    st.info(f"Le percentile 95 est à {p95:.2f} µg/m³, la médiane à {mediane:.2f} µg/m³ et l’écart-type à {ecart_type:.2f} µg/m³.")


