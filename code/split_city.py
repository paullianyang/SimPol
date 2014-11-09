import pandas as pd
from sklearn.cluster import KMeans
import numpy as np
import pickle

###I want to split san francisco up into small equidistant clusters
###So I can sample and origin and destination within each cluster
###over time to estimate traffic
df = pd.read_csv('../data/sfpd_incident_2014.csv')
X = np.array(df[['X', 'Y']])

kmeans = KMeans(n_clusters=50, init='k-means++', n_init=10, n_jobs=-1, random_state=1, max_iter=1000)
kmeans.fit(X)
pickle.dump(kmeans, open('../data/split_sf.pkl', 'wb'))
