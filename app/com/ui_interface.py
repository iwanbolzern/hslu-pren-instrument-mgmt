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
    CMD_BACK_TO_ORIGIN = 8

    def __init__(self):
        self.ui_com = UICommunication()
        self.ui_com.register_callback(self.ui_callback)
        self.callback = defaultdict(list)

        # start ui communication
        self.ui_com.start()

    def send_log(self, log_msg):
        self.ui_com.send_msg('{}{}'.format(self.CMD_LOG, log_msg))

    def send_position_update(self, x_position, z_position):
        self.ui_com.send_msg('{}{},{}'.format(self.CMD_POSITION_FEEDBACK, x_position, z_position))

    def send_end(self):
        self.ui_com.send_msg('{}'.format(self.CMD_END_RUN))

    def send_end_init(self):
        self.ui_com.send_msg('{}'.format(self.CMD_END_INIT))

    def register_init_once(self, callback):
        self.callback[self.CMD_INIT].append(callback)

    def unregister_init_once(self, callback):
        self.callback[self.CMD_INIT].remove(callback)

    def register_back_to_origin_once(self, callback):
        self.callback[self.CMD_BACK_TO_ORIGIN].append(callback)

    def unregister_back_to_origin(self, callback):
        self.callback[self.CMD_BACK_TO_ORIGIN].remove(callback)

    def register_start_once(self, callback):
        self.callback[self.CMD_START].append(callback)

    def unregister_start(self, callback):
        self.callback[self.CMD_START].remove(callback)

    def ui_callback(self, cmd_id: int, payload: List[chr]):
        print('ui_callback called')
        if cmd_id in self.callback:
            for callback in self.callback.pop(cmd_id):
                callback()