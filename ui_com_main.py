import time

from com.ui_communication import UICommunication

ui_com = UICommunication()
ui_com.start()

while True:
    ui_com.send_position(5, 5)
    ui_com.send_log("Das ist eine test log message")
    time.sleep(2)