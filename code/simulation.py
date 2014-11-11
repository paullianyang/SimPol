import numpy as np
import pandas as pd
import utils

DATABASE = '../data/simulation.db'

def initiate_cops(df, cops_num, region, kmean):
    label_indices = df['Region'] == region
    min_y = df[label_indices]['Y'].min()
    max_y = df[label_indices]['Y'].max()
    min_x = df[label_indices]['X'].min()
    max_x = df[label_indices]['X'].max()
    for cop in range(cops_num):
        while True:
            samp_y = (1+np.random.rand()*((max_y-min_y)/min_y))*min_y
            samp_x = (1+np.random.rand()*((max_x-min_x)/min_x))*min_x
            if kmean.predict([samp_x, samp_y]) == region:
                break
        utils.insert_data(DATABASE, 'cops', [cop, samp_y, samp_x, 'available'])
        utils.insert_data(DATABASE, 'rcop_now', [cop, 0, samp_y, samp_x])
        utils.insert_data(DATABASE, 'lcop_now', [cop, 0, samp_y, samp_x])
        utils.insert_data(DATABASE, 'ccop_now', [cop, 0, samp_y, samp_x])
        utils.insert_data(DATABASE, 'hcop_now', [cop, 0, samp_y, samp_x])

    
