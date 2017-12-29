from threading import Event
from typing import List

from com.ic_communication import ICCommunication


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
        self.wait_queue = {}

    # send Commands
    def init_tele(self, timeout: float=None):
        self.ic_com.send_msg(self.CMD_INIT_TELE)
        self._wait_for_ic_callback(self.CMD_END_INIT_TELE, timeout)

    def init_tele_async(self, callback, timeout: float=None):
        raise NotImplementedError()

    def drive_distance(self, ):


    def _wait_for_ic_callback(self, cmd_id: int, timeout: float):
        self.wait_queue[cmd_id] = Event()
        timeout = not self.wait_queue[cmd_id].wait(timeout)
        if timeout:
            raise Exception('Not received callback within timeout: CMD_ID {}, timeout {}'.format(cmd_id, timeout))

    def ic_callback(self, cmd_id: int, payload: List[chr]):
        if cmd_id in self.wait_queue:
            self.wait_queue.pop(cmd_id).set()





