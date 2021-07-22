#!/usr/bin/python

import RPi.GPIO as GPIO            # import RPi.GPIO module  
import os, datetime, atexit, time, urllib2,sys
import time                        # Get sleep function to delay loop 
import decimal
 
GPIO.setmode(GPIO.BOARD)           # choose BCM or BOARD  
GPIO.setup(7, GPIO.IN)             # set pin 7 as input   

counter = 0
duration = 0
last_pulse = datetime.datetime.now()

filename = '/home/pi/IndoorSki/pulse2txt/' + datetime.datetime.now().strftime('%Y-%m-%d %H.%M.%S') + '.txt'


def insert_pulse(pulse):
    # Write 1 line
    line = pulse
    f1 = open(filename, "a") #append mode
    f1.write('\t'.join(line) + '\n')
    f1.close()
    print(line)




#Function that "add_event_detect" runs at input change
def pulse_detected(channel):
    if GPIO.input(channel) > 0.5:  # input is high
        # calculate
        global last_pulse
        global counter
        global duration
        
        delta = datetime.datetime.now() - last_pulse    
        duration = int(delta.total_seconds() * 1000000) # milliseconds
        last_pulse = datetime.datetime.now()
    
        # insert pulse
        pulse = (datetime.datetime.now().strftime("%Y-%m-%d %H.%M.%S.%f"), str(counter), str(duration))
                
        # new connection
        insert_pulse(pulse)

        # Display
        counter += 1          




#On input change, run input_Chng function
GPIO.add_event_detect(7, GPIO.RISING, callback=pulse_detected, bouncetime=3)


try:  
    while True:  
      # print('Last meting', meting_nr, ' - tijd ', str(datetime.datetime.now()), ' - counter', counter, ' - duration', duration)
      time.sleep(100)

except KeyboardInterrupt:          # trap a CTRL+C keyboard interrupt  
    GPIO.cleanup()                 # resets all GPIO ports used by this program 

