from collections import defaultdict
from enum import Enum
from threading import Event
from typing import List

from com.ic_communication import ICCommunication

class Direction(Enum):
    Forward = chr(0)
    Backward = chr(1)

class ICInterface:

    # IM to IC ids
    CMD_INIT_TELE = 1
    CMD_DRIVE_DISTANCE = 2
    CMD_DRIVE_JOG = 3
    CMD_DRIVE_TO_END = 4
    CMD_MOVE_TELE = 5
    CMD_ENABLE_MAGNET = 6
    CMD_DISABLE_MAGNET = 7

    # IC to IM ids
    CMD_END_INIT_TELE = 8
    CMD_END_DRIVE = 9
    CMD_EMD_MOVE_TELE = 10
    CMD_POSITION_FEEDBACK = 11

    def __init__(self):
        self.ic_com = ICCommunication()
        self.ic_com.register_callback(self.ic_callback)
        self.callback_queue = defaultdict(list)

    # send Commands
    def init_tele(self, timeout: float=None):
        self.ic_com.send_msg(self.CMD_INIT_TELE)
        self._wait_for_ic_callback(self.CMD_END_INIT_TELE, timeout)

    def init_tele_async(self, callback, timeout: float=None):
        raise NotImplementedError()

    def drive_distance_async(self, distance: int, speed: chr,
                             direction: Direction, callback):
        payload = distance.to_bytes(2, byteorder='big')
        payload.append(speed)
        payload.append(direction.value)

        self.ic_com.send_msg(self.CMD_DRIVE_DISTANCE)
        self.callback_queue[self.CMD_DRIVE_DISTANCE]\
            .append(callback)



    def _wait_for_ic_callback(self, cmd_id: int, timeout: float):
        thread_event = Event()
        self.callback_queue[cmd_id].append(lambda: thread_event.set())
        timeout = not thread_event.wait(timeout)
        if timeout:
            raise Exception('Not received callback within timeout: CMD_ID {}, timeout {}'.format(cmd_id, timeout))

    def ic_callback(self, cmd_id: int, payload: List[chr]):
        if cmd_id in self.callback_queue:
            for callback in self.callback_queue.pop(cmd_id):
                callback()





