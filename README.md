# Rapport du projet — Dashboard Qualité de l'Air

## 1. Contexte et objectif
Ce projet analyse la pollution de l'air (`PM2.5`) à Antananarivo à partir d'un jeu de données historique. L'objectif est de transformer des données brutes en informations claires, puis de présenter ces informations dans un tableau de bord interactif que l'on peut facilement expliquer.

## 2. Ce que fait le projet
Le projet fait trois choses principales :

1. **Lire les données**
   - Le fichier source contient des relevés de qualité de l'air à différents moments et emplacements.
   - Le programme lit ce fichier et le prépare pour l'analyse.

2. **Nettoyer les données**
   - Il supprime les mesures incorrectes ou extrêmes qui pourraient fausser les résultats.
   - Il conserve uniquement les données propres et cohérentes pour l'analyse.

3. **Montrer des résultats**
   - Il calcule des moyennes et des tendances.
   - Il affiche un tableau de bord interactif pour explorer les résultats facilement.

## 3. Données utilisées
Les données proviennent d'un fichier CSV :
- `tera_analytics_data.csv`

Chaque ligne du fichier représente une mesure de pollution à un instant donné.

## 4. Étapes du traitement
Le projet est organisé en une chaîne simple :

- **Extraction** : lire le fichier de données.
- **Nettoyage** : supprimer les lignes qui ne sont pas fiables.
- **Calcul** : créer des indicateurs utiles.
- **Affichage** : montrer ces indicateurs dans un tableau de bord.

## 5. Ce qui est calculé
Le projet produit plusieurs résultats importants :

- **Moyenne journalière** de PM2.5 sur la ville.
- **Nombre de jours où la pollution dépasse la limite recommandée par l'OMS**.
- **Classement des capteurs** les plus pollués.
- **Profil horaire** : comment la pollution évolue au cours de la journée.
- **Profil mensuel** : comment la pollution change selon les mois.

## 6. Le tableau de bord Streamlit
L'application interactive s'appelle `streamlit_app.py`.

Elle propose :
- Un filtre pour choisir un ou plusieurs capteurs.
- Un filtre pour limiter la période par mois.
- Un filtre pour limiter les heures de la journée.
- Des graphiques dynamiques qui se adaptent aux filtres.

### Section du tableau de bord
- **Vue d'ensemble** : montre les grandes tendances.
- **Analyse temporelle** : montre l'évolution jour après jour.
- **Capteurs** : compare les différents appareils de mesure.
- **Distribution** : montre comment les valeurs se répartissent.

## 7. Résultats clés à expliquer
Voici les points les plus importants à présenter :

- Les mesures sont d'abord nettoyées pour ne pas prendre en compte des erreurs de capteur.
- On calcule une moyenne de PM2.5 sur chaque jour, puis on mesure combien de jours dépassent le seuil recommandé par l'OMS.
- Le tableau de bord permet de voir rapidement quels capteurs enregistrent les valeurs les plus élevées.

## 8. Comment expliquer le projet sans termes techniques
- Le projet transforme des relevés bruts en une présentation facile à lire.
- Il retire d'abord les mauvaises mesures pour n'utiliser que les données fiables.
- Il montre ensuite les tendances de pollution sur la journée et sur l'année.
- Il permet de comparer les lieux de mesure entre eux.
- Il met en évidence les jours où la pollution est trop forte.

## 9. Comment lancer le tableau de bord
Depuis le dossier du projet, utiliser :

```bash
streamlit run streamlit_app.py
```

Puis ouvrir le lien affiché dans le navigateur.

## 10. Points forts du projet
- Le tableau de bord est interactif : on peut changer les filtres et voir les graphiques se mettre à jour.
- Il fournit des résultats simples à comprendre : moyenne, maxi, mini, nombre de jours dangereux.
- Il peut servir à expliquer la qualité de l'air à des décideurs ou à des non-spécialistes.

## 11. Structure du code
- `main.py` : exécute le traitement séquentiel et produit des résultats.
- `etl/extract/extraire.py` : lit le fichier de données.
- `etl/transform/nettoyage.py` : nettoie les données.
- `etl/transform/analyse.py` : calcule les mesures et les tendances.
- `streamlit_app.py` : affiche le tableau de bord interactif.
- `config.py` : contient les chemins et la limite OMS.

## 12. Messages à retenir
- Ce projet n'est pas seulement un calcul de chiffres : c'est un moyen de rendre compréhensible la pollution de l'air.
- Le nettoyage est essentiel pour éviter de tirer de mauvaises conclusions.
- Le tableau de bord permet de naviguer facilement dans les données et d'identifier les périodes ou capteurs problématiques.

## 13. État final du projet
- L'interface principale est désormais `streamlit_app.py`.
- Les anciens prototypes `dashboard.py` et `visualisation/dashboard.py` ont été supprimés.
- La navigation utilise maintenant une barre en haut avec des pages claires : vue d'ensemble, analyse temporelle, capteurs et distribution.
- Les filtres sont accessibles directement dans la barre latérale sans titre de section superflu.
- Le projet est prêt à être présenté et utilisé en production légère.
# tera-analytics
