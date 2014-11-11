import sqlite3

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
    INPUT: str db location, tablename values are from, tablename values are inserted to
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

def log(text):
    floc = '../data/log'
    f = open(floc, 'a')
    f.write(text+'\n')
    f.close()
