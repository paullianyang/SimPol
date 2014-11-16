'''
Simulates cop patrol given a specified region and
displays response times for each patrol behavior
to determine the optimal patrol strategy
'''
import numpy as np
import utils
import split_city
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
        self.df = df
        self.df['split_region'] = -1
        self.cops_num = None
        self.crime_center = None
        self.kmean = kmean
        self.min_y = None
        self.max_y = None
        self.min_x = None
        self.max_x = None
        self.region = None
        self.center = None

    def initiate_region(self, region):
        self.region = region
        self.center = self.kmean.cluster_centers_[self.region]
        label_indices = self.df['Region'] == self.region
        self.min_y = self.df[label_indices]['Y'].min()
        self.max_y = self.df[label_indices]['Y'].max()
        self.min_x = self.df[label_indices]['X'].min()
        self.max_x = self.df[label_indices]['X'].max()
        self.highest_crime()

    def initiate_cops(self, cops_num):
        self.cops_num = cops_num
        for cop in range(self.cops_num):
            samp_y, samp_x = self.random_coord()
            utils.insert_data(DATABASE, 'cops',
                              [cop, samp_y, samp_x, 'available'])
            utils.insert_data(DATABASE, 'rcop_now', [cop, 0, samp_y, samp_x])
            utils.insert_data(DATABASE, 'lcop_now', [cop, 0, samp_y, samp_x])
            utils.insert_data(DATABASE, 'ccop_now', [cop, 0, samp_y, samp_x])
            utils.insert_data(DATABASE, 'hcop_now', [cop, 0, samp_y, samp_x])

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
        kmeans = split_city.split_city(X)
        self.df[label_indices]['split_regions'] = kmeans.labels_
        most_crime = self.df[label_indices]['split_regions'].value_counts(). \
            index[0]
        self.crime_center = kmeans.cluster_centers_[most_crime]

    def move_cop(self, coptype, values):
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

    def update(self, coptype):
        '''
        INPUT: rcop, lcop, ccop, hcop
        OUTPUT: None

        moves all cops current position into move history
        '''
        utils.insert_tabletotable(DATABASE, coptype+'_now', coptype+'_moves')

    def get_crime(self, start_time, end_time, start_date, end_date, region):
        '''
        INPUT: dataframe, start time, end time, start date, end date
        OUTPUT: filtered dataframe

        Fetches crime that occured within a date interval
        '''
        label_indices = self.df['Region'] = region
        crime_startdate = self.df['Date'] >= start_date
        crime_enddate = self.df['Date'] <= end_date
        crime_start = self.df['Time'] >= start_time
        crime_end = self.df['Time'] <= start_time
        return self.df[crime_startdate & crime_enddate &
                       crime_start & crime_end & label_indices]
