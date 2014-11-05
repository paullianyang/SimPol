import numpy as np
import random

class KMeans(object):

    def __init__(self, points, k, iterations=1000, random_state=None):
        self.k = k
        self.points = points
        self.cluster_centers_ = points[self.initialize_centroids()]
        self.labels_ = self.assign_data_point()
        self.iterations = iterations
        if random_state:
            random.seed(random_state)

    def distance(self, Apoint, Bpoint, metric='euclidean'):
        '''
        INPUT: 2 array vector of floats, type of distance metric
        OUTPUT: a float for the distance between the 2 vectors
        '''
        C = Apoint - Bpoint
        C = C*C
        dsquared = C.sum()
        distance = dsquared**0.5
        return distance
    
    def all_distances(self, centroid):
        '''
        INPUT: centroid which is a np vector, 
        OUTPUT: returns list of distances
        '''
        centroid_distances = []
        for point in self.points:
            centroid_distances.append(self.distance(centroid, point))            
        return centroid_distances
    
    def initialize_centroids(self):
        '''
        INPUT: none
        OUTPUT: list of centroids
        randomly choose k points
        '''
        #make a choice choose k
        index = np.arange(0, self.points.shape[0], 1)
        kindexes = random.sample(index, self.k)
        return kindexes
    
    def get_all_centroid_distances(self):
        '''
        INPUT: None
        OUTPUT: list of centroid distances
        '''
        listoflist = []
        for i in xrange(self.k):
            listoflist.append(self.all_distances(self.cluster_centers_[i]))
        return listoflist
    
    def move_to_center(self):
        '''
        INPUT: None
        OUTPUT: Return new centroids
        Move centroids to the mean center of the cluster
        '''
        for k, pointlist in self.pointlabels.iteritems():
            self.cluster_centers_[k] = self.get_mean_centroid(pointlist)
    
    def assign_data_point(self):
        '''
        INPUT: None
        OUTPUT: dictionary with key = k centroid and value = a list of points that belongs to that centroid
        Gets distances for each point to every centroid assigns the points to nearest centroid
        '''
        listofdistances = self.get_all_centroid_distances()
        assignments = {}
        for i in xrange(self.k):
            assignments[i] = []
        for i in xrange(len(listofdistances[0])):
            closestcentroid = -1
            min_dist = listofdistances[0][i]
            for j in xrange(len(listofdistances)):
                if listofdistances[j][i] <= min_dist:
                    min_dist = listofdistances[j][i]
                    closestcentroid = j
            assignments[closestcentroid].append(i)
        return assignments

    def get_mean_centroid(self, list_of_indexes):
        '''
        INPUT: list of points which below to the centroid
        OUTPUT: a new point representing the centroid
        '''
        #get the points from self.points
        centroidpoints = self.points[list_of_indexes]
        return centroidpoints.mean(axis=0)
    
    def iteration(self):
        '''
        INPUT: NONE
        OUTPUT: NONE
        iterate through moving to the averege and reassigning the data points
        '''
        i = self.iterations
        while(i>0):
            oldlabels = self.labels_
            self.move_to_center()
            self.labels_ = self.assign_data_point()
            if oldlabels == self.labels_:
                break
            i = i - 1
    
    def iterate(self):
        oldlabels = self.labels_
        self.move_to_center()
        self.labels_ = self.assign_data_point()

class KPlusPlus(KMeans):
    def _dist_from_centers(self):
        cent = self.mu
        X = self.X
        D2 = np.array([min([np.linalg.norm(x-c)**2 for c in cent]) for x in X])
        self.D2 = D2
 
    def _choose_next_center(self):
        self.probs = self.D2/self.D2.sum()
        self.cumprobs = self.probs.cumsum()
        r = random.random()
        ind = np.where(self.cumprobs >= r)[0][0]
        return(self.X[ind])
 
    def init_centers(self):
        self.mu = random.sample(self.X, 1)
        while len(self.mu) < self.K:
            self._dist_from_centers()
            self.mu.append(self._choose_next_center())
