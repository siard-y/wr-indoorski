#!/usr/bin/python

import RPi.GPIO as GPIO            # import RPi.GPIO module  
import os, datetime, atexit, time, urllib2,sys
import time                        # Get sleep function to delay loop 
import decimal
import requests

# GPIO init
GPIO.setmode(GPIO.BOARD)           # choose BCM or BOARD  
GPIO.setup(7, GPIO.IN)             # set pin 7 as input   

# Vars
meting_started = False
meting_start = datetime.datetime.now()
prev_pulse = datetime.datetime.now()
omtrek_rol_m = 1.274
counter = 0
duration = 0
filename = ""


def insert_pulse(pulse):
    # Write 1 line
    line = pulse
    f1 = open(filename, "a") #append mode
    f1.write('\t'.join(line) + '\n')
    f1.close()
    print(line)


#Function that "add_event_detect" runs at input change
def pulse_detected(pin):
    if GPIO.input(pin) > 0.5:  # input is high
        # Global Vars
        global prev_pulse
        global counter
        global duration
        global filename
        global meting_start
        global meting_started
        global omtrek_rol_m

        # Display
        counter += 1          
        
        # Eerste puls, meting start 
        if meting_started == False:
            meting_start = datetime.datetime.now()
            filename = '/home/pi/IndoorSki/pulse2txt/' + datetime.datetime.now().strftime('%Y-%m-%d %H.%M.%S') + '.txt'
            meting_started = True
        
        # Duration last pulse
        diff_in_milli_secs = (datetime.datetime.now() - prev_pulse).total_seconds() * 1000   
        prev_pulse = datetime.datetime.now()

        # Huidige Snelheid meter per seconde
        snelheid = omtrek_rol_m*1000 / diff_in_milli_secs
        snelheid = round(snelheid, 2)

        # Gem Snelheid
        gem_snelheid = 0   # meter per seconde
        delta = datetime.datetime.now() - meting_start    
        if delta.total_seconds() > 0:
            gem_snelheid = (omtrek_rol_m * counter) / delta.total_seconds()
            gem_snelheid = round(gem_snelheid, 2)

        # insert pulse
        pulse = (datetime.datetime.now().strftime("%Y-%m-%d %H.%M.%S.%f"), str(counter), str(diff_in_milli_secs), str(snelheid), str(gem_snelheid))

        # new connection
        insert_pulse(pulse)
        
        # Send message
        try:
            url = "http://192.168.1.60:8080/json.htm?username=YmVoZWVy&password=TjNROVh2dE02NQ==&type=command&param=udevice&idx=278&nvalue=&svalue="
            requests.get(url + "snelheid=" + str(snelheid) + "ms - gem_snelheid=" + str(gem_snelheid) + "ms", timeout=1)
        except requests.exceptions.ReadTimeout: 
            pass
        



#On input change, run input_Chng function
GPIO.add_event_detect(7, GPIO.RISING, callback=pulse_detected, bouncetime=100)



try:  
    while True:  
      # print('Last meting', meting_nr, ' - tijd ', str(datetime.datetime.now()), ' - counter', counter, ' - duration', duration)
      time.sleep(10)

except KeyboardInterrupt:          # trap a CTRL+C keyboard interrupt  
    GPIO.cleanup()                 # resets all GPIO ports used by this program 

