import sys
sys.path.insert(0, '/home/pi/instrument-mgmt/app/target_recognition')
sys.path.insert(5, '/home/pi/.local/lib/python3.5/site-packages')

from mgmt.core_process import CoreProcess

core_process = CoreProcess()
core_process.start_process()

while True:
    input()
