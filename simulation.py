'''
Simulates cop patrol given a specified region and
displays response times for each patrol behavior
to determine the optimal patrol strategy
'''
from __future__ import division
import numpy as np
from code import utils
from code import split_city
from datetime import datetime
from scipy.spatial.distance import euclidean
import pickle
import pandas as pd
from code import kmeans
DATABASE = 'data/simulation.db'


class SimPol(object):
    def __init__(self, df, kmean):
        '''
        INPUT:
            df - DataFrame with columns: 'X', 'Y', 'Regions'
            kmean - kmean model
        OUTPUT: None

        Simulates cop patrol given kmean cluster
        '''
        self.center = None
        self.cops_num = None
        self.cop_types = ['rcop', 'lcop', 'hcop', 'ccop']
        # self.cop_types = ['rcop']
        self.crime_center = None
        self.df = self.clean_df(df)
        self.kmean = kmean
        self.patrol = {'rcop': self.patrol_random,
                       'hcop': self.patrol_home,
                       'ccop': self.patrol_crime,
                       'lcop': None}
        self.region = None
        self.response_time = None
        self.sql = utils.sqlite(DATABASE)
        self.sql.truncate_table('cops')
        self.tables = ['_moves', '_response', '_now']
        # for cop in self.cop_types:
        for cop in ['rcop', 'lcop', 'hcop', 'ccop']:
            for table in self.tables:
                self.sql.truncate_table(cop+table)

    def initiate_region(self, region):
        self.region = region
        self.center = self.kmean.cluster_centers_[self.region]
        self.df = self.df[self.df['Regions'] == self.region].copy()
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
            self.sql.insert_data('cops', [str(cop), str(samp_y), str(samp_x)])
            self.sql.insert_data('rcop_now',
                                 [str(cop), '0',
                                  str(samp_y), str(samp_x),
                                  '-1', "'available'"])
            self.sql.insert_data('lcop_now',
                                 [str(cop), '0',
                                  str(samp_y), str(samp_x),
                                  '-1', "'available'"])
            self.sql.insert_data('ccop_now',
                                 [str(cop), '0',
                                  str(samp_y), str(samp_x),
                                  '-1', "'available'"])
            self.sql.insert_data('hcop_now',
                                 [str(cop), '0',
                                  str(samp_y), str(samp_x),
                                  '-1', "'available'"])

    def random_coord(self):
        while True:
            index = np.random.choice(self.df.index.values)
            samp_y = self.df.loc[index, ['Y', 'X']][0]
            samp_x = self.df.loc[index, ['Y', 'X']][1]
            X = np.array([[samp_y, samp_x]])
            if self.kmean.predict(X) == self.region:
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
        X = self.df[['Y', 'X']]
        km = split_city.split_city(X)
        self.df['split_regions'] = km.labels_
        most_crime = self.df['split_regions'].value_counts().index[0]
        self.crime_center = km.cluster_centers_[most_crime]

    def move_cop(self, coptype,
                 cop_id, utc, cop_lat, cop_long, end_time, status):
        '''
        INPUT:
            coptype: rcop, lcop, ccop hcop
            cop id, utc, lat, long, end_time, status
        OUTPUT: None

        Moves cop position
        '''
        query = '''
            UPDATE %s_now
            SET utc = %d,
                lat = %f,
                long = %f,
                end_time = %d,
                status = %s
            WHERE id = %d
            ''' % (coptype, utc, cop_lat, cop_long, end_time, status, cop_id)
        self.sql.execute(query)

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
        df['split_regions'] = -1
        df['dtstring'] = df['Date'] + ' ' + df['Time']
        df['dt'] = df['dtstring']. \
            apply(lambda x: datetime.strptime(x, '%m/%d/%Y %H:%M'))
        df['unixtime'] = df['dt']. \
            apply(lambda x: utils.datetime_to_unixtime(x))
        df.pop('dt')
        df.pop('dtstring')
        return df

    def get_crime(self, start_time, end_time):
        '''
        INPUT: start time, end time
        OUTPUT: filtered dataframe

        Fetches crime that occured within a date interval
        '''
        crime_start = self.df['unixtime'] >= start_time
        crime_end = self.df['unixtime'] < end_time
        return self.df[crime_start & crime_end]

    def run(self, date_string):
        '''
        INPUT: YYYY-MM-DD Date String
        OUTPUT: None

        Runs Simulation for given date
        '''
        start_date = datetime.strptime(date_string, '%Y-%m-%d')
        start_utc = utils.datetime_to_unixtime(start_date)
        interval = 60*60  # each run is 60 minutes
        iterations = int((60*60*24)/interval)
        for i in range(iterations):
            print 'Iteration: ', i, ' out of ', iterations
            end_utc = start_utc + interval
            crime_df = self.get_crime(start_time=start_utc,
                                      end_time=end_utc)
            print 'Check Busy: ', i
            self.check_busy(start_utc)
            print 'Dispatch Cops: ', i
            self.dispatch_cops(crime_df, start_utc)
            print 'Patrol Cops: ', i
            self.patrol_cops(start_utc, interval)
            for cop in self.cop_types:
                self.update(cop)
            start_utc += interval

    def check_busy(self, start_utc):
        '''
        INPUT: unix timestamp
        OUTPUT: None

        checks if cops finish attending to crime and updates if they are
        '''
        query = '''
            UPDATE %s_now
            SET status='available'
            WHERE end_time <= %d
            AND status='busy'
            AND end_time > -1
            '''
        for cop in self.cop_types:
            self.sql.execute(query % (cop, start_utc))

    def get_cops(self, coptype, status='available'):
        '''
        INPUT: coptype - rcop, lcop, hcop, ccop
               status - available, busy
        OUTPUT: dataframe

        Returns a dataframe of available cops
        '''
        query = "SELECT * FROM %s_now WHERE status='%s'" % (coptype, status)
        return pd.io.sql.read_sql(query, self.sql.conn)

    def patrol_cops(self, start_utc, interval):
        '''
        INPUT: unix timestamp, interval
        OUTPUT: None

        Assigns cops to patrol
        '''
        for cop in self.cop_types:
            patrol = self.patrol[cop]
            cop_df = self.get_cops(cop)
            for row in range(len(cop_df)):
                cop_interval = interval
                cop_id = cop_df.ix[row]['id']
                cop_lat = cop_df.ix[row]['lat']
                cop_long = cop_df.ix[row]['long']
                if cop == 'lcop':
                    pass  # lcop does not patrol
                elif cop == 'rcop':
                    patrol_lat, patrol_long = patrol()
                    while patrol_lat == cop_lat and patrol_long == cop_long:
                        patrol_lat, patrol_long = patrol()
                    while cop_interval > 0:
                        cop_lat, cop_long, cop_interval = \
                            self.find_location(from_lat=cop_lat,
                                               from_long=cop_long,
                                               to_lat=patrol_lat,
                                               to_long=patrol_long,
                                               interval=cop_interval)
                        patrol_lat, patrol_long = patrol()
                else:
                    patrol_lat, patrol_long = patrol()
                    while cop_interval > 0:
                        if patrol_lat != cop_lat or patrol_long != cop_long:
                            cop_lat, cop_long, cop_interval = \
                                self.find_location(from_lat=cop_lat,
                                                   from_long=cop_long,
                                                   to_lat=patrol_lat,
                                                   to_long=patrol_long,
                                                   interval=cop_interval)
                            patrol_lat, patrol_long = patrol()
                        else:
                            break
                self.move_cop(cop, cop_id=cop_id,
                              utc=start_utc,
                              cop_lat=cop_lat,
                              cop_long=cop_long,
                              end_time=-1,
                              status="'available'")

    def find_location(self, from_lat, from_long, to_lat, to_long, interval):
        '''
        INPUT: origin latitude, origin longitude,
               destination latitude, destination longitude,
               time between simulation rounds (seconds)
        OUTPUT: destination latitude, destination longitude,
                seconds left in round

        find location of cops at end of round or end of destination
        whichever comes first
        '''
        osrm = utils.OSRM(from_lat=from_lat,
                          from_long=from_long,
                          to_lat=to_lat,
                          to_long=to_long,
                          gmaps=False)
        if osrm.r == 'Failed':
            print 'Failed'
            return from_lat, from_long, interval
        if osrm.duration() < interval:
            time_left = interval - osrm.duration()
            return to_lat, to_long, time_left
        else:
            start = osrm.route_geometry()
            next_step = osrm.route_geometry()[1:]
            interval_ratio = 1 - (osrm.duration()-interval)/osrm.duration()
            distances = []
            print 'from coord: ', from_lat, from_long
            print 'to coord: ', to_lat, to_long
            for i in range(len(next_step)):
                distances.append(euclidean(start[i], next_step[i]))
            for i in range(len(distances)):
                percent_travelled = sum(distances[:i+1])/sum(distances)
                if percent_travelled > interval_ratio:
                    break
            dest_lat = next_step[i][0]
            dest_long = next_step[i][1]
            print dest_lat, dest_long
            return dest_lat, dest_long, 0

    def dispatch_cops(self, crime_df, start_utc):
        '''
        INPUT: crime dataframe, unix timestamp
        OUTPUT: None

        assigns cops to crime for each cop type
        '''
        crime_locations = crime_df[['Y', 'X']].values
        for crime_lat, crime_long in crime_locations:
            crime_coord = (crime_lat, crime_long)
            for cop in self.cop_types:
                cop_df = self.get_cops(cop)
                if cop_df['id'].count() == 0:  # no cops available
                    break
                cop_df['cop_coord'] = cop_df['lat'].apply(lambda x: str(x)) + \
                    ',' + cop_df['long'].apply(lambda x: str(x))
                cop_df['distance_away'] = cop_df['cop_coord']. \
                    apply(lambda x:
                          kmeans.driving_distance((float(x.split(',')[0]),
                                                   float(x.split(',')[1])),
                                                  crime_coord))
                cop_id = cop_df.sort(columns='distance_away'). \
                    head(1)['id'].values[0]
                cop_lat = cop_df[cop_df['id'] == cop_id]['lat'].values
                cop_long = cop_df[cop_df['id'] == cop_id]['long'].values
                drive_dur = utils.OSRM(from_lat=cop_lat,
                                       from_long=cop_long,
                                       to_lat=crime_lat,
                                       to_long=crime_long,
                                       gmaps=False).duration()
                self.sql.insert_data('%s_response' % cop,
                                     ["'%d'" % cop_id,
                                      "'%d'" % drive_dur])
                end_time = start_utc + drive_dur + self.response_time
                self.move_cop(cop, cop_id=cop_id,
                              utc=start_utc,
                              cop_lat=crime_lat,
                              cop_long=crime_long,
                              end_time=end_time,
                              status="'busy'")


def preload():
    df = pd.read_csv('data/sfpd_incident_2014.csv')
    km = pickle.load(open('data/trained_km2.pkl', 'rb'))
    km.verbose = False
    labels = pickle.load(open('data/trained_prediction.pkl', 'rb'))
    df['Regions'] = labels
    return df, km


if __name__ == '__main__':
    df, km = preload()
    sim = SimPol(df, km)
    sim.initiate_region(7)
    sim.initiate_cops(cops_num=20, response_time=60)
    sim.run('2014-06-29')
