from pathlib import Path

racine = Path(__file__).parent
fichier_csv = racine / "data/tera_analytics_data.csv"
dossier_donnees = racine / "data" / "processed"
dossier_graphiques = racine / "outputs" / "figures"

seuil_oms = 15.0 # µg/m³ — recommandation OMS sur 24h
percentile_outliers = 0.99
