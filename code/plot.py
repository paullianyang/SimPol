import matplotlib.pyplot as plt
import numpy as np

def pkmean(kmean, X, save_loc=None):
    '''
    INPUT: fitted kmean model,
           1-dimensional array of x,y tuples,
           
           save location
    OUTPUT: None

    Create and show a scatterplot color points by cluster
    and plot the cluster centers in black. 
    
    You can choose to save the plot if 
    file location is specified for save_loc
    '''
    centers = kmean.cluster_centers_
    colors = plt.cm.Spectral(np.linspace(0, 1, len(centers)))
    labels = np.arange(len(centers))
    center_x = centers[:,0]
    center_y = centers[:,1]
    #plot and color points by cluster
    for label, col in zip(labels, colors):
        label_indices = np.where(kmean.labels_ == label)
        x = X[:,0][label_indices]
        y = X[:,1][label_indices]

        plt.plot(x, y, 'o',
                markerfacecolor=col,
                markeredgecolor='k')

    #plot cluster centers in black
    plt.plot(center_x, center_y, 'o',
            markerfacecolor='k')

    #add labels to centers
    for label, x, y in zip(labels, center_x, center_y):
        plt.annotate(
            label, 
            xy = (x, y), xytext = (-20, 20),
            textcoords = 'offset points', ha = 'right', va = 'bottom',
            bbox = dict(boxstyle = 'round,pad=0.5', fc = 'yellow', alpha = 0.5),
            arrowprops = dict(arrowstyle = '->', connectionstyle = 'arc3,rad=0'))

    if save_loc:
        plt.savefig(save_loc)
    else:
        plt.show()
    return None


