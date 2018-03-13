import sys
sys.path.insert(0, '/home/pi/instrument-mgmt/app/target_recognition')

from mgmt.core_process import CoreProcess

core_process = CoreProcess()
core_process.start_process()

while True:
    input()