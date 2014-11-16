'''
methods to webscrap gmaps traffic data
and store it into a sqlite database
'''
import requests
import pickle
import pandas as pd
import numpy as np
import time
import utils
import math
from bs4 import BeautifulSoup


def get_params(df, region):
    '''
    INPUT: dataframe, split city region
    OUTPUT: current utc, lat/long of origin, lat/long of destination

    Sample 2 crime locations as origin/destination and output cleaned
    parameters for traffic estimation
    '''
    label_indices = df['Region'] == region
    coord = df[['Y', 'X']][label_indices].values
    cur_utc = int(time.time())
    samp_coord = np.random.choice(np.arange(coord.shape[0]), size=2)
    origin = str(coord[samp_coord[0]][0]) + ',' + str(coord[samp_coord[0]][1])
    destination = str(coord[samp_coord[1]][0]) + ',' + \
        str(coord[samp_coord[1]][1])
    # avoid sampling same crime locations
    while origin == destination:
        samp_coord = np.random.choice(np.arange(coord.shape[0]), size=2)
        origin = str(coord[samp_coord[0]][0]) + ',' + \
            str(coord[samp_coord[0]][1])
        destination = str(coord[samp_coord[1]][0]) + ',' + \
            str(coord[samp_coord[1]][1])
    return cur_utc, origin, destination


def scrape_gmaps(cur_utc, origin, destination):
    '''
    INPUT: current utc, lat/long origin, lat/long destination
    OUTPUT: distance (str),
            duration without traffic (str),
            duration with traffic (str)

    Scrapes google map directions and return distance/duration metrics
    '''

    url = "https://www.google.com/maps/dir/'%s'/'%s'/" % (origin, destination)
    r = requests.get(url)
    distance = -1
    traffic_dur = -1
    notraffic_dur = -1
    count = 0
    if r.status_code == 200:
        soup = BeautifulSoup(r.text, 'html.parser')
        for line in soup.find_all('span'):
            cleaned_line = str(line).replace('<span>', '').replace('</span>', '').\
                replace('In current traffic:', '').replace(' ', '')
            count -= 1
            if count == 2:
                distance = "'" + cleaned_line + "'"
            elif count == 1:
                notraffic_dur = "'" + cleaned_line + "'"
            elif count == 0:
                if 'span' in cleaned_line:
                    traffic_dur = notraffic_dur
                else:
                    traffic_dur = "'" + cleaned_line + "'"
                break
            if 'Hideoptions' in cleaned_line:
                count = 3
    else:
        error = '%s ERROR: scrape_gmaps with status code %s\norigin - %s\ndestination - %s'\
                % (cur_utc, r.status_code, origin, destination)
        utils.log(error)
    return distance, notraffic_dur, traffic_dur


def run():
    '''
    Randomly choose crime coordinates from SF split into
    50 equidistant regions and find traffic information
    by webscrapping the gmaps site.
    *Note* Ip gets halted at around 900 consecutive requests
    I'm going to try a very conversative number of 200 requests
    every hour (4 samples from each region)
    '''
    DATABASE = '../data/traffic.db'
    kmean = pickle.load(open('../data/split_sf.pkl', 'rb'))
    df = pd.read_csv('../data/sfpd_incident_2014.csv')
    df['Region'] = kmean.predict(df[['X', 'Y']])
    regions = df['Region'].unique()
    # run every 10 minutes pass every hour
    sec_interval = 3600  # one hour
    sec_delay = 600  # 10 minutes
    # number of samples to take
    sample_size = 4

    while True:
        if (math.floor(time.time()) - sec_delay) % sec_interval == 0:
            sql = utils.sqlite(DATABASE)
            for region in regions:
                for i in range(sample_size):
                    cur_utc, origin, destination = get_params(df, region)
                    distance, notraffic_dur, traffic_dur = \
                        scrape_gmaps(cur_utc, origin, destination)
                    if distance != -1.0:
                        sql.insert_data(DATABASE, 'traffic2',
                                        [str(cur_utc),
                                         origin, destination,
                                         distance,
                                         notraffic_dur, traffic_dur])
                        sql.close()
                        utils.log('Insert Region: %s' % region)
        else:
            time.sleep(1)

if __name__ == '__main__':
    while True:
        try:
            run()
        except:
            pass
