'''
I want to split SF up into small equidistant clusters
so I can sample origins & destinations within each cluster
over time to estimate traffic
'''
import pandas as pd
from sklearn.cluster import KMeans
import numpy as np
import pickle


def split_city(X):
    kmeans = KMeans(n_clusters=50, init='k-means++', n_init=10, n_jobs=-1,
                    random_state=1, max_iter=1000)
    kmeans.fit(X)
    return kmeans

if __name__ == '__Main__':
    df = pd.read_csv('../data/sfpd_incident_2014.csv')
    X = np.array(df[['X', 'Y']])
    kmeans = split_city(X)
    pickle.dump(kmeans, open('../data/split_sf.pkl', 'wb'))
