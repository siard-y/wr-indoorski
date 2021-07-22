import datetime
import sqlite3
from sqlite3 import Error


def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)
        
    return conn


def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)



def insert_pulse(conn, pulse):
    """
    Insert a new pulse into the pulse table
    :param conn:
    :param pulse:
    :return: pulse id
    """
    sql = ''' INSERT INTO pulse(datum_on, datum_off)
              VALUES(?,?) '''
    cur = conn.cursor()
    cur.execute(sql, pulse)
    conn.commit()
    return cur.lastrowid



def main():
    database = r"/home/pi/IndoorSki/indoorski.db"

    # get a database connection
    conn = create_connection(database)
    with conn:
    
        # create table
        sql_create_table = """ CREATE TABLE IF NOT EXISTS pulse (
                                 datum_on timestamp PRIMARY KEY,
                                 datum_off timestamp
                               ); """
        create_table(conn, sql_create_table)
    
        # insert pulse
        pulse = (datetime.datetime.now(), datetime.datetime.now())
        pulse_id = insert_pulse(conn, pulse)
        print(pulse_id)
      

    if (conn):
        conn.close()
        print("sqlite connection is closed")


if __name__ == '__main__':
    main()