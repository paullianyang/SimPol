'''
converts traffic.db into a csv
reads it into a dataframe and cleans it up
creates a dictionary of traffic by
split city region and
pickle it as pickle.pkl in data
'''
import utils
import pickle
import pandas as pd


def create_traffic_csv():
    sql = utils.sqlite('../data/traffic.db')
    # we want to avoid samples that have the same origin and dest
    # or are very close (less than 1min driving time)
    # Records without mins/secs for notrafficdur are routes
    # without driving information

    query = '''
        SELECT *
        FROM traffic2
        WHERE origin_lat <> dest_lat
        AND origin_long <> dest_long
        AND notraffic_dur LIKE '%min%'
        '''

    headers = ['utc_time', 'origin_lat', 'origin_long', 'dest_lat',
               'dest_long', 'dist', 'notraffic_dur', 'traffic_dur']
    sql.selecttocsv('../data/sf2014_traffic.csv', query, headers=headers)


def clean_traffic_csv():
    df = pd.read_csv('../data/sf2014_traffic.csv')
    df['notraffic_dur'] = df['notraffic_dur']. \
        apply(lambda x: int(x.strip('mins')))
    df['traffic_dur'] = df['traffic_dur']. \
        apply(lambda x: int(x.strip('mins')) if 'mins' in x else 0)
    df['traffic'] = df['traffic_dur'] - df['notraffic_dur']
    df['traffic'] = df['traffic'].apply(lambda x: 0 if x < 0 else x)
    return df


def estimate_traffic(df):
    '''
    INPUT: dataframe
    OUTPUT: None

    Pickles traffic dictionary by split_city region
    '''
    # label each traffic estimation by the region it was sampled from
    km = pickle.load(open('../data/split_sf.pkl', 'rb'))
    df['split_region'] = km.predict(df[['origin_long', 'origin_lat']])

    traffic = df[['traffic', 'split_region']]. \
        groupby(['split_region']).mean().to_dict()
    pickle.dump(traffic, open('../data/traffic.pkl', 'wb'))

if __name__ == '__main__':
    create_traffic_csv()
    df = clean_traffic_csv()
    estimate_traffic(df)
