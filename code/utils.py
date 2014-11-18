'''
utility methods to manipulate
and fetch data
'''
import sqlite3
import requests
import keys
import calendar


class sqlite(object):
    def __init__(self, dbloc):
        '''
        INPUT: database location'
        OUTPUT: None

        Establish a connction to sqlite3 db
        '''
        self.conn = sqlite3.connect(dbloc)
        self.c = self.conn.cursor()

    def insert_data(self, tablename, values):
        '''
        INPUT:
            str sqlite tablename,
            str list of values matching to table field order
        OUTPUT: None

        inserts data into sqlite3 db
        '''
        query = '''
            INSERT INTO %s
            VALUES (
                %s
            )
            ''' % (tablename, ','.join(values))
        self.c.execute(query)
        self.conn.commit()

    def insert_tabletotable(self, from_table, into_table):
        '''
        INPUT: str db location,
               tablename values are from,
               tablename values are inserted to
        OUTPUT: None

        inserts data from one table to another
        '''
        query = '''
            INSERT INTO %s
            SELECT * FROM %s
            ''' % (into_table, from_table)
        self.c.execute(query)
        self.conn.commit()

    def truncate_table(self, tablename):
        '''
        INPUT: str db location, tablename to truncate
        OUTPUT: None

        deletes all data from one table
        '''
        query = 'DELETE FROM %s' % tablename
        self.c.execute(query)
        self.conn.commit()

    def execute(self, query):
        '''
        INPUT: query to execute
        OUTPUTL None
        '''
        self.c.execute(query)
        self.conn.commit()

    def selecttocsv(self, fname, query, headers=False):
        '''
        INPUT: filename to save to,
               query string
               list of header names (optional)
        OUTPUT: None

        Saves a query to csv
        '''
        results = self.c.execute(query)
        with open(fname, 'wb') as f:
            if headers:
                f.write(','.join(headers))
                f.write('\n')
            for r in results:
                f.write(','.join(r))
                f.write('\n')

    def close(self):
        self.conn.close()


class GMaps_Matrix(object):
    def __init__(self, from_lat, from_long, to_lat, to_long):
        '''
        INPUT:
            from_lat, from_long - starting coordinates
            to_lat, to_long - destination coordinates
        OUTPUT: None

        GMAP Distance Matrix API
        https://developers.google.com/maps/documentation/distancematrix/
        Find driving directions, and calculate distance between them
        '''
        self.from_lat = from_lat
        self.from_long = from_long
        self.to_lat = to_lat
        self.to_long = to_long
        self.r = self.get_requests()
        try:
            if self.r.json()['status'] != 'OK':
                # sometimes fails with unknown error
                # lets try it a second time
                print self.r.json()['status']
                print self.from_lat, self.from_long, self.to_lat, self.to_long
                self.r = self.get_requests()
        except ValueError:
            print self.r
            print self.fromt_lat, self.from_long, self.to_lat, self.to_long

    def get_requests(self):
        url = 'https://maps.googleapis.com/maps/api/distancematrix/json?origins=%f,%f&destinations=%f,%f&key=%s' \
              % (self.from_lat, self.from_long,
                 self.to_lat, self.to_long,
                 keys.gmaps_apikey())
        return requests.get(url)

    def distance(self):
        return self.r.json()['rows'][0]['elements'][0]['distance']['value']

    def duration(self):
        return self.r.json()['rows'][0]['elements'][0]['duration']['value']


class OSRM(object):
    def __init__(self, from_lat, from_long, to_lat, to_long,
                 ip='0.0.0.0', port=5000, gmaps=True):
        '''
        INPUT:
            from_lat, from_long - starting coordinates
            to_lat, to_long - destination coordinates
            ip - ip address of where osrm is running on
            port - port to connect to osrm
            gmaps - T/F to allow use of gmaps API
        OUTPUT: None

        OSRM: (https://github.com/Project-OSRM/osrm-backend/wiki/Server-api)
        Find driving directions, and calculate distance between 2 coordinates
        '''
        self.from_lat = from_lat
        self.from_long = from_long
        self.to_lat = to_lat
        self.to_long = to_long
        self.ip = ip
        self.port = port
        self.gmaps = gmaps
        self.r, self.method = self.driving_directions()

    def driving_directions(self):
        status, r = self.get_request()
        if status == 'Cannot find route between points':
            self.from_lat, self.from_long = \
                self.find_nearest(self.from_lat, self.from_long)
            self.to_lat, self.to_long = \
                self.find_nearest(self.to_lat, self.to_long)
            status, r = self.get_request()

        # Certain Coordinates don't exist in OSRM
        # Fallback to GMaps API when this happens
        if status == 'Cannot find route between points' and self.gmaps:
           print 'defaulting to gmaps'
           gmaps = GMaps_Matrix(self.from_lat, self.from_long,
                                self.to_lat, self.to_long)
           return gmaps, 'gmaps'

        # use only osrm
        if status == 'Cannot find route between points':
            print 'Failed'
            print self.from_lat, ',', self.from_long
            print self.to_lat, ',', self.to_long
            return 'Failed', 'osrm'
        return r, 'osrm'

    def get_request(self):
        url = "http://%s:%d/viaroute?loc=%f,%f&loc=%f,%f&compression=false" \
              % (self.ip, self.port,
                 self.from_lat, self.from_long,
                 self.to_lat, self.to_long)
        r = requests.get(url)
        return r.json()['status_message'], r

    def distance(self):
        if self.method == 'gmaps':
            return self.r.distance()
        else:
            try:
                distance = self.r.json()['route_summary']['total_distance']
            except AttributeError:
                distance = 'Failed'
            return distance

    def duration(self):
        if self.method == 'gmaps':
            return self.r.duration()
        else:
            return self.r.json()['route_summary']['total_time']

    def route_geometry(self):
        if self.method == 'gmaps':
            return None
        else:
            return self.r.json()['route_geometry']

    def find_nearest(self, coordlat, coordlong):
        '''
        INPUT: latitude(float), longitude(float)
        OUTPUT: latitude(float), longitude(float)

        Find nearest coordinate available for routing
        '''
        url = "http://%s:%d/nearest?loc=%f,%f" \
              % (self.ip, self.port, coordlat, coordlong)
        r = requests.get(url)
        coord = r.json()['mapped_coordinate']
        return coord[0], coord[1]


def datetime_to_unixtime(dt):
    '''
    INPUT: datetime object
    OUTPUT: unixtime

    converts datetime to number of seconds since 1970
    '''
    return calendar.timegm(dt.utctimetuple())


def log(text):
    floc = '../data/log'
    f = open(floc, 'a')
    f.write(text+'\n')
    f.close()
