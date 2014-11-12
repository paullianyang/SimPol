import sqlite3
import requests


def insert_data(dbloc, tablename, values):
    '''
    INPUT:
        str sqlite db location,
        str sqlite tablename,
        str list of columns,
        str list of values matching to columns
    OUTPUT: None

    inserts data into sqlite3 db
    '''
    conn = sqlite3.connect(dbloc)
    c = conn.cursor()
    query = '''
        INSERT INTO %s
        VALUES (
            %s
        )
        ''' % (tablename, ','.join(values))

    c.execute(query)
    conn.commit()
    conn.close()


def insert_tabletotable(dbloc, from_table, into_table):
    '''
    INPUT: str db location,
           tablename values are from,
           tablename values are inserted to
    OUTPUT: None

    inserts data from one table to another
    '''
    conn = sqlite3.connect(dbloc)
    c = conn.cursor()
    query = '''
        INSERT INTO %s
        SELECT * FROM %s
        ''' % (from_table, into_table)
    c.execute(query)
    conn.commit()
    conn.close()


def truncate_table(dbloc, tablename):
    '''
    INPUT: str db location, tablename to truncate
    OUTPUT: None

    deletes all data from one table
    '''
    conn = sqlite3.connect(dbloc)
    c = conn.cursor()
    query = 'DELETE FROM %s' % tablename
    c.execute(query)
    conn.commit()
    conn.close()


def execute(dbloc, query):
    '''
    INPUT: query to execute
    OUTPUTL None
    '''
    conn = sqlite3.connect(dbloc)
    c = conn.cursor()
    c.execute(query)
    conn.commit()
    conn.close()


class osrm(object):
    def __init__(self, from_lat, from_long, to_lat, to_long,
                 ip='0.0.0.0', port=5000):
        '''
        INPUT:
            from_lat, from_long - starting coordinates
            to_lat, to_long - destination coordinates
            ip - ip address of where osrm is running on
            port - port to connect to osrm
        OUTPUT: None

        uses OSRM (https://github.com/Project-OSRM/osrm-backend/wiki/Server-api)
        to find driving directions, and calculate distance between 2 coordinates
        '''
        self.from_lat = from_lat
        self.from_long = from_long
        self.to_lat = to_lat
        self.to_long = to_long
        self.ip = ip
        self.port = port
        self.url = "http://%s:%d/viaroute?loc=%f,%f&loc=%f,%f&compression=false" \
                   % (ip, port, from_lat, from_long, to_lat, to_long)
        self.r = requests.get(self.url)

    def distance(self):
        return self.r.json()['route_summary']['total_distance']

    def duration(self):
        return self.r.json()['route_summary']['total_time']

    def route_geometry(self):
        return self.r.json()['route_geometry']


def log(text):
    floc = '../data/log'
    f = open(floc, 'a')
    f.write(text+'\n')
    f.close()
