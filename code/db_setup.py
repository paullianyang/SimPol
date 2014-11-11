import sqlite3

def trafficdb():
    conn = sqlite3.connect('../data/traffic.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE traffic2
        (
        utc_time TEXT,
        origin_lat TEXT,
        origin_long TEXT,
        dest_lat TEXT,
        dest_long TEXT,
        dist TEXT,
        notraffic_dur TEXT,
        traffic_dur TEXT
        )
    ''')
    conn.commit()
    conn.close()

def simulationdb():
    conn = sqlite3.connect('../data/simulation.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE cops
        (
            id INT,
            init_lat REAL,
            init_long REAL,
            status TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE rcop_moves
        (
            id INT,
            utc INT,
            lat REAL,
            long REAL
        )
    ''')
    c.execute('''
        CREATE TABLE lcop_moves
        (
            id INT,
            utc INT,
            lat REAL,
            long REAL
        )
    ''')
    c.execute('''
        CREATE TABLE ccop_moves
        (
            id INT,
            utc INT,
            lat REAL,
            long REAL
        )
    ''')
    c.execute('''
        CREATE TABLE hcop_moves
        (
            id INT,
            utc INT,
            lat REAL,
            long REAL
        )
    ''')
    c.execute('''
        CREATE TABLE rcop_now
        (
            id INT,
            utc INT,
            lat REAL,
            long REAL
        )
    ''')
    c.execute('''
        CREATE TABLE lcop_now
        (
            id INT,
            utc INT,
            lat REAL,
            long REAL
        )
    ''')
    c.execute('''
        CREATE TABLE ccop_now
        (
            id INT,
            utc INT,
            lat REAL,
            long REAL
        )
    ''')
    c.execute('''
        CREATE TABLE hcop_now
        (
            id INT,
            utc INT,
            lat REAL,
            long REAL
        )
    ''')
    conn.commit()
    conn.close()

if __name__ == '__main__':
    trafficdb()
    simulationdb()
