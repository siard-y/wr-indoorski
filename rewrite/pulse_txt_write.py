#!/usr/bin/python3
import sqlite3
import RPi.GPIO as GPIO
from datetime import datetime

GPIO.setmode(GPIO.BOARD)
GPIO.setup(7, GPIO.IN)

counter_filename = f"counter_{datetime.now().strftime('%F__%H_%M_%S')}.txt"


class Data:
    counter = 0
    meting_start_time = datetime.now()
    datetime_previouspulse = datetime.now()
    log_list = []

    def increment_counter(self):
        self.counter += 1

    def get_counter(self):
        return self.counter

    def setnewpreviouspulse(self, dtn):
        self.datetime_previouspulse = dtn


data = Data()


def pulse_detected(channel):
    if GPIO.input(channel) > 0.5:  # input is high
        pulse_time_now = datetime.now()
        time_since_start = pulse_time_now - data.meting_start_time
        time_since_last_pulse_ms = (pulse_time_now - data.datetime_previouspulse).total_seconds() * 1000

        data.setnewpreviouspulse(pulse_time_now)  # set new previous (current) pulse
        data.increment_counter()  # counter += 1

        data_string = f"{time_since_start}, {pulse_time_now}, {time_since_last_pulse_ms:0.2f}, {data.get_counter()}\n"

        data.log_list.append(data_string)
        # print(data_string.replace("\n", ""))

        if len(data.log_list) == 40:
            with open(f"{counter_filename}", "a") as counterfile:
                for line in data.log_list:
                    counterfile.write(f"{line}")
            data.log_list.clear()


GPIO.add_event_detect(7, GPIO.RISING, callback=pulse_detected, bouncetime=10)

try:
    while True:
        pass
except KeyboardInterrupt:
    GPIO.cleanup()
