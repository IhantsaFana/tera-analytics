from config import dossier_donnees


def exporter(df, moyenne_journaliere):
    """Chargement : écrit les données transformées en CSV."""
    dossier_donnees.mkdir(parents=True, exist_ok=True)
    df.to_csv(dossier_donnees / "donnees_nettoyees.csv", index=False)
    moyenne_journaliere.to_csv(dossier_donnees / "moyenne_journaliere.csv", index=False)
    return dossier_donnees
