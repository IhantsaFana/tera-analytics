import pandas as pd

from config import fichier_csv


def extraire(chemin=None):
    """Extraction : lit le CSV brut."""
    return pd.read_csv(chemin or fichier_csv, skiprows=1, parse_dates=["time"])
