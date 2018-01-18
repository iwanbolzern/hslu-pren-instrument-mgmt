from threading import Event

from mgmt.steps_base import Step, Context
from utils import log


class WaitForInitStep(Step):

    def __init__(self, context: Context):
        super(WaitForInitStep, self).__init__(context)

    def run(self):
        log.debug('WaitForInitStep started')
        self.event = Event()
        self.context.ui_interface.register_init_once(lambda: self.event.set())
        log.info('Waiting for init callback')
        self.event.wait()
        if not self.is_canceled:
            log.info('Init callback received')

    def cancel(self):
        super(WaitForInitStep, self).cancel()
        self.event.set()


class InitStep(Step):

    def __init__(self, context: Context):
        super(InitStep, self).__init__(context)

    def run(self):
        log.debug('Init Tele started')
        self.context.ic_interface.init_tele()
        self.context.ui_interface.send_end_init()
        log.debug('Init Tele end')
