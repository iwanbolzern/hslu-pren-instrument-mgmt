from collections import defaultdict
from typing import List

from com.ui_communication import UICommunication


class UIInterface:

    #SC to IM
    CMD_CONFIGURE = 0
    CMD_INIT = 1
    CMD_START = 2

    #IM to SC
    CMD_END_INIT = 3
    CMD_POSITION_FEEDBACK = 4
    CMD_END_RUN = 5
    CMD_LOG = 6

    def __init__(self):
        self.ui_com = UICommunication()
        self.ui_com.register_callback(self.ui_callback)
        self.callback = defaultdict(list)

        # start ui communication
        self.ui_com.start()

    def register_init_once(self, callback):
        self.callback[self.CMD_INIT].append(callback)

    def register_start_once(self, callback):
        self.callback[self.CMD_START].append(callback)

    def ui_callback(self, cmd_id: int, payload: List[chr]):
        if cmd_id in self.callback:
            for callback in self.callback.pop(cmd_id):
                callback()