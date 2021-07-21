#!/usr/bin/python
import sqlite3
from sqlite3 import Error

import RPi.GPIO as GPIO            # import RPi.GPIO module  
import os, datetime, atexit, time, urllib2,sys
import time                        # Get sleep function to delay loop 
 
GPIO.setmode(GPIO.BOARD)           # choose BCM or BOARD  
GPIO.setup(7, GPIO.IN)             # set pin 7 as input   

counter = 0
meting_nr = 1
duration = 0
last_pulse = datetime.datetime.now()


def get_connection():
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    try:
        conn = sqlite3.connect(r"/home/pi/IndoorSki/indoorski.db")
    
    except Error as e:
        print(e)
    
    return conn



def create_table():
    sql = """ CREATE TABLE IF NOT EXISTS pulse (
                datum       TIMESTAMP PRIMARY KEY
                                      DEFAULT (CURRENT_TIMESTAMP),
                meting_nr   INTEGER   DEFAULT (0),
                counter     INTEGER   DEFAULT (0), 
                duration    INTEGER   DEFAULT (0)
             ); """
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(sql)
        conn.commit()
        conn.close()
    except Error as e:
        print(e)




def get_new_meting_nr():
    sql = ''' SELECT ifnull(meting_nr, 0) FROM pulse ORDER BY meting_nr DESC LIMIT 1 '''
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(sql)
    global meting_nr
    row = cur.fetchone()
    if row is None:
        meting_nr = 1
    else:      
        meting_nr = row[0] + 1
    conn.close()
    return meting_nr




def insert_pulse(pulse):
    """
    Insert a new pulse into the pulse table
    :param conn:
    :param pulse:
    :return: pulse id
    """
    sql = ''' INSERT INTO pulse(datum, meting_nr, counter, duration)
              VALUES(?,?,?,?) '''
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(sql, pulse)
    conn.commit()
    conn.close()
    print('New pulse - meting_nr ', str(pulse[0]), ' - meting ', pulse[1], ' - counter', pulse[2], ' - duration', pulse[3])




#Function that "add_event_detect" runs at input change
def pulse_detected(channel):
    global counter
    if GPIO.input(channel) > 0.5:  # input is high
        # calculate
        global last_pulse
        global meting_nr
        global counter
        global duration
        
        delta = datetime.datetime.now() - last_pulse    
        duration = int(delta.total_seconds() * 1000000) # milliseconds
        last_pulse = datetime.datetime.now()
    
        # insert pulse
        pulse = (datetime.datetime.now(), meting_nr, counter, duration)
                
        # new connection
        pulse_id = insert_pulse(pulse)

        # Display
        counter += 1          





# create table
create_table()

# get last meting
meting_nr = get_new_meting_nr()


#On input change, run input_Chng function
GPIO.add_event_detect(7, GPIO.RISING, callback=pulse_detected, bouncetime=3)


try:  
    while True:  
      # print('Last meting', meting_nr, ' - tijd ', str(datetime.datetime.now()), ' - counter', counter, ' - duration', duration)
      time.sleep(1)

except KeyboardInterrupt:          # trap a CTRL+C keyboard interrupt  
    GPIO.cleanup()                 # resets all GPIO ports used by this program 

