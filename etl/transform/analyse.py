from config import seuil_oms


def ajouter_features_temporelles(df):
    df = df.copy()
    df["hour"] = df["time"].dt.hour
    df["month"] = df["time"].dt.month
    df["date"] = df["time"].dt.date
    return df


def moyenne_journaliere_ville(df):
    """Moyenne PM2.5 par jour, agrégée sur tous les capteurs."""
    daily = df.groupby(["id_sensor", "date"])["pm25"].mean().reset_index()
    return daily.groupby("date")["pm25"].mean().reset_index(name="pm25_mean")


def stats_par_capteur(df):
    return (
        df.groupby(["id_sensor", "id_install"])["pm25"]
        .agg(["count", "mean", "median", "max"])
        .round(2)
        .sort_values("mean", ascending=False)
    )


def profil_horaire(df):
    return df.groupby("hour")["pm25"].agg(["mean", "std"]).round(2)


def profil_mensuel(df):
    return df.groupby("month")["pm25"].agg(["mean", "std"]).round(2)


def conformite_oms(moyenne_journaliere):
    pm25 = moyenne_journaliere["pm25_mean"]
    au_dessus_oms = pm25 > seuil_oms
    return {
        "pm25_moyen": round(pm25.mean(), 2),
        "jours_au_dessus_oms": int(au_dessus_oms.sum()),
        "pct_au_dessus_oms": round(au_dessus_oms.mean() * 100, 1),
    }
