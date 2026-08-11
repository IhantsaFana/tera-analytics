from config import percentile_outliers


def supprimer_valeurs_invalides(df):
    """Supprime les valeurs négatives et les incohérences PM1 > PM2.5."""
    df = df[(df["pm1"] >= 0) & (df["pm25"] >= 0)]
    return df[df["pm1"] <= df["pm25"]]


def supprimer_outliers(df):
    """Supprime les valeurs extrêmes au-delà du percentile configuré."""
    seuil = df["pm25"].quantile(percentile_outliers)
    return df[df["pm25"] <= seuil]


def nettoyer(df):
    """Pipeline de nettoyage complet."""
    n_initial = len(df)
    df = supprimer_valeurs_invalides(df)
    df = supprimer_outliers(df)
    print(f"Nettoyage : {n_initial:,} → {len(df):,} lignes")
    return df.reset_index(drop=True)
