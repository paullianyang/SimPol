'''
Simulates cop patrol given a specified region and
displays response times for each patrol behavior
to determine the optimal patrol strategy
'''
import numpy as np
import utils
import split_city
from datetime import datetime
import pickle
import pandas as pd
import kmeans
DATABASE = '../data/simulation.db'


class SimPol(object):
    def __init__(self, df, kmean):
        '''
        INPUT:
            df - DataFrame with columns: 'X', 'Y', 'Regions'
            kmean - kmean model
        OUTPUT: None

        Simulates cop patrol given kmean cluster
        '''
        self.df = self.clean_df(df)
        self.cops_num = None
        self.crime_center = None
        self.kmean = kmean
        self.min_y = None
        self.max_y = None
        self.min_x = None
        self.max_x = None
        self.region = None
        self.center = None
        self.response_time = None
        self.sql = utils.sqlite(DATABASE)

    def initiate_region(self, region):
        self.region = region
        self.center = self.kmean.cluster_centers_[self.region]
        label_indices = self.df['Region'] == self.region
        self.min_y = self.df[label_indices]['Y'].min()
        self.max_y = self.df[label_indices]['Y'].max()
        self.min_x = self.df[label_indices]['X'].min()
        self.max_x = self.df[label_indices]['X'].max()
        self.highest_crime()

    def initiate_cops(self, cops_num, response_time):
        '''
        INPUT: number of cops, minutes dealt for each crime
        OUTPUT: None

        Set the number of caps/cases that can be handled simultaneously
        and the number of minutes is needed to respond to each crime
        '''
        self.cops_num = cops_num
        # convert reponse_time to seconds
        self.response_time = response_time*60
        for cop in range(self.cops_num):
            samp_y, samp_x = self.random_coord()
            self.sql.insert_data('cops', [cop, samp_y, samp_x])
            self.sql.insert_data('rcop_now',
                                 [cop, 0, samp_y, samp_x, -1, 'available'])
            self.sql.insert_data('lcop_now',
                                 [cop, 0, samp_y, samp_x, -1, 'available'])
            self.sql.insert_data('ccop_now',
                                 [cop, 0, samp_y, samp_x, -1, 'available'])
            self.sql.insert_data('hcop_now',
                                 [cop, 0, samp_y, samp_x, -1, 'available'])

    def random_coord(self):
        while True:
            samp_y = (1+np.random.rand() *
                      ((self.max_y-self.min_y)/self.min_y))*self.min_y
            samp_x = (1+np.random.rand() *
                      ((self.max_x-self.min_x)/self.min_x))*self.min_x
            if self.kmean.predict([samp_x, samp_y]) == self.region:
                break
        return samp_y, samp_x

    def patrol_random(self):
        samp_y, samp_x = self.random_coord()
        return samp_y, samp_x

    def patrol_home(self):
        return self.center

    def patrol_crime(self):
        return self.crime_center

    def highest_crime(self):
        # split region into 50
        # and find the most probable
        # region for crime
        # Use KDE on next iteration
        label_indices = self.df['Region'] == self.region
        X = self.df[label_indices][['X', 'Y']]
        km = split_city.split_city(X)
        self.df[label_indices]['split_regions'] = km.labels_
        most_crime = self.df[label_indices]['split_regions'].value_counts(). \
            index[0]
        self.crime_center = km.cluster_centers_[most_crime]

    def move_cop(self, coptype, values):
        '''
        INPUT:
            coptype: rcop, lcop, ccop hcop
            values: id, utc, lat, long
        OUTPUT: None

        Moves cop position
        '''
        cop_id, utc, cop_lat, cop_long, start_time, status = values
        query = '''
            UPDATE %s_now
            SET utc = %d,
                lat = %f,
                long = %f,
                start_time = %d,
                status = %s
            WHERE id = %d
            ''' % (coptype, utc, cop_lat, cop_long, start_time, status, cop_id)
        utils.execute(query)

    def update(self, coptype):
        '''
        INPUT: rcop, lcop, ccop, hcop
        OUTPUT: None

        moves all cops current position into move history
        '''
        self.sql.insert_tabletotable(coptype+'_now', coptype+'_moves')

    def clean_df(self, df):
        '''
        INPUT: dataframe
        OUTPUT: dataframe

        preprocessing for simulation
        '''
        df['split_region'] = -1
        df['unixtime'] = df['Date'] + ' ' + df['Time']
        df['unixtime'] = df['unixtime']. \
            apply(lambda x: datetime.strptime(x, '%m/%d/%Y %H:%M'))
        df['unixtime'] = df['unixtime']. \
            apply(lambda x: utils.datetime_to_unixtime(x))
        df['X'] = df['X'].apply(lambda x: str(x))
        df['Y'] = df['Y'].apply(lambda x: str(x))
        return df

    def get_crime(self, start_time, end_time, region):
        '''
        INPUT: dataframe, start time, end time, start date, end date
        OUTPUT: filtered dataframe

        Fetches crime that occured within a date interval
        '''
        label_indices = self.df['Region'] = region
        crime_start = self.df['unixtime'] >= start_time
        crime_end = self.df['unixtime'] < start_time
        return self.df[crime_start & crime_end & label_indices]

    def run(self, date_string):
        '''
        INPUT: YYYY-MM-DD Date String
        OUTPUT: None

        Runs Simulation for given date
        '''
        start_date = datetime.strptime(date_string, '%Y-%m-%d')
        start_utc = utils.datetime_to_unixtime(start_date)
        interval = 60  # each run is 60 seconds
        iterations = (60*60*24)/interval
        for i in range(iterations):
            end_utc = start_utc + interval
            crime_df = self.get_crime(start_time=start_utc,
                                      end_time=end_utc,
                                      region=self.region)
            self.dispatch_cops(crime_df, start_utc)

    def dispatch_cops(self, crime_df, start_utc):
        coptypes = ['rcop', 'lcop', 'hcop', 'ccop']
        crime_df['coord'] = crime_df['Y'] + ',' + crime_df['X']
        crime_locations = crime_df['coord'].values
        for crime_loc in crime_locations:
            for cop in coptypes:
                query = "SELECT * FROM %s_now WHERE status = 'available'" % cop
                cop_df = pd.io.sql.read_sql(query, self.sql.conn)
                if cop_df['id'].count() == 0:  # no cops available
                    break
                cop_df['origin_coord'] = cop_df['origin_lat'] + \
                    ',' + cop_df['origin_long']
                cop_df['time_away'] = cop_df['origin_coord']. \
                    apply(lambda x: kmeans.driving_distance(x.split(),
                                                            crime_loc.split()))
                cop_id = cop_df.sort(columns='time_away').head()['id'].values
                self.update()
                self.move_cop(cop, values=(cop_id,
                                           start_utc,
                                           crime_loc.split(),
                                           start_utc,
                                           'busy'))


def preload():
    df = pickle.load(open('../data/sfpd_incident_2014.csv', 'rb'))
    km = pickle.load(open('../data/traind_km.pkl', 'rb'))
    labels = pickle.load(open('../data/trained_prediction.pkl', 'rb'))
    df['Regions'] = labels
    return df, km


if __name__ == '__main__':
    df, km = preload()
    sim = SimPol(df, km)
    sim.initiate_region(7)
    sim.initiate_cops(cops_num=20, response_time=30)
