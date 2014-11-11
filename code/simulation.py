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

def move_cop(coptype, values):
    '''
    INPUT:
        coptype: rcop, lcop, ccop hcop
        values: id, utc, lat, long
    OUTPUT: None
    
    Moves cop position
    '''
    cop_id, utc, cop_lat, cop_long = values
    query = '''
        UPDATE %s_now
        SET utc = %d,
            lat = %f,
            long = %f
        WHERE id = %d
        ''' % (coptype, utc, cop_lat, cop_long, cop_id)
    utils.execute(query)

def update(coptype):
    '''
    INPUT: rcop, lcop, ccop, hcop
    OUTPUT: None

    moves all cops current position into move history
    '''
    utils.insert_tabletotable(DATABASE, coptype+'_now', coptype+'_moves')

def get_crime(df, start_time, end_time, start_date, end_date, region):
    '''
    INPUT: dataframe, start time, end time, start date, end date
    OUTPUT: filtered dataframe

    Fetches crime that occured within a date interval
    '''
    label_indices = df['Region'] = region
    crime_startdate = df['Date'] >= start_date
    crime_enddate = df['Date'] <= end_date
    crime_start = df['Time'] >= start_time
    crime_end = df['Time'] <= start_time
    return df[crime_startdate & crime_enddate & crime_start & crime_end & region]
