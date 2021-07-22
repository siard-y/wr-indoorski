from guizero import App, Text, PushButton, TextBox
import sqlite3
from sqlite3 import Error

import datetime, atexit, time
import time                        # Get sleep function to delay loop 


def get_last_record():
    conn = sqlite3.connect(r"/home/pi/IndoorSki/indoorski.db")
    cursor = conn.execute("SELECT datum, meting_nr, counter, duration FROM pulse ORDER BY datum DESC LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    print (row[0])
    welcome_message.value = row[0]

app = App(title="World Record Indoor Ski")

update_text = PushButton(app, command=get_last_record, text="Display my name")
welcome_message = Text(app, text="Welcome to my app", size=40, font="Times New Roman", color="lightblue")


app.display()

