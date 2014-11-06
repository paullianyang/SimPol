import random
import numpy as np
from scipy.spatial.distance import euclidean, cityblock

class kmeans(object):
    def __init__(self, k, init='k++', max_iter=-1, verbose = False, distance='euclidean'):
        '''
        k: number of clusters
        init: choose initial metrics randomly or method of kmeans++
        max_iter: set a maximum number of iterations for convergence. The default is -1, which sets no max
        verbose: if True, prints the iteration number and the current centers for each iteration
        distance: sets the distance metric to minimize for
        random_state: sets a random seed
        '''
        distance_methods = {'euclidean': euclidean,
                            'cityblock': cityblock}

        self.k = k
        self.init = init
        self.max_iter = max_iter
        self.verbose = verbose
        self.cluster_centers_ = None
        self.labels_ = None
        self.distance = distance_methods[distance]
        
    def fit(self, X):
        '''
        INPUT: numpy 1-D matrix
        OUTPUT: none
        '''
        if self.init == 'k++':
            self.kplusplus_init(X)
        else:
            self.cluster_centers_ = np.array(random.sample(X, self.k))
            
        counter = 0
        while True:
            if self.max_iter > 0 or self.verbose:
                if counter == self.max_iter:
                    break
                else:
                    counter += 1
            
            labels = self.predict(X)

            new_centers = np.zeros(self.cluster_centers_.shape)
            for i in np.arange(self.k):
                new_centers[i] = np.mean(X[labels == i], axis=0)
    
            if (new_centers == self.cluster_centers_).all():
                break
    
            self.cluster_centers_ = new_centers
            
            if self.verbose:
                print 'iter: ', counter
                print new_centers
        
        self.labels_ = labels
        pass

    def predict(self, X):
        '''
        INPUT: 1-D numpy array
        OUTPUT: 1-D numpy array

        returns the closest center for each point
        '''
        labels = np.zeros(X.shape[0])
        for i, datapoint in enumerate(X):
            distances = [self.distance(datapoint, center) for center in self.cluster_centers_]
            labels[i] = np.argmin(distances)
        return labels

    def kplusplus_init(self, X):
        '''
        INPUT: 1-D numpy array
        OUTPUT: None
        
        picks initial cluster centers weighted against how close they are from another
        '''
        self.cluster_centers_ = np.array(random.sample(X, 1))
        while self.cluster_centers_.shape[0] < self.k:
            distances = np.array([min([self.distance(datapoint, center) for center in self.cluster_centers_]) for datapoint in X])
            probs = distances/distances.sum()
            cumprobs = probs.cumsum()
            i = np.where(cumprobs >= random.random())[0][0]
            self.cluster_centers_ = np.row_stack((self.cluster_centers_, X[i]))
            if self.verbose:
                print self.cluster_centers_
        pass
