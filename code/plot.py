'''
2D Plot of KMean with labels
'''
import matplotlib.pylab as plt
import numpy as np
plt.style.use('ggplot')


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
    center_x = centers[:, 0]
    center_y = centers[:, 1]
    # plot and color points by cluster
    for label, col in zip(labels, colors):
        label_indices = np.where(kmean.labels_ == label)
        x = X[:, 0][label_indices]
        y = X[:, 1][label_indices]

        plt.plot(x, y, 'o',
                 markerfacecolor=col,
                 alpha=0.1)
        plt.axis('off')

    # plot cluster centers in black
    plt.plot(center_x, center_y, 'o',
             markerfacecolor='k')

    # add labels to centers
    for label, x, y in zip(labels, center_x, center_y):
        plt.annotate(
            label,
            xy=(x, y), xytext = (-20, 20),
            textcoords = 'offset points', ha = 'right', va = 'bottom',
            bbox = dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.5),
            arrowprops = dict(arrowstyle='->', connectionstyle='arc3,rad=0'))

    if save_loc:
        plt.savefig(save_loc)
    else:
        plt.show()


def plotone(df, field, centers=None, figsize=(8, 5), save_loc=False):
    '''
    INPUT: dataframe, field to color by,
           cluster centers (optional),
           figure size tuple,
           local file path to save to (optional)
    OUTPUT: scatter plot

    Show scatterplot by dataframe field, and optional cluster centers
    if plotting predicted values
    '''
    regions = df[field].unique()
    colors = plt.cm.Spectral(np.linspace(0, 1, len(regions)))
    plt.figure(figsize=figsize)
    for r, col in zip(regions, colors):
        label_indices = df[field] == r
        x = df[label_indices]['X']
        y = df[label_indices]['Y']
        plt.plot(x, y, '.',
                 markerfacecolor=col,
                 alpha=0.1)
        plt.axis('off')

    if centers is not None:
        center_x = centers[:, 0]
        center_y = centers[:, 1]
        plt.plot(center_x, center_y, '.',
                 markerfacecolor='k')
        labels = np.arange(len(centers))

        for label, x, y in zip(labels, center_x, center_y):
            plt.annotate(
                label,
                xy=(x, y), xytext=(-20, 20),
                textcoords='offset points', ha='right', va='bottom',
                bbox=dict(boxstyle='round, pad=0.5', fc='yellow', alpha=0.5),
                arrowprops=dict(arrowstyle='->',
                                connectionstyle='arc3, rad=0'))

    if save_loc:
        plt.savefig(save_loc)
    else:
        plt.show()
