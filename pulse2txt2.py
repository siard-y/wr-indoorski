#!/usr/bin/python

from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from threading import Thread
from time import sleep
import RPi.GPIO as GPIO  # import RPi.GPIO module
import decimal
import glob
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
send_lastmeting_httprequest = True

# Vars
counter = 0
counter_totaal = 0
filename_data = ''
meting_start = datetime.datetime.now()
nieuwe_meting = True
datum_previous = datetime.datetime.now()

# url_json = "http://deskthijs.local/Digizon/Website/IndoorSki.aspx"
url_json = "https://www.digizon.nl/IndoorSki.aspx"


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

        # Wanneer geen puls of nieuw uur, dan nieuwe meting
        if (
                (datetime.datetime.now() - datum_previous).total_seconds() > 20 or
                (datetime.datetime.now().hour != meting_start.hour)
        ):
            nieuwe_meting = True

        # Eerste puls, meting start 
        if nieuwe_meting:
            filename_data = '/home/pi/IndoorSki/pulse2txt/' + datum2string(datetime.datetime.now()) + '.txt'
            print('######### NIEUWE METING ########### \nFile: ' + filename_data)
            counter = 0
            datum_previous = datetime.datetime.now()
            meting_start = datetime.datetime.now()
            nieuwe_meting = False

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

        # insert pulse
        pulse = (
            datum2string(meting_start),
            datum2string(datetime.datetime.now()),
            datum2string(datum_previous),
            str(counter),
            str(counter_totaal),
            str(round(diff_in_milli_secs, 2)),
            str(round(snelheid, 2)),
            str(round(meting_afstand, 2)),
            str(round(meting_afstand_totaal, 2)),
            str(round(gem_snelheid, 2))
        )

        # Write 1 line
        f1 = open(filename_data, "a")  # append mode
        f1.write('\t'.join(pulse) + '\n')
        f1.close()

        # Compose Json
        pulse_json = {
            "meting_start": pulse[0],
            "datum": pulse[1],
            "datum_previous": pulse[2],
            "counter": pulse[3],
            "counter_totaal": pulse[4],
            "diff_in_milli_secs": pulse[5],
            "snelheid": pulse[6],
            "meting_afstand": pulse[7],
            "meting_afstand_totaal": pulse[8],
            "gem_snelheid": pulse[9]
        }
        print(json.dumps(pulse_json, indent=4))

        # Display
        counter += 1
        counter_totaal += 1


# On input change, run input_Chng function
GPIO.add_event_detect(7, GPIO.RISING, callback=pulse_detected, bouncetime=100)

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
    with open("counterdata_testrun1_24h.txt", "w") as cntfile:
        cntfile.write(str(f"{counter_totaal}, {counter}, {datum_previous}"))
