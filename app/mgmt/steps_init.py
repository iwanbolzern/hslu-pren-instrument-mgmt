from threading import Event

from mgmt.steps_base import Step, Context
from mgmt_utils import log

from com.ic_interface import Direction


class BackToOriginStep(Step):

    def __init__(self, context: Context):
        super(BackToOriginStep, self).__init__(context)

    def run(self):
        log.debug('WaitForBackToOriginStep started')
        self.event = Event()
        self.context.ui_interface.register_back_to_origin_once(self.event.set)
        log.info('Waiting for BackToOriginStep callback')
        self.event.wait()
        if not self.is_canceled:
            log.info('BackToOriginStep callback received')
            self.context.ic_interface.drive_jog(50, Direction.Backward)

    def cancel(self):
        super(BackToOriginStep, self).cancel()
        self.context.ui_interface.unregister_back_to_origin(self.event.set)
        self.event.set()


class WaitForInitStep(Step):

    def __init__(self, context: Context):
        super(WaitForInitStep, self).__init__(context)

    def run(self):
        log.debug('WaitForInitStep started')
        self.event = Event()
        self.context.ui_interface.register_init_once(self.set_event)
        log.info('Waiting for init callback')
        self.event.wait()
        if not self.is_canceled:
            log.info('Init callback received')

    def set_event(self):
        self.event.set()

    def cancel(self):
        super(WaitForInitStep, self).cancel()
        self.context.ui_interface.unregister_init_once(self.set_event)
        self.event.set()


class InitStep(Step):

    def __init__(self, context: Context):
        super(InitStep, self).__init__(context)

    def run(self):
        log.debug('Init Tele started')
        self.context.ic_interface.init_tele()
        self.context.ui_interface.send_end_init()
        self.context.reset_position()
        log.debug('Init Tele end')
