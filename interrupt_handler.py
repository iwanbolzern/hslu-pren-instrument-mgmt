import RPi.GPIO as GPIO
from datetime import datetime, timedelta
import time

PIN = 2

GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN, GPIO.IN)

time = datetime.now()
count = 0


def countUp(channel):
    global count
    count += 1


GPIO.add_event_detect(PIN, GPIO.RISING, callback=countUp)


while True:
    print("Count: {}, Span: {}", count, datetime.now() - time)
    time = datetime.now()
    count = 0
    time.sleep(1)
