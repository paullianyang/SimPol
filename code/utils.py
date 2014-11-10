import sqlite3

def insert_data(dbloc, tablename, values):
    '''
    INSERT:
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

def log(text):
    floc = '../data/log'
    f = open(floc, 'a')
    f.write(text+'\n')
    f.close()
