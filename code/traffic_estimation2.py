import requests
import pickle
import pandas as pd
import numpy as np
import time
import utils
import math

API_KEY = 'AIzaSyAms5uhYxJnB-X2vkEnufTmuoAgEBDi5xg'
DATABASE = '/home/paul/zipfian/capstone-project/data/traffic.db'

kmean = pickle.load(open('../data/split_sf.pkl', 'rb'))
df = pd.read_csv('../data/sfpd_incident_2014.csv')
df['Region'] = kmean.predict(df[['X','Y']])
regions = df['Region'].unique()
sec_interval = 3600
sec_delay = 600
log = '/home/paul/zipfian/capstone-project/data/log'

def get_params(df):
    label_indices = df['Region'] == region
    coord = df[['Y', 'X']][label_indices].values
    cur_utc = int(time.time())
    samp_coord = np.random.choice(np.arange(coord.shape[0]), size=2)
    origin = str(coord[samp_coord[0]][0]) + ',' + str(coord[samp_coord[0]][1])
    destination = str(coord[samp_coord[1]][0]) + ',' + str(coord[samp_coord[1]][1])
    return cur_utc, origin, destination

if __name__ == '__main__':
    while True:
        if (math.floor(time.time()) - sec_delay) % sec_interval == 0:
            for region in regions:
                for i in range(2):
                    print i
                    cur_utc, origin, destination = get_params(df)
                    if i == 0:
                        traffic_url = 'https://maps.googleapis.com/maps/api/distancematrix/json?origins=%s&destinations=%s&key=%s&departure_time=%d' % (origin, destination, API_KEY, cur_utc)
                        notraffic_url = 'https://maps.googleapis.com/maps/api/distancematrix/json?origins=%s&destinations=%s&key=%s' % (origin, destination, API_KEY)
                    else:
                        traffic_url = 'https://maps.googleapis.com/maps/api/directions/json?origin=%s&destination=%s&key=%s&departure_time=%d' % (origin, destination, API_KEY, cur_utc)
                        notraffic_url = 'https://maps.googleapis.com/maps/api/directions/json?origin=%s&destination=%s&key=%s' % (origin, destination, API_KEY)
                    r_traffic = requests.get(traffic_url)
                    r_notraffic = requests.get(notraffic_url)
                    if r_traffic.status_code == 200 and r_notraffic.status_code == 200:
                        if i == 0:
                            traffic_distance = r_traffic.json()['rows'][0]['elements'][0]['distance']['value']
                            traffic_duration = r_traffic.json()['rows'][0]['elements'][0]['duration']['value']
                            notraffic_distance = r_notraffic.json()['rows'][0]['elements'][0]['distance']['value']
                            notraffic_duration = r_notraffic.json()['rows'][0]['elements'][0]['duration']['value']
                        else:
                            traffic_distance = r_traffic.json()['routes'][0]['legs'][0]['distance']['value']
                            traffic_duration = r_traffic.json()['routes'][0]['legs'][0]['duration']['value']
                            notraffic_distance = r_notraffic.json()['routes'][0]['legs'][0]['distance']['value']
                            notraffic_duration = r_notraffic.json()['routes'][0]['legs'][0]['duration']['value']
                        if traffic_distance != notraffic_distance:
                            f = open(log, 'a')
                            f.write('%s: paths not the same\n' % cur_utc)
                            f.write('Origin: %s\nDestination: %s\n' % (origin, destination))
                            f.write('Traffic Distance: %d\n' % traffic_distance)
                            f.write('No Traffic Distance: %d\n' % notraffic_distance)
                            f.close()
                        else:
                            traffic = traffic_duration - notraffic_duration
                            utils.insert_data(DATABASE, 'traffic2', [str(cur_utc), origin, destination, str(traffic_distance), str(notraffic_duration), str(traffic)])
                            f = open(log, 'a')
                            f.write('%s: insert region %s\n' % (cur_utc, region))
                            f.close()
                    else:
                        f = open(log, 'a')
                        f.write('%s: Error Codes %s %s' % (cur_utc, r_traffic.status_code, r_notraffic.status_code))
                        f.close()
        else:
            time.sleep(1)

