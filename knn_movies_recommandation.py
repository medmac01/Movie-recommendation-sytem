# -*- coding: utf-8 -*-
"""KNN movies recommandation.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1XhKQIkj7K4FDcUwpcEEbZww_1GF6au71

**MOVIES RECOMMANDATION USING KNN**

# Collaborative Filtering Recommendation Engine

## 1) Importation des données
"""

# Chargement des données:
import pandas as pd
import numpy as np

# Movies
movies = pd.read_csv('/content/movie.csv')
movies.head()

# Ratings
rating = pd.read_csv('/content/rating.csv')
rating.head()

"""## 2) Exploration et nettoyage des données"""

# Description des movies
movies.describe()

# Description des ratings
rating.describe()

# Recherche de valeurs manquantes dans movies
movies.isnull().sum()

# Recherche de valeurs manquantes dans ratings
rating.isnull().sum()

# Affichages
print("Movies:",movies.shape)
print("Ratings:",rating.shape)

"""Fusion des bases de données importées pour l'analyse"""

# Réunir les deux bases de données
movies_merged = movies.merge(rating, on='movieId')
movies_merged.head()

# Effacer les données manquantes (il n'y en a pas dans cette base de données)
movies_merged = movies_merged.dropna(axis = 0, subset = ['title'])
movies_merged.head()

# Classer les données selon les titres les mieux notés
movies_average_rating = movies_merged.groupby('title')['rating'].mean().sort_values(ascending=False).reset_index().rename(columns={'rating':'Average Rating'})
movies_average_rating.head()

# Classer les données selon le nombre de votes et le rating (Ascendant)
movies_rating_count = movies_merged.groupby('title')['rating'].count().sort_values(ascending=False).reset_index().rename(columns={'rating':'Rating Count'}) #ascending=False
movies_rating_count_avg = movies_rating_count.merge(movies_average_rating, on='title')
movies_rating_count_avg.head()

# Classer les données selon le nombre de votes et le rating (Descendant)
movies_rating_count2 = movies_merged.groupby('title')['rating'].count().sort_values(ascending=True).reset_index().rename(columns={'rating':'Rating Count'}) #ascending=False
movies_rating_count_avg2 = movies_rating_count2.merge(movies_average_rating, on='title')
movies_rating_count_avg2.head()

"""Observations

* De nombreux films ont une note moyenne parfaite (5 étoiles) sur un ensemble de données de près de 100.000 notes d'utilisateurs. Cela suggère l'existence de valeurs aberrantes que nous devons confirmer davantage avec la visualisation.
* La présence de notes uniques pour plusieurs films suggère qu'on a défini une valeur seuil de notes pour produire de recommandations beaucoup plus précises

## 3) Visionnage des données

On se concentrerai sur la création de graphiques pour prouver/réfuter les observations et analyser les tendances que prendront les données (le cas échéant). On s'en tiendra à seaborn et matplotlib pour ce projet.
"""

# Commented out IPython magic to ensure Python compatibility.
#importation des bibliothèques de visualisation
import seaborn as sns
import matplotlib.pyplot as plt
sns.set(font_scale = 1)
plt.rcParams["axes.grid"] = False
plt.style.use('dark_background')
# %matplotlib inline

# Visualisation en histogrammes du nombre de films notés
plt.figure(figsize=(12,4))
plt.hist(movies_rating_count_avg['Rating Count'],bins=80,color='tab:purple')
plt.ylabel('Ratings Count(Scaled)', fontsize=16)
plt.savefig('ratingcounthist.jpg')

# Visualisation en histogramme du nombre d'utilisateurs qui notent chaque film et sauvegarde du plot
plt.figure(figsize=(12,4))
plt.hist(movies_rating_count_avg['Average Rating'],bins=80,color='tab:purple')
plt.ylabel('Average Rating',fontsize=16)
plt.savefig('avgratinghist.jpg')

# Le nuage de points associé à l'histogramme
plot = sns.jointplot(x='Average Rating',y='Rating Count',data=movies_rating_count_avg,alpha=0.5, color='tab:blue')
plot.savefig('joinplot.jpg')

"""**Analyse**

* Le tracé n°1 confirme nos observations d'un volume élevé de films avec un faible nombre d'audiences (notes). Outre la définition d'un seuil, nous pouvons également utiliser des quantiles à un centile plus élevé pour ce cas d'utilisation.
* L'histogramme n°2 présente la fonction de distribution des valeurs de la note moyenne.
* Joinplot illustre magnifiquement qu'il n'y a qu'un sous-ensemble de valeurs avec une note plus élevée qui ont une quantité considérable de notes.

### Élimination des valeurs aberrantes (films moins populaires)
"""

# Sélection des meilleures notes
rating_with_RatingCount = movies_merged.merge(movies_rating_count, left_on = 'title', right_on = 'title', how = 'left')
rating_with_RatingCount.head()

# Description de la nouvelle base de données
pd.set_option('display.float_format', lambda x: '%.3f' % x)
print(rating_with_RatingCount['Rating Count'].describe())

# Extraction des films les plus populaires
popularity_threshold = 50
popular_movies= rating_with_RatingCount[rating_with_RatingCount['Rating Count']>=popularity_threshold]
popular_movies.head()

"""
### Pivoter les Titres en tant qu'indices et userId en tant que colonnes (pour avoir une base de données prête à utiliser avec KNN)"""

import os
movie_features = popular_movies.pivot_table(index='title',columns='userId',values='rating').fillna(0)
movie_features.head()
# movie_features.to_excel('output.xlsx')

"""Ainsi, nous sauront quel utilisateur a noté quel film et aussi les films les plus notés

## 4) Implémentation du modèle KNN
"""

# Importations
from scipy.sparse import csr_matrix
movie_features_matrix = csr_matrix(movie_features.values)

# Entrainement du modèle
from sklearn.neighbors import NearestNeighbors
model_knn = NearestNeighbors(metric = 'cosine', algorithm = 'brute')
model_knn.fit(movie_features_matrix)

movie_features.shape

# 
np.random.seed(5)
query_index = np.random.choice(movie_features.shape[0])
print("recomendation for movie id:",query_index)
distances, indices = model_knn.kneighbors(movie_features.iloc[query_index,:].values.reshape(1, -1), n_neighbors = 6)
print("distances:",distances)
print("indices",indices)

movie_features.head()

for i in range(0, len(distances.flatten())):
    if i == 0:
        print('Recommendations for {0}:\n'.format(movie_features.index[query_index]))
    else:
        print('{0}: {1}, with distance of {2}:'.format(i, movie_features.index[indices.flatten()[i]], distances.flatten()[i]))
