from collections import defaultdict



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
        self.callback = defaultdict(list)

    def register_init_once(self, callback):
        self.callback[self.CMD_INIT].append(callback)