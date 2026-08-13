"""Point d'entrée du pipeline de qualité de l'air."""

import argparse
import subprocess
import sys

from etl.extract.extraire import extraire
from etl.load.exporter import exporter
from etl.transform.analyse import (
    ajouter_features_temporelles,
    conformite_oms,
    moyenne_journaliere_ville,
    stats_par_capteur,
)
from etl.transform.nettoyage import nettoyer
from visualisation import graphique_dashboard


def parser_arguments():
    parser = argparse.ArgumentParser(description="Pipeline qualité de l'air — Madagascar")
    groupe = parser.add_mutually_exclusive_group()
    groupe.add_argument("--show", dest="mode", action="store_const", const="show", default="show", help="Afficher le dashboard de visualisation")
    groupe.add_argument("--export", dest="mode", action="store_const", const="export", help="Exporter les graphiques sans ouvrir l'interface")
    groupe.add_argument("--web", dest="mode", action="store_const", const="web", help="Lancer la version Streamlit du dashboard")
    return parser.parse_args()


def run_pipeline(mode="show"):
    print("1. Extract — lecture du CSV...")
    df = extraire()
    print(f"   {len(df):,} lignes — {df['time'].min().date()} → {df['time'].max().date()}")

    print("2. Transform — nettoyage...")
    df = nettoyer(df)

    print("3. Transform — analyse...")
    df = ajouter_features_temporelles(df)
    moyenne_jour = moyenne_journaliere_ville(df)
    stats = stats_par_capteur(df)
    oms = conformite_oms(moyenne_jour)

    print("\n--- Résultats ---")
    print(f"PM2.5 moyen : {oms['pm25_moyen']} µg/m³")
    print(f"Jours > OMS 15 µg/m³ : {oms['jours_au_dessus_oms']} ({oms['pct_au_dessus_oms']}%)")
    print("\nTop 5 capteurs les plus pollués :")
    print(stats.head())

    print("\n4. Load — export CSV...")
    dossier = exporter(df, moyenne_jour)
    print(f"   → {dossier}/")

    print(f"\n5. Dashboard ({mode})...")
    chemin_dashboard = graphique_dashboard(df, stats, moyenne_jour, mode)
    if mode == "export" and chemin_dashboard is not None:
        # graphique_dashboard peut maintenant retourner une liste de chemins
        if isinstance(chemin_dashboard, (list, tuple)):
            for p in chemin_dashboard:
                print(f"   → {p}")
        else:
            print(f"   → {chemin_dashboard}")

    print("\nTerminé.")


def run_web():
    print("Lancement de la version Web Streamlit...")
    print("Accédez à http://localhost:8501 après démarrage")
    subprocess.run([sys.executable, "-m", "streamlit", "run", "streamlit_app.py"], check=True)


def main():
    args = parser_arguments()
    if args.mode == "web":
        run_web()
    else:
        run_pipeline(mode=args.mode)


if __name__ == "__main__":
    main()
