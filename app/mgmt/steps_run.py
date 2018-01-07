from threading import Event

from com.ic_interface import Direction, MagnetDirection
from mgmt.steps_base import Step, Context
from utils import log


class WaitForStartStep(Step):

    def __init__(self, context: Context):
        super(WaitForStartStep, self).__init__(context)
        self.event = None

    def run(self):
        log.debug('WaitForStartStep started')
        self.event = Event()
        self.context.ui_interface.register_start_once(lambda: self.event.set())
        log.info('Waiting for start callback')
        self.event.wait()
        if not self.is_canceled:
            log.info('Start callback received')

    def cancel(self):
        super(WaitForStartStep, self).cancel()
        self.event.set()


class UpdatePositionStep(Step):

    def __init__(self, context: Context):
        super(UpdatePositionStep, self).__init__(context)
        self.event = None

    def run(self):
        log.debug('UpdatePositionStep started')
        self.context.ic_interface.register_position_callback(self._position_update_received)

        #prevent step from end
        self.event = Event()
        self.event.wait()

    def _position_update_received(self, x_position, z_position):
        if self.context.load_present:
            self.context.ui_interface.send_position_update(x_position, z_position)

    def cancel(self):
        super(UpdatePositionStep, self).cancel()
        self.event.set()


class DriveXToLoadPickup(Step):

    def __init__(self, context: Context):
        super(DriveXToLoadPickup, self).__init__(context)
        self.event = None

    def run(self):
        self.event = Event()
        self.context.ic_interface.drive_distance_async(600, 100, Direction.Forward,
                                                       lambda: self.event.set())
        self.event.wait()


class DriveZToLoadPickup(Step):

    def __init__(self, context: Context):
        super(DriveZToLoadPickup, self).__init__(context)
        self.event = None

    def run(self):
        #wait to start of move tele
        self.event = Event()
        self.context.ic_interface.register_position_callback(self._position_update_received)
        self.event.wait()

        #drive tele
        self.event = Event()
        self.context.ic_interface.move_tele_async(50, Direction.Forward,
                                                  lambda: self.event.set())
        self.event.wait()

    def _position_update_received(self, x_position, z_position):
        if x_position >= 500:
            self.context.ic_interface.unregister_position_callback(self._position_update_received)
            self.event.set()


class EnableMagnetStep(Step):

    def __init__(self, context: Context):
        super(EnableMagnetStep, self).__init__(context)
        self.event = None

    def run(self):
        # wait to start of move tele
        self.event = Event()
        self.context.ic_interface.register_position_callback(self._position_update_received)
        self.event.wait()

        #enable magnet
        self.context.ic_interface.enable_magnet(MagnetDirection.Enforce)

    def _position_update_received(self, x_position, z_position):
        if x_position >= 500 and z_position >= 200:
            self.context.ic_interface.unregister_position_callback(self._position_update_received)
            self.event.set()


class DriveZToTravelPosition(Step):

    def __init__(self, context: Context):
        super(DriveZToTravelPosition, self).__init__(context)
        self.event = None

    def run(self):
        #drive tele
        self.event = Event()
        self.context.ic_interface.move_tele_async(50, Direction.Backward,
                                                  lambda: self.event.set())
        self.event.wait()

class DriveToUnloadPlain(Step):

    def __init__(self, context: Context):
        super(DriveToUnloadPlain, self).__init__(context)
        self.event = None

    def run(self):
        #wait to start of move tele
        self.event = Event()
        self.context.ic_interface.register_position_callback(self._position_update_received)
        self.event.wait()

        #drive tele
        self.context.ic_interface.drive_jog

    def _position_update_received(self, x_position, z_position):
        if x_position >= 500:
            self.context.ic_interface.unregister_position_callback(self._position_update_received)
            self.event.set()

class DriveZToUnloadPosition(Step):

    def __init__(self, context: Context):
        super(DriveZToUnloadPosition, self).__init__(context)
        self.event = None

    def run(self):
        #wait to start of move tele
        self.event = Event()
        self.context.ic_interface.register_position_callback(self._position_update_received)
        self.event.wait()

        #drive tele
        self.event = Event()
        self.context.ic_interface.move_tele_async(50, Direction.Forward,
                                                  lambda: self.event.set())
        self.event.wait()

    def _position_update_received(self, x_position, z_position):
        if x_position >= 500:
            self.context.ic_interface.unregister_position_callback(self._position_update_received)
            self.event.set()