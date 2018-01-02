from threading import Event

from mgmt.steps_base import Step, Context
from utils import log


class WaitForInitStep(Step):

    def __init__(self, context: Context):
        super(WaitForInitStep, self).__init__(context)

    def run(self):
        log.debug('WaitForInitStep started')
        event = Event()
        self.context.ui_interface.register_init_once(lambda: event.set())
        log.info('Waiting for init callback')
        event.wait()
        log.info('Init callback received')


class InitStep(Step):

    def __init__(self, context: Context):
        super(InitStep, self).__init__(context)

    def run(self):
        log.debug('Init Tele started')
        self.context.ic_interface.init_tele()
        log.debug('Init Tele end')