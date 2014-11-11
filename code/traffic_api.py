import requests
import pickle
import pandas as pd
import numpy as np
import time
import sqlite3
import math

API_KEY = 'AIzaSyAms5uhYxJnB-X2vkEnufTmuoAgEBDi5xg'

kmean = pickle.load(open('../data/split_sf.pkl', 'rb'))
df = pd.read_csv('../data/sfpd_incident_2014.csv')
df['Region'] = kmean.predict(df[['X','Y']])
regions = df['Region'].unique()
sec_interval = 3600
sec_delay = 600

def insert_data(ut_time, origin, destination, distance, duration):
    '''
    INSERT:
        utc time (str),
        lat/long with comma (str),
        lat/long with comma (str),
        distance in meters (str),
        duration in seconds (str)
    OUTPUT: None

    inserts data into table traffic in traffic.db
    '''
    conn = sqlite3.connect('../data/traffic.db')    
    origin_lat, origin_long = origin.split(',')
    dest_lat, dest_long = destination.split(',')
    
    c = conn.cursor()
    c.execute('''
        INSERT INTO traffic
        VALUES (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s
        )
        ''' % (ut_time, origin_lat, origin_long, dest_lat, dest_long, distance, duration)
    )
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    while True:
        if (math.floor(time.time()) - sec_delay) % sec_interval == 0:
            for region in regions:
                for i in range(2):
                    label_indices = df['Region'] == region
                    coord = df[['Y', 'X']][label_indices].values
                    cur_utc = int(time.time())
                    samp_coord = np.random.choice(np.arange(coord.shape[0]), size=2)
                    origin = str(coord[samp_coord[0]][0]) + ',' + str(coord[samp_coord[0]][1])
                    destination = str(coord[samp_coord[1]][0]) + ',' + str(coord[samp_coord[1]][1])
                    request_url = 'https://maps.googleapis.com/maps/api/distancematrix/json?origins=%s&destinations=%s&key=%s&departure_time=%d' % (origin, destination, API_KEY, cur_utc)
                    r = requests.get(request_url)
                    distance = r.json()['rows'][0]['elements'][0]['distance']['value']
                    duration = r.json()['rows'][0]['elements'][0]['duration']['value']
                    insert_data(cur_utc, origin, destination, distance, duration)
                    print 'inserted %s at time %s' % (region, cur_utc)
        else:
            time.sleep(1)


