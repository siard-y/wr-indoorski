#!/usr/bin/python
import RPi.GPIO as GPIO  # import RPi.GPIO module
import json
import os, datetime, atexit, time, sys
import requests
import sys
import time  # Get sleep function to delay loop

# generate random floating point values
from random import seed
from random import random

# GPIO init
GPIO.setmode(GPIO.BOARD)  # choose BCM or BOARD
GPIO.setup(7, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # set pin 7 as input

# Settings
last_meting_folder = '/home/pi/IndoorSki/pulse2txt/lastmeting/'

omtrek_rol_m = 1.274

# Vars
counter = 0
counter_totaal = 0
filename_data = ''
meting_start = datetime.datetime.now()
nieuwe_meting = True
datum_previous = datetime.datetime.now()
log_list = []

# url_json = "http://deskthijs.local/Digizon/Website/IndoorSki.aspx"
url_json = "https://www.digizon.nl/IndoorSki.aspx"


def threaded_request(pulse_json):
    global url_json
    json_dump = json.dumps(pulse_json)
    response = requests.post(url_json, json=json_dump, timeout=0.5)
    # print(response.text)


# def create_textfile(filename):
#     f2 = open(last_meting_folder + filename, 'w')
#     f2.close()


def datum2string(datum):
    return datum.strftime("%Y-%m-%d %H.%M.%S.%f")[:-3]


# Function that "add_event_detect" runs at input change
def pulse_detected(pin, force=False):
    if GPIO.input(pin) == 1 or force:  # input is high
        # Global Vars
        global datum_previous
        global counter
        global counter_totaal
        global filename_data
        global meting_start
        global nieuwe_meting
        global omtrek_rol_m

        # Previous pulse
        diff_in_milli_secs = (datetime.datetime.now() - datum_previous).total_seconds() * 1000
        datum_previous = datetime.datetime.now()

        # Huidige Snelheid meter per seconde
        snelheid = 0
        if diff_in_milli_secs > 10:
            snelheid = (omtrek_rol_m * 1000) / diff_in_milli_secs

        # Afstand
        meting_afstand = omtrek_rol_m * counter
        meting_afstand_totaal = omtrek_rol_m * counter_totaal

        # Gem Snelheid
        gem_snelheid = 0  # meter per seconde
        delta = datetime.datetime.now() - meting_start
        if delta.total_seconds() > 0:
            gem_snelheid = meting_afstand / delta.total_seconds()

        counter += 1
        counter_totaal += 1

        log_list.append(f"{delta}, {datetime.datetime.now()}, {diff_in_milli_secs:0.2f}, {counter_totaal}\n")

        if len(log_list) == 40:
            with open("counterdata_testrun1_24h.txt", "a") as counterfile:
                for line in log_list:
                    counterfile.write(f"{line}")
            log_list.clear()



# On input change, run input_Chng function
GPIO.add_event_detect(7, GPIO.RISING, callback=pulse_detected, bouncetime=10)

# Ready for meting!
print('Ready!')

# seed random number generator
seed(1)

try:
    while True:
        # print('Fake pulsing...')
        # pulse_detected(7, True)
        time.sleep(0.3 + (random() / 20))

except KeyboardInterrupt:  # trap a CTRL+C keyboard interrupt
    GPIO.cleanup()  # resets all GPIO ports used by this program
