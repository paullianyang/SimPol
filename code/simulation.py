'''
Simulates cop patrol given a specified region and
displays response times for each patrol behavior
to determine the optimal patrol strategy
'''
from __future__ import division
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
        self.center = None
        self.cops_num = None
        self.cop_types = ['rcop', 'lcop', 'hcop', 'ccop']
        self.crime_center = None
        self.df = self.clean_df(df)
        self.kmean = kmean
        self.min_y = None
        self.max_y = None
        self.min_x = None
        self.max_x = None
        self.patrol = {'rcop': self.patrol_random,
                       'hcop': self.patrol_home,
                       'ccop': self.patrol_crime}
        self.region = None
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
        X = self.df[label_indices][['Y', 'X']]
        km = split_city.split_city(X)
        self.df[label_indices]['split_regions'] = km.labels_
        most_crime = self.df[label_indices]['split_regions'].value_counts(). \
            index[0]
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
        df['split_region'] = -1
        df['unixtime'] = df['Date'] + ' ' + df['Time']
        df['unixtime'] = df['unixtime']. \
            apply(lambda x: datetime.strptime(x, '%m/%d/%Y %H:%M'))
        df['unixtime'] = df['unixtime']. \
            apply(lambda x: utils.datetime_to_unixtime(x))
        df['X'] = df['X'].apply(lambda x: str(x))
        df['Y'] = df['Y'].apply(lambda x: str(x))
        return df

    def get_crime(self, start_time, end_time):
        '''
        INPUT: start time, end time
        OUTPUT: filtered dataframe

        Fetches crime that occured within a date interval
        '''
        label_indices = self.df['Region'] = self.region
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
                                      end_time=end_utc)
            self.check_busy(start_utc)
            self.dispatch_cops(crime_df, start_utc)
            self.patrol_cops(start_utc, interval)
            self.update()

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
                cop_id = cop_df.ix[0]['id']
                cop_lat = cop_df.ix[0]['lat']
                cop_long = cop_df.ix[0]['long']
                if cop == 'lcop':
                    pass  # lcop does not patrol
                elif cop == 'rcop':
                    patrol_lat, patrol_long = patrol()
                    while patrol_lat == cop_lat and patrol_long == cop_long:
                        patrol_lat, patrol_long = patrol()
                    while interval > 0:
                        cop_lat, cop_long, interval = \
                            self.find_location(from_lat=cop_lat,
                                               from_long=cop_long,
                                               to_lat=patrol_lat,
                                               to_long=patrol_long,
                                               interval=interval)
                else:
                    patrol_lat, patrol_long = patrol()
                    if patrol_lat != cop_lat or patrol_long != cop_long:
                        while interval > 0:
                            cop_lat, cop_long, interval = \
                                self.find_location(from_lat=cop_lat,
                                                   from_long=cop_long,
                                                   to_lat=patrol_lat,
                                                   to_long=patrol_long,
                                                   interval=interval)
                self.move_cop(cop, cop_id=cop_id,
                              utc=start_utc,
                              cop_lat=cop_lat,
                              cop_long=cop_long,
                              end_time=-1,
                              status='available')

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
                          to_long=to_long)
        if osrm.duration() < interval:
            time_left = interval - osrm.duration()
            return to_lat, to_long, time_left
        else:
            start = osrm.route_geometry()
            next_step = osrm.route_geometry()[1:]
            duration = 0
            for i in range(len(next_step)):
                # there's a bug with ORSM route geometrys
                # where a destination on an intersection may
                # be interpretted heading in another direction
                # a hack will be to take flip the directions and
                # take the one with the smaller duration
                step_dur = utils.OSRM(from_lat=start[i][0],
                                      from_long=start[i][1],
                                      to_lat=next_step[i][0],
                                      to_long=next_step[i][1]).duration()
                step_dur2 = utils.OSRM(to_lat=start[i][0],
                                       to_long=start[i][1],
                                       from_lat=next_step[i][0],
                                       from_long=next_step[i][1]).duration()
                step_dur = min(step_dur, step_dur2)
                if duration+step_dur < interval:
                    duration += step_dur
                    ratio = 1
                else:
                    ratio = (duration+step_dur)/interval
                    duration = interval
                    break
            dest_lat = next_step[i][0]*ratio
            dest_long = next_step[i][1]*ratio
            time_left = interval - duration
            return dest_lat, dest_long, time_left

    def dispatch_cops(self, crime_df, start_utc):
        '''
        INPUT: crime dataframe, unix timestamp
        OUTPUT: None

        assigns cops to crime for each cop type
        '''
        crime_df['crime_coord'] = crime_df['Y'] + ',' + crime_df['X']
        crime_locations = crime_df['crime_coord'].values
        for crime_loc in crime_locations:
            for cop in self.cop_types:
                cop_df = self.get_cops(cop)
                if cop_df['id'].count() != 0:  # no cops available
                    break
                cop_df['cop_coord'] = cop_df['lat'] + ',' + cop_df['long']
                cop_df['time_away'] = cop_df['cop_coord']. \
                    apply(lambda x: kmeans.driving_distance(x.split(),
                                                            crime_loc.split()))
                cop_id = cop_df.sort(columns='time_away').head()['id'].values
                drive_dur = cop_df[cop_df['id'] == cop_id]['time_away'].values
                end_time = start_utc + drive_dur + self.response_time
                self.move_cop(cop, cop_id=cop_id,
                              utc=start_utc,
                              cop_lat=crime_loc.split(',')[0],
                              cop_long=crime_loc.split(',')[1],
                              end_time=end_time,
                              status='busy')


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
    sim.run()
