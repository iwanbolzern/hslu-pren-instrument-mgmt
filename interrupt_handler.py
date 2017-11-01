import RPi.GPIO as GPIO
from datetime import datetime, timedelta

PIN = 2

GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN, GPIO.IN)

time = datetime.now()
count = 0
while True:
    GPIO.wait_for_edge(PIN, GPIO.RISING)
    count += 1

    if datetime.now() - time > timedelta(seconds=1):
        print("Count: {}, Span: {}", count, datetime.now() - time)
        time = datetime.now()
        count = 0
